"""Comprehensive compatibility layer for pymodbus missing functions."""

import logging

_LOGGER = logging.getLogger(__name__)

def make_byte_string(data):
    """Compatibility function for make_byte_string."""
    if isinstance(data, str):
        return data.encode('utf-8')
    elif isinstance(data, bytes):
        return data
    elif isinstance(data, (list, tuple)):
        return bytes(data)
    else:
        return str(data).encode('utf-8')

def pack_bitstring(data):
    """Compatibility function for pack_bitstring."""
    if isinstance(data, str):
        # Convert string of bits to bytes
        padded = data.ljust((len(data) + 7) // 8 * 8, '0')
        result = []
        for i in range(0, len(padded), 8):
            byte_str = padded[i:i+8]
            result.append(int(byte_str, 2))
        return bytes(result)
    elif isinstance(data, (list, tuple)):
        return bytes(data)
    else:
        return bytes(str(data), 'utf-8')

def unpack_bitstring(data):
    """Compatibility function for unpack_bitstring."""
    if isinstance(data, bytes):
        result = []
        for byte in data:
            result.append(format(byte, '08b'))
        return ''.join(result)
    else:
        return str(data)

# List of functions that might be missing
MISSING_FUNCTIONS = {
    'make_byte_string': make_byte_string,
    'pack_bitstring': pack_bitstring,
    'unpack_bitstring': unpack_bitstring,
}

# Monkey patch pymodbus.utilities BEFORE any other imports
try:
    import pymodbus.utilities
    
    patched_functions = []
    for func_name, func in MISSING_FUNCTIONS.items():
        if not hasattr(pymodbus.utilities, func_name):
            setattr(pymodbus.utilities, func_name, func)
            patched_functions.append(func_name)
    
    if patched_functions:
        _LOGGER.debug("Successfully patched pymodbus.utilities functions: %s", patched_functions)
    else:
        _LOGGER.debug("All required functions already exist in pymodbus.utilities")
        
except ImportError as e:
    _LOGGER.warning("Could not import pymodbus.utilities: %s", e)
except Exception as e:
    _LOGGER.error("Error patching pymodbus.utilities: %s", e)
