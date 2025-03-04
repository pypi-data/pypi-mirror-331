from . import cpype
from . import simple_types


_POINTER_MAP = dict()


class PointerContents:
    """ Descriptor to handle pointer `contents` attribute """
    def __get__(self, instance, objtype=None):
        ptr_value = cpype.read(instance._ptr_, simple_types.c_void_p)
        return instance._type_.from_address(ptr_value)

    def __set__(self, instance, value):
        cpype.write(instance._ptr_, simple_types.c_void_p, value._ptr_)


class _Pointer(simple_types._CData):
    contents = PointerContents()

    @classmethod
    def _byte_rep_(cls):
        return simple_types.c_void_p._byte_rep_()

    @classmethod
    def _layout_(cls):
        cls.__size__ = simple_types.c_void_p._size_()

    def __init__(self, obj):
        self._ptr_ = cpype.alloc(self.__size__)
        cpype.write(self._ptr_, simple_types.c_void_p, obj._ptr_)
        self._b_needsfree_ = True

def POINTER(ctype):
    global _POINTER_MAP
    if ctype in _POINTER_MAP:
        return _POINTER_MAP[ctype]
    cls_name = f"LP_{ctype.__name__}"
    cls_dict = {"_type_": ctype}
    _POINTER_MAP[ctype] = type(cls_name, (_Pointer,), cls_dict)
    return _POINTER_MAP[ctype]

def pointer(obj):
    ptr_cls = POINTER(type(obj))
    # TODO: It would be better to use `addressof`, but that introduces
    # import problems.
    return ptr_cls(obj)
