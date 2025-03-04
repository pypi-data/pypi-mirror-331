""" Inter-process-communication implementation of `ctypes` API """

from . import cpype

from .simple_types import *
from .simple_types import _CData
from .cstruct import Structure
from .carray import Array, ARRAY
from .cpointer import POINTER, pointer

DEFAULT_ABI = 0

class LibraryLoader:
    def __init__(self, dll_type):
        self.dll_type = dll_type

    def LoadLibrary(self, name):
        return self.dll_type(name)

class CDLL:
    def __init__(self, path):
        self.path = path
        self.handle = cpype.load(path)
        self.abi = DEFAULT_ABI

    def __getattr__(self, name):
        func_ptr = cpype.find(self, name)
        return CFunction(func_ptr, self.abi)

class CFunction:
    def __init__(self, pointer, abi):
        self._ptr_ = pointer
        self._abi_ = abi
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        restype = self.restype
        argtypes = self.argtypes
        if restype is None:
            restype = c_int
        if argtypes is None:
            argtypes = [_get_ctype(arg) for arg in args]

        # This is a band-aid to fix issues with array arguments.
        for i in range(len(argtypes)):
            if issubclass(argtypes[i], Array):
                argtypes[i] = POINTER(argtypes[i]._type_)
        args = list(args)
        for i in range(len(args)):
            if isinstance(args[i], Array):
                item_type = args[i]._type_
                first_item = item_type.from_address(args[i]._ptr_)
                args[i] = pointer(first_item)

        rtn = cpype.call(self._ptr_, self._abi_,
            restype, argtypes, args)
        return rtn

cdll = LibraryLoader(CDLL)

def sizeof(x):
    return x._size_()

def addressof(x):
    return x._ptr_

def create_string_buffer(length):
    return (c_char * length)()

def _get_ctype(x):
    if isinstance(x, simple_types._CData):
        return type(x)
    elif isinstance(x, int):
        return c_int
    elif isinstance(x, bytes):
        return c_char_p
    elif isinstance(x, bool):
        return c_bool
    elif isinstance(x, float):
        return c_float
    raise ValueError(f"Cannot determine type of argument: {x}")
