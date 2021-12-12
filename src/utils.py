from json import load as json_load
import os


def mkpath(*paths):
    return os.path.normpath(os.path.join(*paths))


def int2byte(a):
    return bytes([a])


def int2hex(a):
    return hex(a)[2:]


def hex2int(a):
    return int(a, 16)


def bytes2int(a):
    return int.from_bytes(a, "little")


def bytes2hex(a):
    return int2hex(bytes2int(a))


def bytes2string(a):
    return a.decode("utf-8")


def int2bits(a):
    return bin(a)[2:]


def bytes2bits(a):
    return int2bits(bytes2int(a))


def bits2int(a):
    return int(a, 2)


def skip(*args, **kwargs):
    pass


with open("msg.json" if os.path.isfile("msg.json") else mkpath("src", "msg.json"), 'r', encoding="utf-8") as file:
    MSG = json_load(file)
