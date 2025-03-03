import copy
import math
from time import sleep
from typing import Generator

import libusb_package
import usb.core
from pydfuutil import dfu
from pydfuutil.dfu import StatusRetVal
from pydfuutil.usb_dfu import FuncDescriptor
from rich import progress
from rich.progress import Progress, Task
from usb.backend import libusb1


class DfuProgress(Progress):

    def __init__(self, *args, callback=None, **kwargs):
        super(DfuProgress, self).__init__(*args, **kwargs)
        self.callback = callback
        self.started = False

    def update(self, task_id, prevent_recursion=False, *args, **kwargs) -> None:
        super(DfuProgress, self).update(task_id, *args, **kwargs)
        task: Task = self._tasks[task_id]

        if 'callback' in task.fields and not prevent_recursion:
            if callable(task.fields['callback']):
                task.fields['callback'](task)

    def start(self) -> None:
        """Start the progress display."""

        self.started = True
        super(DfuProgress, self).start()

    def stop(self) -> None:
        """Stop the progress display."""
        self.started = False
        super(DfuProgress, self).stop()


DFU_PROGRESS = DfuProgress(
    progress.TextColumn("[progress.description]{task.description}"),
    progress.BarColumn(10),
    progress.TaskProgressColumn(),
    progress.TimeRemainingColumn(),
    progress.DownloadColumn(),
    progress.TransferSpeedColumn(),
)

task_desc_fmt = '[{color}]{port} {desc}'

libusb1.get_backend(libusb_package.find_library)


def dfu_progress(func):
    def wrapper(*args, **kwargs):
        DFU_PROGRESS.start()
        try:
            ret = func(*args, **kwargs)

        finally:
            DFU_PROGRESS.stop()
            for task in DFU_PROGRESS.tasks:
                DFU_PROGRESS.remove_task(task.id)
        return ret

    return wrapper


def find(find_all=False, backend=None, custom_match=None, **args):
    dev = usb.core.find(find_all, backend, custom_match, **args)

    def device_iter():
        for d in dev:
            d: DfuDevice = copy.copy(d)
            d.__class__ = DfuDevice
            d.dfu_init()

            yield d

    if dev is None:
        return dev
    elif isinstance(dev, usb.core.Device):
        dev: DfuDevice = copy.copy(dev)
        dev.__class__ = DfuDevice
        dev.dfu_init()
        return dev
    elif isinstance(dev, Generator):
        return device_iter()


class DfuDevice(usb.core.Device):

    def __init__(self, dev, backend, dfu_timeout=None, num_connect_attempts=5):
        super(DfuDevice, self).__init__(dev, backend)
        self.dfu_init(dfu_timeout, num_connect_attempts)

    def dfu_init(self, dfu_timeout=None, num_connect_attempts=5):
        self.dfu_interface: usb.core.Interface | None = None
        self.dfu_descriptor: dict | None = None

        self.num_connect_attempts = num_connect_attempts

        dfu.init(dfu_timeout if dfu_timeout else 5000)
        # dfu.dfu_debug(logging.INFO)

    @property
    def dfu_intf(self) -> [int, None]:
        if self.dfu_interface is not None:
            return self.dfu_interface.bInterfaceNumber
        self.get_dfu_interface()
        return self.dfu_interface.bInterfaceNumber

    def get_dfu_descriptor(self, interface: usb.core.Interface):
        try:
            extra = interface.extra_descriptors
            return FuncDescriptor.from_bytes(bytes(extra))
            # return USB_DFU_FUNC_DESCRIPTOR.parse(bytes(extra))
        except Exception as exc:
            raise ConnectionError(
                f'DFU descriptor not found on interface {interface.bInterfaceNumber}: {self._str()}'
            )

    def get_dfu_interface(self):
        cfg: usb.core.Configuration = self.get_active_configuration()
        for intf in cfg.interfaces():
            if intf.bInterfaceClass != 0xfe or intf.bInterfaceSubClass != 1:
                continue

            dfu_desc = self.get_dfu_descriptor(intf)
            if dfu_desc:
                self.dfu_interface = intf
                self.dfu_descriptor = dfu_desc
                break

        if not self.dfu_interface:
            raise ConnectionError(f'No DFU interface found: {self._str()}')

    def get_status(self) -> StatusRetVal:
        status = dfu._get_status(self, self.dfu_intf)
        sleep(status.bwPollTimeout)
        sleep(0.5)
        return status

    def is_connect_valid(self):
        status = self.get_status()
        while status.bState != dfu.State.DFU_IDLE:

            if status.bState in [dfu.State.APP_IDLE, dfu.State.APP_DETACH]:
                return False
            elif status.bState == dfu.State.DFU_ERROR:
                if dfu._clear_status(self, self.dfu_intf) < 0:
                    return False
                status = self.get_status()
            elif status.bState in [dfu.State.DFU_DOWNLOAD_IDLE, dfu.State.DFU_UPLOAD_IDLE]:
                if dfu._abort(self, self.dfu_intf) < 0:
                    return False
                status = self.get_status()
            else:
                break

        if status.bStatus != dfu.Status.OK:
            if dfu._clear_status(self, self.dfu_intf) < 0:
                return False
            status = self.get_status()
            if int(status) < 0:
                return False
            if status.bStatus != dfu.Status.OK:
                return False
            sleep(status.bwPollTimeout)

        return True

    @property
    def usb_port(self):
        port = self.port_numbers
        enc_address = ":".join(f"{num:02X}" for num in port[:6]) + ":00" * (6 - len(port))
        return enc_address

    def dfu_detach(self) -> int:
        detach_timeout = self.dfu_descriptor.wDetachTimeOut / 10000
        detach_timeout = math.ceil(detach_timeout)
        dfu._detach(self, self.dfu_intf, 1000)
        sleep(1)
        return detach_timeout

    def connect(self, hold_port=True):
        if self.num_connect_attempts > 0:
            self.num_connect_attempts -= 1
            self.get_dfu_interface()
            if not self.dfu_interface:
                raise IOError(f'No DFU interface found: {self._str()}')

            if not self.is_connect_valid():
                detach_timeout = self.dfu_detach()
                self.reconnect(detach_timeout, hold_port)
        else:
            raise ConnectionError(f"Can't connect device: {self._str()}")

    def reconnect(self, count: int = 10, hold_port: bool = True, callback=None, task=None):

        def reattach_device_handle() -> DfuDevice | None:
            if not hold_port:
                return find(idVendor=self.idVendor, idProduct=self.idProduct)

            devices = find(find_all=True, idVendor=self.idVendor, idProduct=self.idProduct)
            detached = tuple(filter(lambda d: d if d.port_numbers == self.port_numbers else None, devices))
            if len(detached) != 1:
                return None

            return detached[0]

        countdown = count
        # dev_handle = None

        # FIXME: Local variable 'wait_task' might be referenced before assignment :236
        if isinstance(task, Task):
            wait_task_desc = task
        else:
            wait_task_desc = 'Waiting for device'
            wait_task = DFU_PROGRESS.add_task(
                task_desc_fmt.format(color='magenta1', port=self.usb_port, desc=wait_task_desc),
                total=None, callback=callback
            )

        while countdown > 0:
            dev_handle: DfuDevice = reattach_device_handle()
            if dev_handle is not None:
                break
            countdown -= 1
            sleep(1)
            wait_task_desc += '.'
            DFU_PROGRESS.update(
                wait_task,
                description=task_desc_fmt.format(color='magenta1', port=self.usb_port, desc=wait_task_desc)
            )

        if dev_handle is None:
            DFU_PROGRESS.update(
                wait_task,
                description=task_desc_fmt.format(color='red', port=self.usb_port, desc="Can't reconnect device"),
            )
            raise ConnectionResetError(f"Can't reconnect device: {self._str()}")

        DFU_PROGRESS.update(
            wait_task,
            description=task_desc_fmt.format(color='green', port=self.usb_port, desc="Device connected!"),
            completed=0, total=0
        )

        self.__dict__.update(dev_handle.__dict__)
        self.connect()

    def disconnect(self):
        usb.util.release_interface(self, self.dfu_intf)
        self.free()

    def free(self):
        usb.util.dispose_resources(self)

    def do_upload(self, offset: int, length: int, page_size: int = 2048, callback=None, task=None):
        USB_PAGE = page_size

        total: int = length
        start_page: int = math.ceil(offset / USB_PAGE)
        page = start_page
        ret = bytes()

        if isinstance(task, Task):
            upload_task = task
        else:
            upload_task = DFU_PROGRESS.add_task(
                task_desc_fmt.format(color='magenta1', port=self.usb_port, desc='Uploading...'),
                total=total, callback=callback
            )

        while True:

            rc = dfu._upload(self, self.dfu_intf, page, USB_PAGE),
            page += 1

            if len(rc[0]) < 0:
                ret = rc
                break

            DFU_PROGRESS.update(
                upload_task, advance=USB_PAGE,
                description=task_desc_fmt.format(
                    color='magenta1',
                    port=self.usb_port,
                    desc='Uploading...'
                )
            )

            ret += rc[0]

            if len(rc[0]) < USB_PAGE or (len(ret) >= total >= 0):
                break

        dfu._upload(self, self.dfu_intf, page, 0),

        DFU_PROGRESS.update(
            upload_task, advance=0,
            description=task_desc_fmt.format(
                color='green', port=self.usb_port, desc='Uploading OK!'
            )
        )

        return ret

    def do_download(self, offset: int, data: bytes, page_size: int = 2048, callback=None, task=None):

        total: int = len(data)
        start_page: int = math.ceil(offset / page_size)
        page = start_page
        ret = 0

        if isinstance(task, Task):
            download_task = task
        else:
            download_task = DFU_PROGRESS.add_task(
                task_desc_fmt.format(color='magenta1', port=self.usb_port, desc='Downloading...'),
                total=total, callback=callback
            )

        part_num = 0

        while True:

            part = data[part_num * page_size:part_num * page_size + page_size]
            rc = dfu._download(self, self.dfu_intf, page, part)

            while True:
                status = dfu._get_status(self, self.dfu_intf)

                if int(status) < 0:
                    return part_num * page_size + page_size

                if status.bState in (dfu.State.DFU_DOWNLOAD_IDLE, dfu.State.DFU_ERROR):
                    break

            if status.bStatus != dfu.Status.OK:
                raise IOError(dfu._state_to_string(status.bState))

            page += 1
            part_num += 1

            if rc < 0:
                ret = rc
                break

            DFU_PROGRESS.update(
                download_task, advance=page_size,
                description=task_desc_fmt.format(
                    color='magenta1',
                    port=self.usb_port,
                    desc='Downloading...',
                )
            )

            ret += rc

            if rc < page_size or ret >= total >= 0:
                break

        dfu._download(self, self.dfu_intf, page, 0),

        DFU_PROGRESS.update(
            download_task, advance=0,
            description=task_desc_fmt.format(
                color='deep_sky_blue1', port=self.usb_port, desc='Downloading OK!'
            )
        )

        return ret
