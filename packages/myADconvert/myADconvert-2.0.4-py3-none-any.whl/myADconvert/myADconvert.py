# ver 2.0.4

import platform
os = platform.system()
import ctypes
if os == 'Windows':
    import ctypes.wintypes
from enum import IntEnum, auto


class DIO_ch(IntEnum):
    O_0 = 0
    O_1 = auto()
    O_2 = auto()
    O_3 = auto()
    O_4 = auto()
    O_5 = auto()
    O_6 = auto()
    O_7 = auto()
    O_10 = auto()
    O_11 = auto()
    O_12 = auto()
    O_13 = auto()
    O_14 = auto()
    O_15 = auto()
    O_16 = auto()
    O_17 = auto()


class _AIOfunc:
    def __init__(self):
        if os == 'Windows':
            caio_dll = ctypes.windll.LoadLibrary('caio.dll')
        elif os == 'Linux':
            caio_dll = ctypes.cdll.LoadLibrary('libcaio.so')

        # Define function
        self.AioInit = caio_dll.AioInit
        self.AioInit.restype = ctypes.c_long
        self.AioInit.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_short)]

        self.AioGetAoMaxChannels = caio_dll.AioGetAoMaxChannels
        self.AioGetAoMaxChannels.restype = ctypes.c_long
        self.AioGetAoMaxChannels.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

        self.AioGetAiMaxChannels = caio_dll.AioGetAiMaxChannels
        self.AioGetAiMaxChannels.restype = ctypes.c_long
        self.AioGetAiMaxChannels.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short)]

        self.AioSingleAiEx = caio_dll.AioSingleAiEx
        self.AioSingleAiEx.restype = ctypes.c_long
        self.AioSingleAiEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_float)]

        self.AioSingleAoEx = caio_dll.AioSingleAoEx
        self.AioSingleAoEx.restype = ctypes.c_long
        self.AioSingleAoEx.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_float]

        self.AioOutputDoBit = caio_dll.AioOutputDoBit
        self.AioOutputDoBit.restype = ctypes.c_long
        self.AioOutputDoBit.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_short]

        self.AioExit = caio_dll.AioExit
        self.AioExit.restype = ctypes.c_long
        self.AioExit.argtypes = [ctypes.c_short]

        self.AioInputDiBit = caio_dll.AioInputDiBit
        # self.AioInputDiBit.restype = ctypes.c_long
        # self.AioInputDiBit.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_ubyte)]

        self._lret = ctypes.c_long()
        self._aio_id = ctypes.c_short()
        self._AiData = ctypes.c_float()
        self._DiData = ctypes.c_short()
        self.MaxAoChannels = ctypes.c_short()
        self.MaxAiChannels = ctypes.c_short()

    def init(self, devicename):
        self._lret.value = self.AioInit(devicename.encode(), ctypes.byref(self._aio_id))
        if self._lret.value == 0:
            print('Success to initialize')
            self.AioGetAoMaxChannels(self._aio_id, ctypes.byref(self.MaxAoChannels))
            self.AioGetAiMaxChannels(self._aio_id, ctypes.byref(self.MaxAiChannels))
            return 1
        else:
            print('Failure to initialize')
            return 0

    def read(self, channel, AI_DI='AI'):
        if AI_DI == 'AI':
            if channel < 0 or channel > self.MaxAiChannels.value - 1:
                print('Set channel is failure')
                return -100
            ret = self.AioSingleAiEx(self._aio_id, channel, ctypes.byref(self._AiData))
            if ret != 0:
                print("CHECK")
            return self._AiData.value
        else:
            ret = self.AioInputDiBit(self._aio_id, channel, ctypes.byref(self._DiData))
            if ret != 0:
                print("CHECK")
            return self._DiData.value

    def write(self, channel, value, AO_DO='AO'):
        if AO_DO == 'AO':
            if channel < 0 or channel > self.MaxAoChannels.value - 1:
                print('Set channel is failure')
                return 0
            self._lret.value = self.AioSingleAoEx(self._aio_id, channel, value)
        else:
            self._lret.value = self.AioOutputDoBit(self._aio_id, channel, bool(value))
        if self._lret.value != 0:
            print('Action failure')
            return 0
        return 1

    def exit(self):
        for i in range(self.MaxAoChannels.value):
            self.write(i, 0, AO_DO='AO')
        i = 0
        while self.write(i, 0, AO_DO='DO'):
            i = i + 1
        self.AioExit(self._aio_id)


class _DIOfunc:
    def __init__(self):
        if os == 'Windows':
            cdio_dll = ctypes.windll.LoadLibrary('cdio.dll')
        elif os == 'Linux':
            cdio_dll = ctypes.cdll.LoadLibrary('libcdio.so')

        # Define function
        self.DioInit = cdio_dll.DioInit
        self.DioInit.restype = ctypes.c_long
        self.DioInit.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_short)]

        self.DioGetMaxPorts = cdio_dll.DioGetMaxPorts
        self.DioGetMaxPorts.restype = ctypes.c_long
        self.DioGetMaxPorts.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]

        self.DioOutBit = cdio_dll.DioOutBit
        self.DioOutBit.restype = ctypes.c_long
        self.DioOutBit.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_ubyte]

        self.DioInpBit = cdio_dll.DioInpBit
        self.DioInpBit.restype = ctypes.c_long
        self.DioInpBit.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.POINTER(ctypes.c_ubyte)]

        self.DioExit = cdio_dll.DioExit
        self.DioExit.restype = ctypes.c_long
        self.DioExit.argtypes = [ctypes.c_short]

        self._lret = ctypes.c_long()
        self._dio_id = ctypes.c_short()
        self._DiData = ctypes.c_ubyte()
        self.MaxDoChannels = ctypes.c_short()
        self.MaxDiChannels = ctypes.c_short()

    def init(self, devicename):
        self._lret.value = self.DioInit(devicename.encode(), ctypes.byref(self._dio_id))
        if self._lret.value == 0:
            print('Success to initialize')
            self.DioGetMaxPorts(self._dio_id, self.MaxDiChannels, self.MaxDoChannels)
            self.MaxDiChannels = self.MaxDiChannels.value * 8
            self.MaxDoChannels = self.MaxDoChannels.value * 8
            return 1
        else:
            print('Failure to initialize')
            return 0

    def write(self, channel, value):
        if type(channel) == DIO_ch:
            channel = channel.value
        self._lret.value = self.DioOutBit(self._dio_id, channel, bool(value))
        if self._lret.value != 0:
            print('Action failure')
            return 0
        return 1

    def read(self, channel):
        self._lret.value = self.DioInpBit(self._dio_id, channel, ctypes.byref(self._DiData))
        if self._lret.value != 0:
            print('Action failure')
            return 0
        return self._DiData.value

    def exit(self):
        for i in range(self.MaxDoChannels):
            self.write(i, False)
        self.DioExit(self._dio_id)

class ADfunc:
    def __init__(self, DeviceType):
        self.devicetype = DeviceType
        if DeviceType == 'AIO':
            self.now_func = _AIOfunc()
        elif DeviceType == 'DIO':
            self.now_func = _DIOfunc()

    def init(self, devicename):
        return self.now_func.init(devicename)

    def write(self, channel, value, AO_DO=''):
        if self.devicetype == 'AIO':
            self.now_func.write(channel, value, AO_DO)
        elif self.devicetype == 'DIO':
            self.now_func.write(channel, value)

    def read(self, channel, AI_DI=''):
        if self.devicetype == 'AIO':
            return self.now_func.read(channel, AI_DI)
        elif self.devicetype == 'DIO':
            return self.now_func.read(channel)

    def exit(self):
        self.now_func.exit()




