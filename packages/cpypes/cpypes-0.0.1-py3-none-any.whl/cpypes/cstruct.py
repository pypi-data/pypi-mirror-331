import struct

from . import cpype
from . import simple_types

class Structure(simple_types._CData):
    @classmethod
    def _byte_rep_(cls):
        rtn = simple_types.CP_TYPE_STRUCT
        rtn += struct.pack("!I", len(cls._fields_))
        for _, ftype in cls._fields_:
            rtn += ftype._byte_rep_()
        return rtn

    def _assign_(self, value):
        # TODO: Type check.
        for fname, _ in self._fields_:
            setattr(self, fname, getattr(value, fname))

    def __init__(self, **kwargs):
        cls = type(self)
        # Allocate.
        self._ptr_ = cpype.alloc(cls._size_())
        self._b_needsfree_ = True
        # Initialize.
        for name, value in kwargs.items():
            setattr(self, name, value)

    @classmethod
    def _layout_(cls):
        """ Sets the class size and creates field descriptors.

        Returns immediately if the class has already been layed out. """
        if hasattr(cls, "__size__"):
            return
        cls.__size__ = cpype.size(cls)
        offsets = cpype.offsets(cls)
        for (fname, ftype), offset in zip(cls._fields_, offsets):
            setattr(cls, fname, Field(fname, ftype, offset))

class Field:
    def __init__(self, name, ftype, offset):
        self.name = name
        self.ftype = ftype
        self.offset = offset

    def __get__(self, instance, objtype=None):
        print(f"[ ] Getting field {self.name}")
        addr = instance._ptr_ + self.offset
        field = self.ftype.from_address(addr)
        if simple_types.issimple(self.ftype):
            return field.value
        else:
            return field

    def __set__(self, instance, value):
        print(f"[ ] Setting field {self.name} to {value}")
        addr = instance._ptr_ + self.offset
        self.ftype.from_address(addr)._assign_(value)
