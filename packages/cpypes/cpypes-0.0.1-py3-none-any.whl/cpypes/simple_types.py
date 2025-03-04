import struct

from . import cpype


STRUCT_SIGNED_INT_FORMATS = {1: "b", 2: "h", 4: "i", 8: "q"}

# Libffi defines:
# * char, short, int, long (signed and unsigned)
# * int8, int16, int32, int64 (signed and unsigned)
# * float, double, longdouble (real and complex)
# * generic pointer
# * void

CP_TYPE_SCHAR =      struct.pack("!B", 0)
CP_TYPE_UCHAR =      struct.pack("!B", 1)
CP_TYPE_SSHORT =     struct.pack("!B", 2)
CP_TYPE_USHORT =     struct.pack("!B", 3)
CP_TYPE_SINT =       struct.pack("!B", 4)
CP_TYPE_UINT =       struct.pack("!B", 5)
CP_TYPE_SLONG =      struct.pack("!B", 6)
CP_TYPE_ULONG =      struct.pack("!B", 7)
CP_TYPE_SINT8 =      struct.pack("!B", 8)
CP_TYPE_UINT8 =      struct.pack("!B", 9)
CP_TYPE_SINT16 =     struct.pack("!B", 10)
CP_TYPE_UINT16 =     struct.pack("!B", 11)
CP_TYPE_SINT32 =     struct.pack("!B", 12)
CP_TYPE_UINT32 =     struct.pack("!B", 13)
CP_TYPE_SINT64 =     struct.pack("!B", 14)
CP_TYPE_UINT64 =     struct.pack("!B", 15)
CP_TYPE_VOID_P =     struct.pack("!B", 16)
CP_TYPE_FLOAT =      struct.pack("!B", 17)
CP_TYPE_DOUBLE =     struct.pack("!B", 18)
CP_TYPE_LONGDOUBLE = struct.pack("!B", 19)
CP_TYPE_STRUCT =     struct.pack("!B", 27)

class _PyCType(type):
    def __mul__(self, value):
        from . import carray
        return carray.ARRAY(self, value)


class _CData(metaclass=_PyCType):
    @classmethod
    def from_address(cls, addr, needs_free=False):
        rtn = cls.__new__(cls)
        rtn._ptr_ = addr
        rtn._b_needsfree_ = needs_free
        return rtn

    def __new__(cls, *args, **kwargs):
        cls._layout_()
        return super().__new__(cls)

    @classmethod
    def _size_(cls):
        cls._layout_()
        return cls.__size__

    def __del__(self):
        if self._b_needsfree_:
            cpype.free(self._ptr_)


class SimpleValue:
    """ Descriptor to handle `value` attribute """
    def __get__(self, instance, objtype=None):
        return cpype.read(instance._ptr_, type(instance))

    def __set__(self, instance, value):
        cpype.write(instance._ptr_, type(instance), data)


class _SimpleCData(_CData):
    value = SimpleValue()

    @classmethod
    def _byte_rep_(cls):
        return cls.__byte_rep__

    @classmethod
    def _layout_(cls):
        if hasattr(cls, "__size__"):
            return
        cls.__size__ = cpype.size(cls)

    @classmethod
    def _decode_(cls, data):
        """ Decode binary data into a Python object """
        cls._layout_()
        return struct.unpack("!" + cls._type_, data)[0]

    @classmethod
    def _encode_(cls, value):
        """ Encode a Python object into binary data """
        cls._layout_()
        return struct.pack("!" + cls._type_, value)

    def _assign_(self, value):
        cpype.write(self._ptr_, type(self), value)

    def __init__(self, value):
        self._ptr_ = cpype.alloc(self.__size__)
        cpype.write(self._ptr_, type(self), value)
        self._b_needsfree_ = True


class _CInteger(_SimpleCData):
    @classmethod
    def _layout_(cls):
        # We need the check here so we don't bother with `_type_` if
        # we've already assigned it.
        if hasattr(cls, "__size__"):
            return
        super()._layout_()
        t = STRUCT_SIGNED_INT_FORMATS[cls.__size__]
        if issubclass(cls, _CUnsignedInteger):
            t = t.upper()
        cls._type_ = t

class _CSignedInteger(_CInteger):
    pass

class _CUnsignedInteger(_CInteger):
    pass

class c_bool(_SimpleCData):
    # This matches the size for ctypes`.
    __byte_rep__ = CP_TYPE_UINT8

class c_byte(_CSignedInteger):
    __byte_rep__ = CP_TYPE_SCHAR
class c_ubyte(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_UCHAR

class c_short(_CSignedInteger):
    __byte_rep__ = CP_TYPE_SSHORT
class c_ushort(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_USHORT
class c_int(_CSignedInteger):
    __byte_rep__ = CP_TYPE_SINT
class c_uint(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_UINT
class c_long(_CSignedInteger):
    __byte_rep__ = CP_TYPE_SLONG
class c_ulong(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_ULONG
class c_longlong(_CSignedInteger):
    # TODO: Is this right?
    __byte_rep__ = CP_TYPE_SINT64
class c_ulonglong(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_UINT64

class c_int8(_CSignedInteger):
    __byte_rep__ = CP_TYPE_SINT8
class c_uint8(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_UINT8
class c_int16(_CSignedInteger):
    __byte_rep__ = CP_TYPE_SINT16
class c_uint16(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_UINT16
class c_int32(_CSignedInteger):
    __byte_rep__ = CP_TYPE_SINT32
class c_uint32(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_UINT32
class c_int64(_CSignedInteger):
    __byte_rep__ = CP_TYPE_SINT64
class c_uint64(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_UINT64

class c_size_t(_CSignedInteger):
    __byte_rep__ = CP_TYPE_VOID_P
class c_ssize_t(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_VOID_P

class _CChar(_SimpleCData):
    pass

class c_char(_CChar):
    __byte_rep__ = CP_TYPE_UCHAR

    @classmethod
    def _encode_(cls, value):
        # `value` can be an int or a single-length bytes object.
        if isinstance(value, bytes):
            assert len(value) == 1
            return value
        return chr(value).encode()

    @classmethod
    def _decode_(cls, data):
        assert len(data) == 1
        return data

class CCharPValue:
    """ Descriptor to handle `c_char_p` `value` attribute """
    def __get__(self, instance, objtype=None):
        # Consider optimizing this by adding a special `cpype` call
        # for reading a null-terminated array.
        char_array = []
        array_address = c_void_p.from_address(instance._ptr_).value
        i = 0
        while True:
            c = cpype.read(array_address + i, c_char)
            print(c)
            if c == b"\x00":
                break
            char_array.append(c)
            i += 1
            if i > 100:
                raise ValueError("Overflew")
        return b"".join(char_array)

    def __set__(self, instance, value):
        from . import carray
        array_cls = carray.ARRAY(c_char, len(value) + 1)
        array = array_cls(*value, 0)
        instance._objects = [array]
        cpype.write(instance._ptr_, type(instance), array._ptr_)

class c_char_p(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_VOID_P
    value = CCharPValue()

    def __init__(self, value):
        # First, create a char array to hold the bytes.
        from . import carray
        array_cls = carray.ARRAY(c_char, len(value) + 1)
        array = array_cls(*value, 0)
        super().__init__(array._ptr_)
        self._objects = [array]

class c_wchar(_CChar):
    pass

class c_wchar_p(_SimpleCData):
    __byte_rep__ = CP_TYPE_VOID_P

class c_void_p(_CUnsignedInteger):
    __byte_rep__ = CP_TYPE_VOID_P

# Floating-point types.
class _CFloat(_SimpleCData):
    pass
class c_float(_CFloat):
    pass
class c_double(_CFloat):
    pass
class c_longdouble(_CFloat):
    pass

def issimple(cls):
    # TODO: Return False for userdefined subclasses.
    return issubclass(cls, _SimpleCData)
