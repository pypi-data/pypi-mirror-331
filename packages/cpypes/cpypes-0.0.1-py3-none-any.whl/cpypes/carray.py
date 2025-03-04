from . import cpype
from . import simple_types

class Array(simple_types._CData):
    # We pass class dict when calling `type`.
    @classmethod
    def _byte_rep_(cls):
        # TODO
        pass

    # We have to define this method, but we don't need to do anything
    # since we already know the layout from the size of the array type.
    @classmethod
    def _layout_(cls):
        pass

    def _get_item_addr(self, index):
        if index < 0 or index >= self._length_:
            msg = f"Index ({index}) out of range "
            msg += f"(length {self._length_})"
        return self._ptr_ + index*self._type_._size_()

    def __getitem__(self, index):
        addr = self._get_item_addr(index)
        obj = self._type_.from_address(addr)
        if simple_types.issimple(self._type_):
            return obj.value
        else:
            return obj

    def __setitem__(self, index, value):
        addr = self._get_item_addr(index)
        self._type_.from_address(addr)._assign_(value)

    def __init__(self, *values):
        cls = type(self)
        self._ptr_ = cpype.alloc(cls._size_())
        self._b_needsfree_ = True
        # Initialize.
        for i, value in enumerate(values):
            self[i] = value


class CharArrayValue:
    """ Descriptor to handle `c_char` array `value` attribute """
    def __get__(self, instance, objtype=None):
        byte_values = []
        for i in range(type(instance)._length_):
            value = cpype.read(instance._ptr_ + i, instance._type_)
            if value == b"\x00":
                break
            byte_values.append(value)
        return b"".join(byte_values)

    def __set__(self, instance, value):
        if len(value) >= type(instance)._length_:
            raise ValueError("byte string too long")
        for i in range(len(value)):
            cpypes.write(instance._ptr_ + i, instance._type_, value[i])

def ARRAY(ctype, length):
    cls_name = f"{ctype.__name__}_Array_{length}"
    cls_dict = dict(_type_=ctype, _length_=length,
                    __size__=length*ctype._size_())
    if ctype is simple_types.c_char:
        cls_dict["value"] = CharArrayValue()
    return type(cls_name, (Array,), cls_dict)
