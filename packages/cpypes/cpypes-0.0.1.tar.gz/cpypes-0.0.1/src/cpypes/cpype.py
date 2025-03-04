""" Core IPC implementation

TODO: Figure out how to free all leaked pointers before exiting.

TODO: Fix function docstrings. They're pretty much all wrong.
"""

import appdirs
import os
import socket
import struct
import subprocess

from .simple_types import *
from . import install


CP_LOAD =    0
CP_FIND =    1
CP_READ =    2
CP_WRITE =   3
CP_SIZE =    4
CP_OFFSETS = 5
CP_ALLOC =   6
CP_FREE =    7
CP_CALL =    8


pype = None
FMT_DICT = {1: "B", 2: "H", 4: "I", 8: "Q"}


class Pype:
    def __init__(self, rfd, wfd, child=None):
        self.rfd = rfd
        self.wfd = wfd
        self.child = child
        self.send(b"cpyp", flush=True)
        assert self.recv(4) == b"cpyp"
        self.word_size = struct.unpack("!B", self.recv(1))[0]
        self.word_fmt = "!" + FMT_DICT[self.word_size]

    @classmethod
    def spawn(cls, debug=None):
        install.install()
        child = subprocess.Popen([install.server_path],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        return cls(child.stdout, child.stdin, child=child)

    @classmethod
    def connect(cls, address):
        sock = socket.socket()
        sock.connect(address)
        return cls(sock, sock)

    def close(self):
        # TODO: Cleanup? Maybe server can handle that.
        self.rfd.close()
        if self.wfd is not self.rfd:
            self.wfd.close()
        if self.child is not None:
            self.child.wait()
            print(self.child.stderr)

    def flush(self):
        if not isinstance(self.wfd, socket.socket):
            self.wfd.flush()

    def send(self, data, flush=False):
        if isinstance(self.wfd, socket.socket):
            self.wfd.sendall(data)
        else:
            self.wfd.write(data)
            if flush:
                self.wfd.flush()

    def recv(self, length):
        received = b""
        while len(received) < length:
            if isinstance(self.rfd, socket.socket):
                received += self.rfd.recv(length - len(received))
            else:
                received += self.rfd.read(length - len(received))
        return received

    def recv_success(self):
        received = self.recv(1)
        return not bool(struct.unpack("!B", received)[0])

    def recv_word(self):
        received = self.recv(self.word_size)
        return struct.unpack(self.word_fmt, received)[0]

    def send_word(self, word, flush=False):
        self.send(struct.pack(self.word_fmt, word), flush=flush)


def connect(address):
    """ Connect to a cpypes server socket """
    global pype
    if pype is not None:
        raise ValueError("Already connected!")
    pype = Pype.connect(address)


def _get_pype():
    # TODO: Handle the case where the child process fails immediately.
    global pype
    if pype is None:
        pype = Pype.spawn()
    return pype


def load(name):
    """ Load a shared object

    Args:
        name (str): Name of library to load

    Returns:
        Address of remote loaded library
    """
    name = _interpret_libname(name)
    pype = _get_pype()
    pype.send(struct.pack("!B", CP_LOAD))
    pype.send(struct.pack("!I", len(name)))
    pype.send(name.encode(), flush=True)
    rtn = pype.recv_word()
    if not rtn:
        raise ValueError(f"Could not load library '{name}'")
    return rtn

def find(library, symbol, allow_null=False):
    """ Find a symbol in a shared object

    Args:
        library (cpypes.CDLL): cpypes library object
        symbol (str): Name of symbol to load
        allow_null (bool): Allow NULL result without error

    Returns:
        Address of remote symbol
    """
    pype = _get_pype()
    pype.send(struct.pack("!B", CP_FIND))
    pype.send_word(library.handle)
    pype.send(struct.pack("!I", len(symbol)))
    pype.send(symbol.encode(), flush=True)
    rtn = pype.recv_word()
    if not rtn and not allow_null:
        raise ValueError(f"Could not find '{symbol}' in '{library.path}'")
    return rtn

def read(address, ctype):
    """ Read simple ctype from remote memory

    Args:
        address (int): Pointer to beginning of remote object
        ctype (cpypes._SimpleCData): cpypes type of remote object

    Returns:
        Value of remote object
    """
    pype = _get_pype()
    ctype._layout_()
    pype.send(struct.pack("!B", CP_READ))
    pype.send(ctype._byte_rep_())
    pype.send_word(address, flush=True)
    data = pype.recv(ctype._size_())
    return ctype._decode_(data)

def write(address, ctype, value):
    """ Write values to remote memory

    Args:
        address (int): Pointer to beginning of remote object
        ctype (cpypes._SimpleCData type): Type of remote object
        value: Simple value to write
    """
    pype = _get_pype()
    ctype._layout_()
    pype.send(struct.pack("!B", CP_WRITE))
    pype.send(ctype._byte_rep_())
    pype.send_word(address)
    pype.send(ctype._encode_(value), flush=True)

def size(ctype):
    """ Get size of type from remote

    Args:
        ctype (cpypes._CData type): ctype to find size of

    Returns:
        Size in bytes as an int
    """
    pype = _get_pype()
    pype.send(struct.pack("!B", CP_SIZE))
    pype.send(ctype._byte_rep_(), flush=True)
    return pype.recv_word()

def offsets(ctype):
    """ Get offsets of structure type from remote

    Args:
        ctype (cpypes.Structure type): ctype struct to get offsets of

    Returns:
        List of integer offsets for each field (in bytes)
    """

    pype = _get_pype()
    pype.send(struct.pack("!B", CP_OFFSETS))
    pype.send(ctype._byte_rep_(), flush=True)
    rtn = [pype.recv_word() for _ in ctype._fields_]
    return rtn

def alloc(size):
    """ Allocate memory for a remote object

    Args:
        size (int): Number of bytes to allocate

    Returns:
        Pointer to remote buffer allocated
    """
    pype = _get_pype()
    pype.send(struct.pack("!B", CP_ALLOC))
    pype.send_word(size, flush=True)
    return pype.recv_word()

def free(address):
    """ Free a remote object

    TODO: Handle errors.

    Args:
        address (int): Pointer to remote object to free
    """
    pype = _get_pype()
    pype.send(struct.pack("!B", CP_FREE))
    pype.send_word(address, flush=True)

def call(func, abi, rtn_ctype, arg_ctypes, arg_values):
    """ Call a function in the remote process

    Args:
        func (int): Pointer to remote function
        abi (cpypes.ABI): ABI of remote function
        rtn_ctype (cpypes._CData type): Function's return type
        arg_ctypes (list): Types of function's arguments
        arg_values (list): List of argument values

    Returns:
        Value returned from function
    """
    if len(arg_ctypes) != len(arg_values):
        raise ValueError("Argument types/values length mismatch")

    # Create a new arg list where pure Python args have been turned
    # into actual `cpypes` objects on the remote side. These arguments
    # should be automatically freed when they are dropped from scope
    # at the end of the function.
    new_args = []
    for arg, arg_type in zip(arg_values, arg_ctypes):
        if isinstance(arg, arg_type):
            new_args.append(arg)
        else:
            new_arg = arg_type(arg)
            new_args.append(new_arg)

    pype = _get_pype()
    pype.send(struct.pack("!B", CP_CALL))
    pype.send_word(func)
    pype.send(struct.pack("!B", abi))
    pype.send(rtn_ctype._byte_rep_())
    pype.send(struct.pack("!I", len(arg_ctypes)))
    for ctype in arg_ctypes:
        pype.send(ctype._byte_rep_())
    for arg in new_args:
        pype.send_word(arg._ptr_)
    pype.flush()

    result_pointer = pype.recv_word()
    result = rtn_ctype.from_address(result_pointer, needs_free=True)

    result_value = result.value
    return result_value


def _interpret_libname(libname):
    """ Interpret a library name in accordance with `dlopen`

    If there's a slash, then it's a path, so we can make it absolute
    so there's no ambiguity in case the server isn't running in our
    CWD. Otherwise, it indicates a system lib in the search path, so
    we shouldn't change it. """
    if not "/" in libname:
        return libname
    else:
        return os.path.abspath(libname)
