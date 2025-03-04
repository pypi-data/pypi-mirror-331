import importlib

import pytest


def make_point(ctypes):
    class Point(ctypes.Structure):
        _fields_ = [("x", ctypes.c_int),
                    ("y", ctypes.c_int),
                    ("z", ctypes.c_int)]
    return Point

def make_line(ctypes, Point):
    class Line(ctypes.Structure):
        _fields_ = [("a", Point), ("b", Point)]
    return Line


@pytest.fixture(params=["ctypes", "cpypes"])
def ctypes(request):
    return importlib.import_module(request.param)


def test_sum(ctypes):
    example = ctypes.cdll.LoadLibrary("./example.so")
    summ = example.sum
    summ.argtypes = [ctypes.c_int, ctypes.c_int]
    summ.restype = ctypes.c_int
    assert summ(23, 42) == 65

def test_taxicab_length_plus_n(ctypes):
    example = ctypes.cdll.LoadLibrary("./example.so")
    tlpn = example.taxicab_length_plus_n
    Point = make_point(ctypes)
    tlpn.argtypes = [ctypes.POINTER(Point), ctypes.c_int]
    tlpn.restype = ctypes.c_int
    p = Point(x=1, y=2, z=0)
    assert isinstance(ctypes.pointer(p), ctypes.POINTER(Point))
    assert tlpn(ctypes.pointer(p), 5) == 8
    assert p.z == 42

def test_slope(ctypes):
    example = ctypes.cdll.LoadLibrary("./example.so")
    slope_and_42 = example.slope_and_set_z_to_42
    Point = make_point(ctypes)
    Line = make_line(ctypes, Point)
    slope_and_42.argtypes = [Line]
    slope_and_42.restype = ctypes.c_int
    a = Point(x=3, y=4, z=0)
    b = Point(x=7, y=12, z=0)
    l = Line(a=a, b=b)
    assert slope_and_42(l) == 2
    # The point here is that `z` is still 0 because we passed
    # the struct by value, not by reference.
    assert l.a.z == 0
    assert l.b.z == 0

def test_sum_chars(ctypes):
    example = ctypes.cdll.LoadLibrary("./example.so")
    sum_chars = example.sum_chars
    sum_chars.argtypes = [ctypes.c_char_p]
    sum_chars.restype = ctypes.c_int
    assert sum_chars(b"hello") == 532

def test_sizeof_simple(ctypes):
    assert ctypes.sizeof(ctypes.c_byte) == 1
    assert ctypes.sizeof(ctypes.c_ubyte) == 1
    assert ctypes.sizeof(ctypes.c_short) == 2
    assert ctypes.sizeof(ctypes.c_ushort) == 2
    assert ctypes.sizeof(ctypes.c_int) == 4
    assert ctypes.sizeof(ctypes.c_uint) == 4
    assert ctypes.sizeof(ctypes.c_long) == 8
    assert ctypes.sizeof(ctypes.c_ulong) == 8
    assert ctypes.sizeof(ctypes.c_int8) == 1
    assert ctypes.sizeof(ctypes.c_uint8) == 1
    assert ctypes.sizeof(ctypes.c_int16) == 2
    assert ctypes.sizeof(ctypes.c_uint16) == 2
    assert ctypes.sizeof(ctypes.c_int32) == 4
    assert ctypes.sizeof(ctypes.c_uint32) == 4
    assert ctypes.sizeof(ctypes.c_int64) == 8
    assert ctypes.sizeof(ctypes.c_uint64) == 8
    assert ctypes.sizeof(ctypes.c_char_p) == 8
    assert ctypes.sizeof(ctypes.c_void_p) == 8

def test_sizeof_struct(ctypes):
    Point = make_point(ctypes)
    Line = make_line(ctypes, Point)
    assert ctypes.sizeof(Point) == 12
    assert ctypes.sizeof(Line) == 24

def test_struct(ctypes):
    Point = make_point(ctypes)
    Line = make_line(ctypes, Point)
    p = Point(x=1, y=2, z=3)
    q = Point(x=4, y=5, z=6)
    l = Line(a=p, b=q)
    assert l.a.x == 1
    assert l.a.y == 2
    assert l.a.z == 3
    assert l.b.x == 4
    assert l.b.y == 5
    assert l.b.z == 6

def test_array(ctypes):
    my_array_class = ctypes.c_int * 5
    assert my_array_class._length_ == 5
    my_array = my_array_class(1, 2, 3, 4, 5)
    assert my_array[0] == 1
    assert my_array[1] == 2
    assert my_array[2] == 3
    assert my_array[3] == 4
    assert my_array[4] == 5

def test_char(ctypes):
    c = ctypes.c_char(b"A")
    assert c.value == b"A"

def test_c_char_p(ctypes):
    hello = b"Hello, world!"
    bye = b"So long!"
    s = ctypes.c_char_p(hello)
    assert s.value == hello
    addr = ctypes.addressof(s)
    hello_addr = ctypes.c_void_p.from_address(addr).value
    s.value = bye
    assert s.value == bye
    assert ctypes.addressof(s) == addr
    bye_addr = ctypes.c_void_p.from_address(addr).value
    assert hello_addr != bye_addr

def test_pointer(ctypes):
    n = ctypes.c_int(42)
    m = ctypes.c_int(1337)
    # Test the more standard way of making a pointer.
    p = ctypes.pointer(n)
    assert p.contents.value == n.value
    # Test this way of creating a pointer, too.
    q = ctypes.POINTER(ctypes.c_int)(n)
    assert q.contents.value == n.value
    # Test changing the contents.
    p.contents = m
    assert p.contents.value == m.value
    void_p = ctypes.c_void_p.from_address(ctypes.addressof(p))
    assert void_p.value == ctypes.addressof(m)

def test_strcpy(ctypes):
    libc = ctypes.cdll.LoadLibrary("libc.so.6")
    dst = ctypes.create_string_buffer(10)
    libc.strncpy(dst, b"Hello, world!", 5)
    assert dst.value == b"Hello"
