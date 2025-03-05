"""Interface to ZWO ASI Electronic Automatic Focusers (EAFs)."""

import ctypes as c
from ctypes.util import find_library
import logging
import sys
import traceback
import logging

def get_num_focusers():
    """Retrieves the number of ZWO EAFs that are connected. Type :class:`int`."""
    return eaf_zwolib.EAFGetNum()

def _get_focuser_property(id_):
    prop = _EAF_INFO()
    r = eaf_zwolib.EAFGetProperty(id_, prop)
    if r:
        raise zwo_errors[r]
    return prop.get_dict()

def _open_focuser(id_):
    r = eaf_zwolib.EAFOpen(id_)
    if r:
        raise zwo_errors[r]
    return

def _close_focuser(id_):
    r = eaf_zwolib.EAFClose(id_)
    if r:
        raise zwo_errors[r]
    return

def _get_id(id_):
    id2 = c.c_int()
    r = eaf_zwolib.EAFGetID(id_, id2)
    if r:
        raise zwo_errors[r]
    return id2.value()

def _set_id(id_, new_id):
    id2 = _EAF_ID(new_id.encode())
    r = eaf_zwolib.EAFSetID(id_, id2)
    if r:
        raise zwo_errors[r]
    return

def _move_focuser(id_, abs_pos):
    r = eaf_zwolib.EAFMove(id_, abs_pos)
    if r:
        raise zwo_errors[r]
    return

def _stop_focuser(id_):
    # If moving via the handle control, cannot stop
    is_moving_manual = _is_moving(id_)[1]
    if not is_moving_manual:
        r = eaf_zwolib.EAFStop(id_)
        if r:
            raise zwo_errors[r]
    return

def _is_moving(id_):
    is_moving = c.c_bool()
    is_moving_manual = c.c_bool()
    r = eaf_zwolib.EAFIsMoving(id_, is_moving, is_moving_manual)
    if r:
        raise zwo_errors[r]
    return [is_moving.value, is_moving_manual.value]

def _get_temp(id_):
    temp = c.c_float()
    r = eaf_zwolib.EAFGetTemp(id_, temp)
    if r:
        raise zwo_errors[r]
    return temp.value

def _get_position(id_):
    abs_pos = c.c_int()
    r = eaf_zwolib.EAFGetPosition(id_, abs_pos)
    if r:
        raise zwo_errors[r]
    return abs_pos.value

def _reset_position(id_, abs_pos):
    r = eaf_zwolib.EAFResetPostion(id_, abs_pos) # "Position" misspelled in SDK
    if r:
        raise zwo_errors[r]
    return

def _get_beep(id_):
    beep = c.c_bool()
    r = eaf_zwolib.EAFGetBeep(id_, beep)
    if r:
        raise zwo_errors[r]
    return beep.value

def _set_beep(id_, beep):
    r = eaf_zwolib.EAFSetBeep(id_, beep)
    if r:
        raise zwo_errors[r]
    return

def _get_max_step(id_):
    step = c.c_int()
    r = eaf_zwolib.EAFGetMaxStep(id_, step)
    if r:
        raise zwo_errors[r]
    return step.value

def _set_max_step(id_, step):
    r = eaf_zwolib.EAFSetMaxStep(id_, step)
    if r:
        raise zwo_errors[r]
    return

def _get_step_range(id_):
    step_range = c.c_int()
    r = eaf_zwolib.EAFStepRange(id_, step_range)
    if r:
        raise zwo_errors[r]
    return step_range.value

def _get_reverse(id_):
    reverse = c.c_bool()
    r = eaf_zwolib.EAFGetReverse(id_, reverse)
    if r:
        raise zwo_errors[r]
    return reverse.value

def _set_reverse(id_, reverse):
    r = eaf_zwolib.EAFSetReverse(id_, reverse)
    if r:
        raise zwo_errors[r]
    return

def _get_backlash(id_):
    backlash = c.c_int()
    r = eaf_zwolib.EAFGetBacklash(id_, backlash)
    if r:
        raise zwo_errors[r]
    return backlash.value

def _set_backlash(id_, backlash):
    r = eaf_zwolib.EAFSetBacklash(id_, backlash)
    if r:
        raise zwo_errors[r]
    return

def _get_serial_number(id_):
    serial = _EAF_SN()
    r = eaf_zwolib.EAFGetSerialNumber(id_, serial)
    if r:
        raise zwo_errors[r]
    return serial.get_serial_number()

def list_focusers():
    """Retrieves model names of all connected ZWO EAFs. Type :class:`list` of :class:`str`."""
    r = []
    for id_ in range(get_num_focusers()):
        r.append(_get_focuser_property(id_)['Name'])
    return r

class ZWO_Error(Exception):
    """Exception class for errors returned from the :mod:`zwoasi` module."""
    def __init__(self, message):
        Exception.__init__(self, message)


class ZWO_IOError(ZWO_Error):
    """Exception class for all errors returned from the ASI SDK library."""
    def __init__(self, message, error_code=None):
        ZWO_Error.__init__(self, message)
        self.error_code = error_code

class Focuser(object):
    """Representation of ZWO EAF.
    
    The contructor for a focuser object requires the camera ID number or model. The focuser destructor automatically
    closes the focuser."""
    def __init__(self, id_):
        if isinstance(id_, int):
            if id_ >= get_num_focusers() or id_ < 0:
                raise IndexError('Invalid id')
        elif isinstance(id_, str):
            # Find first matching EAF model
            found = False
            for n in range(get_num_focusers()):
                model = _get_focuser_property(n)['Name']
                if model in (id_, 'ZWO ' + id_, 'EAF ' + id_):
                    found = True
                    id_ = n
                    break
            if not found:
                raise ValueError('Could not find focuser model %s' % id_)
        else:
            raise TypeError('Unknown type for id')
        
        self.id = id_
        try:
            _open_focuser(id_)
            self.closed = False
        except Exception:
            self.closed = True
            _close_focuser(id_)
            logger.error('could not open focuser ' + str(id_))
            logger.debug(traceback.format_exc())
            raise

    def __del__(self):
        self.close()

    def close(self):
        """Close the focuser in the EAF library.
        
        The destructor will automatically close the focuser if it has not already been closed."""
        try:
            _close_focuser(self.id)
        finally:
            self.closed = True

    def get_id(self):
        return _get_id(self.id)
    
    def set_id(self, new_id):
        _set_id(self.id, new_id)

    def get_temp(self):
        return _get_temp(self.id)

    def get_position(self):
        return _get_position(self.id)

    def reset_position(self, abs_pos):
        _reset_position(self.id, abs_pos)

    def move_focuser(self, abs_pos):
        _move_focuser(self.id, abs_pos)

    def stop_focuser(self):
        _stop_focuser(self.id)

    def is_moving(self):
        return _is_moving(self.id) # returns [is_moving: bool, is_moving_manual: bool]

    def get_beep(self):
        _get_beep(self.id)

    def set_beep(self, beep):
        _set_beep(self.id, beep)

    def get_max_step(self):
        return _get_max_step(self.id)
    
    def set_max_step(self, step):
        _set_max_step(self.id, step)

    def get_step_range(self):
        return _get_step_range(self.id)

    def get_reverse(self):
        return _get_reverse(self.id)

    def set_reverse(self, reverse):
        _set_reverse(self.id, reverse)

    def get_backlash(self):
        return _get_backlash(self.id)

    def set_backlash(self, backlash):
        _set_backlash(self.id, backlash)

    def get_serial_number(self):
        return _get_serial_number(self.id)

class _EAF_INFO(c.Structure):
    _fields_ = [
        ('ID', c.c_int),
        ('Name', c.c_char * 64),
        ('MaxStep', c.c_int)
    ]

    def get_dict(self):
        r = {}
        for k, _ in self._fields_:
            v = getattr(self, k)
            if sys.version_info[0] >= 3 and isinstance(v, bytes):
                v = v.decode()
            r[k] = v

class _EAF_ID(c.Structure):
    _fields_ = [('id', c.c_char * 8)]

    def get_id(self):
        v =  self.id
        if sys.version_info[0] >= 3 and isinstance(v, bytes):
            v = v.decode()
        return v

class _EAF_SN(c.Structure):
    _fields_ = [('sn', c.c_ubyte * 8)]

    def get_serial_number(self):
        return '{:016x}'.format(int.from_bytes(self.sn, byteorder='big'))

def init(library_file=None):
    global eaf_zwolib

    if eaf_zwolib is not None:
        return # Library already initialized. do nothing
    
    if library_file is None:
        library_file = find_library('EAF_focuser')

    if library_file is None:
        raise ZWO_Error('EAF SDK library not found')
    
    eaf_zwolib = c.cdll.LoadLibrary(library_file)

    eaf_zwolib.EAFGetNum.argtypes = []
    eaf_zwolib.EAFGetNum.restype = c.c_int

    eaf_zwolib.EAFGetID.argtypes = [c.c_int, c.POINTER(c.c_int)]
    eaf_zwolib.EAFGetID.restype = c.c_int

    eaf_zwolib.EAFOpen.argtypes = [c.c_int]
    eaf_zwolib.EAFOpen.restype = c.c_int

    eaf_zwolib.EAFGetProperty.argtypes = [c.c_int, c.POINTER(_EAF_INFO)]
    eaf_zwolib.EAFGetProperty.restype = c.c_int

    eaf_zwolib.EAFMove.argtypes = [c.c_int, c.c_int]
    eaf_zwolib.EAFMove.restype = c.c_int

    eaf_zwolib.EAFStop.argtypes = [c.c_int]
    eaf_zwolib.EAFStop.restype = c.c_int

    eaf_zwolib.EAFIsMoving.argtypes = [c.c_int, 
                                      c.POINTER(c.c_bool), 
                                      c.POINTER(c.c_bool)]
    eaf_zwolib.EAFIsMoving.restype = c.c_int

    eaf_zwolib.EAFGetPosition.argtypes = [c.c_int, c.POINTER(c.c_int)]
    eaf_zwolib.EAFGetPosition.restype = c.c_int

    eaf_zwolib.EAFResetPostion.argtypes = [c.c_int, c.c_int] # "Position" misspelled in SDK
    eaf_zwolib.EAFResetPostion.restype = c.c_int # "Position" misspelled in SDK

    eaf_zwolib.EAFGetTemp.argtypes = [c.c_int, c.POINTER(c.c_float)]
    eaf_zwolib.EAFGetTemp.restype = c.c_int

    eaf_zwolib.EAFSetBeep.argtypes = [c.c_int, c.c_bool]
    eaf_zwolib.EAFSetBeep.restype = c.c_int

    eaf_zwolib.EAFGetBeep.argtypes = [c.c_int, c.POINTER(c.c_bool)]
    eaf_zwolib.EAFGetBeep.restype = c.c_int

    eaf_zwolib.EAFSetMaxStep.argtypes = [c.c_int, c.c_int]
    eaf_zwolib.EAFSetMaxStep.restype = c.c_int

    eaf_zwolib.EAFGetMaxStep.argtypes = [c.c_int, c.POINTER(c.c_int)]
    eaf_zwolib.EAFGetMaxStep.restype = c.c_int

    eaf_zwolib.EAFStepRange.argtypes = [c.c_int, c.POINTER(c.c_int)]
    eaf_zwolib.EAFStepRange.restype = c.c_int

    eaf_zwolib.EAFSetReverse.argtypes = [c.c_int, c.c_bool]
    eaf_zwolib.EAFSetReverse.restype = c.c_int

    eaf_zwolib.EAFGetReverse.argtypes = [c.c_int, c.POINTER(c.c_bool)]
    eaf_zwolib.EAFGetReverse.restype = c.c_int

    eaf_zwolib.EAFSetBacklash.argtypes = [c.c_int, c.c_int]
    eaf_zwolib.EAFSetBacklash.restype = c.c_int

    eaf_zwolib.EAFGetBacklash.argtypes = [c.c_int, c.POINTER(c.c_int)]
    eaf_zwolib.EAFGetBacklash.restype = c.c_int

    eaf_zwolib.EAFClose.argtypes = [c.c_int]
    eaf_zwolib.EAFClose.restype = c.c_int

    eaf_zwolib.EAFGetSerialNumber.argtypes = [c.c_int, c.POINTER(_EAF_SN)]
    eaf_zwolib.EAFGetSerialNumber.restype = c.c_int

    eaf_zwolib.EAFSetID.argtypes = [c.c_int, _EAF_ID]
    eaf_zwolib.EAFSetID.restype = c.c_int

logger = logging.getLogger(__name__)

# Mapping of error numbers to exceptions. Zero is used for success.
zwo_errors = [None,
              ZWO_IOError('Invalid index', 1),
              ZWO_IOError('Invalid ID', 2),
              ZWO_IOError('Invalid value', 3),
              ZWO_IOError('Removed', 4),
              ZWO_IOError('Moving', 5),
              ZWO_IOError('Error State', 6),
              ZWO_IOError('General error', 7),
              ZWO_IOError('Not supported', 8),
              ZWO_IOError('Closed', 9)
              ]

eaf_zwolib = None
try:
    init() # Initialize library on import, will only run once.
except ZWO_Error as e:
    logging.warning(str(e))