from ctypes import windll, byref, Structure, WinError, POINTER, WINFUNCTYPE, c_int
from ctypes.wintypes import BOOL, HMONITOR, HDC, RECT, LPARAM, DWORD, BYTE, WCHAR, HANDLE

_MONITORENUMPROC = WINFUNCTYPE(BOOL, HMONITOR, HDC, POINTER(RECT), LPARAM)

class _PHYSICAL_MONITOR(Structure):
    _fields_ = [('handle', HANDLE),
                ('description', WCHAR * 128)]

# Gamer Mode constants
GAMER_MODE_OFF = 0
GAMER_MODE_FPS = 11
GAMER_MODE_RTS = 12
GAMER_MODE_RACING = 13
GAMER_MODE_GAMER1 = 14
GAMER_MODE_GAMER2 = 15
GAMER_MODE_GAMER3 = 16

# Input Constants
INPUT_SOURCE_DP = 15
INPUT_SOURCE_HDMI = 17

def get_physical_monitors():
    """
    Returns a list of physical monitor handles and their descriptions.
    
    Returns:
        list: A list of tuples containing (handle, description) for each physical monitor
    """
    monitors = []
    
    def callback(hmonitor, hdc, lprect, lparam):
        monitors.append(HMONITOR(hmonitor))
        return True
    
    if not windll.user32.EnumDisplayMonitors(None, None, _MONITORENUMPROC(callback), None):
        raise WinError('EnumDisplayMonitors failed')
    
    result = []
    for monitor in monitors:
        # Get physical monitor count
        count = DWORD()
        if not windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(monitor, byref(count)):
            print(f"Warning: Failed to get number of physical monitors for a display. Skipping.")
            continue
            
        # Get physical monitor handles
        physical_array = (_PHYSICAL_MONITOR * count.value)()
        if not windll.dxva2.GetPhysicalMonitorsFromHMONITOR(monitor, count.value, physical_array):
            print(f"Warning: Failed to get physical monitors for a display. Skipping.")
            continue
            
        for physical in physical_array:
            result.append((physical.handle, physical.description))
    
    return result

def safe_close_monitor(handle):
    """
    Safely close a physical monitor handle.
    
    Args:
        handle: The physical monitor handle to close
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not windll.dxva2.DestroyPhysicalMonitor(handle):
            print(f"Warning: Failed to destroy monitor handle {handle}")
            return False
        return True
    except Exception as e:
        print(f"Error closing monitor handle: {e}")
        return False

def set_vcp_feature(monitor, code, value):
    """
    Sends a DDC command to the specified monitor.
    
    Args:
        monitor: Physical monitor handle
        code: VCP code (see MCCS specification for details)
        value: Value to set for the VCP feature
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not windll.dxva2.SetVCPFeature(HANDLE(monitor), BYTE(code), DWORD(value)):
            error_code = windll.kernel32.GetLastError()
            print(f"Error setting VCP feature: {error_code}")
            return False
        return True
    except Exception as e:
        print(f"Exception setting VCP feature: {e}")
        return False

def get_vcp_feature(monitor, code):
    """
    Gets the current value of a VCP feature from the specified monitor.
    
    Args:
        monitor: Physical monitor handle
        code: VCP code to query
        
    Returns:
        tuple: (current_value, maximum_value) if successful, (None, None) otherwise
    """
    current_value = DWORD()
    maximum_value = DWORD()
    
    try:
        if not windll.dxva2.GetVCPFeatureAndVCPFeatureReply(
            HANDLE(monitor), BYTE(code), None, byref(current_value), byref(maximum_value)):
            error_code = windll.kernel32.GetLastError()
            print(f"Error getting VCP feature: {error_code}")
            return None, None
        return current_value.value, maximum_value.value
    except Exception as e:
        print(f"Exception getting VCP feature: {e}")
        return None, None

def get_input_source(monitor):
    """
    Gets the current input source of the monitor.
    
    Args:
        monitor: Physical monitor handle
        
    Returns:
        int: Current input source code, or None if unable to determine
    """
    current, _ = get_vcp_feature(monitor, 0x60)
    return current

def set_input_source(monitor, source):
    """
    Sets the input source of the monitor.
    
    Args:
        monitor: Physical monitor handle
        source: One of the input source constants (e.g., INPUT_SOURCE_DP, INPUT_SOURCE_HDMI)
        
    Returns:
        bool: True if successful, False otherwise
    """
    return set_vcp_feature(monitor, 0x60, source)

def get_gamer_mode(monitor):
    """
    Gets the current gamer mode from a monitor using VCP code 0xDC.
    
    Args:
        monitor: Physical monitor handle
        
    Returns:
        int: Current gamer mode code, or None if unable to determine
    """
    current, _ = get_vcp_feature(monitor, 0xDC)
    return current

def set_gamer_mode(monitor, mode):
    """
    Sets the gamer mode on a monitor using VCP code 0xDC.
    
    Args:
        monitor: Physical monitor handle
        mode: One of the GAMER_MODE_* constants
              
    Returns:
        bool: True if successful, False otherwise
    """
    return set_vcp_feature(monitor, 0xDC, mode)

