from __future__ import annotations

from contextlib import contextmanager
from ctypes import POINTER, Structure, WINFUNCTYPE, byref, windll
from ctypes.wintypes import BOOL, BYTE, DWORD, HANDLE, HDC, HMONITOR, LPARAM, RECT, WCHAR
from typing import Iterator

_MONITORENUMPROC = WINFUNCTYPE(BOOL, HMONITOR, HDC, POINTER(RECT), LPARAM)
INPUT_SOURCE_CODE = 0x60
GAMER_MODE_CODE = 0xDC
COLOR_PRESET_CODE = 0x14


class _PhysicalMonitor(Structure):
    _fields_ = [("handle", HANDLE), ("description", WCHAR * 128)]


@contextmanager
def physical_monitors() -> Iterator[list[tuple[HANDLE, str]]]:
    displays: list[HMONITOR] = []

    def callback(hmonitor, _hdc, _rect, _data):
        displays.append(HMONITOR(hmonitor))
        return True

    if not windll.user32.EnumDisplayMonitors(None, None, _MONITORENUMPROC(callback), None):
        raise OSError("EnumDisplayMonitors failed")

    result: list[tuple[HANDLE, str]] = []
    try:
        for display in displays:
            count = DWORD()
            if not windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(display, byref(count)):
                continue
            entries = (_PhysicalMonitor * count.value)()
            if not windll.dxva2.GetPhysicalMonitorsFromHMONITOR(display, count.value, entries):
                continue
            result.extend((entry.handle, entry.description) for entry in entries)
        yield result
    finally:
        for handle, _description in result:
            windll.dxva2.DestroyPhysicalMonitor(handle)


def get_vcp_feature(handle: HANDLE, code: int) -> int | None:
    current, maximum = DWORD(), DWORD()
    if not windll.dxva2.GetVCPFeatureAndVCPFeatureReply(handle, BYTE(code), None, byref(current), byref(maximum)):
        return None
    return current.value


def set_vcp_feature(handle: HANDLE, code: int, value: int) -> bool:
    return bool(windll.dxva2.SetVCPFeature(handle, BYTE(code), DWORD(value)))
