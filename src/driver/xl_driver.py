import ctypes
from ctypes import c_uint, byref, c_char_p, c_uint64, c_long, c_void_p, c_int

from PySide6.QtCore import QObject, Signal

from src.driver.enums.common_event_tag import CommonEventTag
from src.driver.enums.bus_type import BusType
from src.driver.enums.xl_hw_type import XLHwType
from src.driver.enums.xl_status import XLStatus
from src.driver.structures.xl_driver_config import XLDriverConfig
from src.driver.structures.xl_event import XLevent

class XLDriver(QObject):
    # 用于输出日志
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        
        self.DLL_PATH = "src/driver/dll/vxlapi64.dll"
        self.APP_NAME = "CANoe"
        # 选择的 app 通道，Vector Hardware Manager 中配置，使用虚拟通道 Virtual CAN Bus1
        self.APP_CHANNEL = 0
        self.BUS_TYPE = BusType.XL_BUS_TYPE_CAN.value
        # output params
        self.hw_type = c_uint()
        self.hw_index = c_uint()
        self.hw_channel = c_uint()
        self.channel_mask = c_uint()
        self.port_handle = c_long()
        self.event_handle = c_void_p()
        self.driver_config = XLDriverConfig()

        self.listen = False

    # 输出日志
    def log(self,*args):
        msg = " ".join(str(arg) for arg in args)
        self.log_signal.emit(msg)

    def error(self,*args):
        head = "Error:\n"
        msg = " ".join(str(arg) for arg in args)
        self.log_signal.emit(head + msg)
    
    def init_config(self):
        self.open_dll()

        self.open_driver()

        self.get_driver_config()

        self.get_app_config()

        major, minor, build = self.parse_dll_version(self.driver_config.dllVersion)
        self.log(f"Driver Version: {major}.{minor}.{build}")

        return self.driver_config

    def init_driver(self):

        # TODO: IF THERE IS NO APP CONFIG, SET IT
        # also could create a new application in the Vector Hardware Manager
        # or sets the channel configuration in an existing application
        # through xlSetApplConfig()

        # OPTIONAL: get channel index
        # channel_index = vxlapi.xlGetChannelIndex(hwType, hwIndex, hwChannel)
        # self.log("channel index:", channel_index")

        self.get_channel_mask()

        self.open_port()

        self.set_notification()

        self.activate_channel()

        self.log("Initialization Complete!")

    def parse_dll_version(self,dll_version):
        major = (dll_version >> 24) & 0xFF
        minor = (dll_version >> 16) & 0xFF
        build = dll_version & 0xFFFF
        return major, minor, build

    def open_dll(self):
        self.vxlapi = ctypes.CDLL(self.DLL_PATH)

    def open_driver(self):
        status = self.vxlapi.xlOpenDriver()
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Open driver error. Error code: {XLStatus(status).name}")
        self.log("Open driver success!")

    def get_app_config(self):
        app_name = c_char_p(self.APP_NAME.encode("utf-8"))
        app_channel = c_uint(self.APP_CHANNEL)
        bus_type = c_uint(self.BUS_TYPE)

        status = self.vxlapi.xlGetApplConfig(app_name, app_channel, byref(self.hw_type), byref(self.hw_index), byref(
            self.hw_channel), bus_type)
        self.log("hw type: ",XLHwType(self.hw_type.value).name)
        self.log("hw index: ",self.hw_index.value)
        self.log("hw channel: ",self.hw_channel.value)
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Get app config error. Error code: {XLStatus(status).name}")
        self.log("Get app config success!")
        if XLHwType.XL_HWTYPE_NONE.value == self.hw_type.value:
            raise Exception("Not configured channel!")
    
    def set_app_config(self,hw_type,hw_index,hw_channel):
        app_name = c_char_p(self.APP_NAME.encode("utf-8"))
        app_channel = c_uint(self.APP_CHANNEL)
        bus_type = c_uint(self.BUS_TYPE)
        status = self.vxlapi.xlSetApplConfig(app_name,app_channel,hw_type, hw_index, hw_channel, bus_type)
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Set app config error. Error code: {XLStatus(status).name}")
        self.log("Set app config success!")
        # 更新 app 配置，用于后续建立连接
        self.get_app_config()

    def get_channel_mask(self):
        self.channel_mask = self.vxlapi.xlGetChannelMask(self.hw_type, self.hw_index, self.hw_channel)
        if self.channel_mask == 0:
            raise Exception("Get channel mask error.")

    def get_driver_config(self):
        status = self.vxlapi.xlGetDriverConfig(byref(self.driver_config))

        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Get driver config error. Error code: {XLStatus(status).name}")
        self.log(f"Get driver config success!")

        self.log("--------------Driver Config--------------")
        self.log("channel count: ",self.driver_config.channelCount)
        for i in range(self.driver_config.channelCount):
            ch = self.driver_config.channel[i]
            self.log("channel",i + 1,": ",ch.name.decode("utf-8"))
            self.log("channel",i + 1,"type: ",ch.hwType)
            self.log("channel",i + 1,"driver: ",ch.channelMask)
        self.log("-----------------------------------------")

    def open_port(self):
        app_name = c_char_p(self.APP_NAME.encode("utf-8"))
        access_mask = c_uint64(self.channel_mask)
        permission_mask = access_mask
        rx_queue_size = c_uint(256)
        # Interface version for CAN, LIN, DAIO, K-Line
        xl_interface_version = c_uint(3)
        bus_type = c_uint(self.BUS_TYPE)

        status = self.vxlapi.xlOpenPort(byref(self.port_handle), app_name, access_mask, byref(permission_mask),
                                        rx_queue_size, xl_interface_version, bus_type)
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Open port error. Error code: {XLStatus(status).name}")
        self.log("Open port success!")

    def close_port(self):
        status = self.vxlapi.xlClosePort(self.port_handle)
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Close port error. Error code: {XLStatus(status).name}")
        self.log("Close port success!")

    def close_driver(self):
        status = self.vxlapi.xlCloseDriver()
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Close driver config error. Error code: {XLStatus(status).name}")
        self.log("Close driver success!")

    # 注册消息事件，返回的 event_handle 用于 WaitForSingleObject 接收消息
    def set_notification(self):
        queue_level = c_int(1)
        status = self.vxlapi.xlSetNotification(self.port_handle, byref(self.event_handle), queue_level)
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Set notification error. Error code: {XLStatus(status).name}")
        self.log("Set notification success!")

    def activate_channel(self):
        access_mask = c_uint64(self.channel_mask)
        bus_type = c_uint(self.BUS_TYPE)
        flag = c_uint()
        status = self.vxlapi.xlActivateChannel(self.port_handle, access_mask, bus_type, flag)
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Active channel error. Error code: {XLStatus(status).name}")
        self.log("Active channel success!")

    def deactivate_channel(self):
        access_mask = c_uint64(self.channel_mask)
        status = self.vxlapi.xlDeactivateChannel(self.port_handle, access_mask)
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Deactive channel error. Error code: {XLStatus(status).name}")
        self.log("Deactive channel success!")

    def send_message(self, id, data_str):
        # 将 data_str 转换为字节列表（每 2 个字符组成一项，每项都是 8 字节）
        data = data_str.replace(" ", "")
        byte_list = [int(data[i:i + 2], 16) for i in range(0, len(data), 2)]

        xl_event = XLevent()
        xl_event.tag = CommonEventTag.XL_TRANSMIT_MSG.value
        xl_event.tagData.msg.id = id
        xl_event.tagData.msg.dlc = len(byte_list)
        xl_event.tagData.msg.flags = 0
        for i in range(len(byte_list)):
            xl_event.tagData.msg.data[i] = byte_list[i]
            
        access_mask = c_uint64(self.channel_mask)
        message_count = c_uint(1)

        status = self.vxlapi.xlCanTransmit(self.port_handle, access_mask, byref(message_count), byref(xl_event))
        if XLStatus(status) != XLStatus.XL_SUCCESS:
            raise Exception(f"Send message error. Error code: {XLStatus(status).name}")
        self.log("Send message success!")
        self.log("Send ID: ",hex(xl_event.tagData.msg.id),"; Send message: ",data_str)

    # 官方推荐的接收方式，WaitForSingleObject + xlReceive 轮询
    def receive_message(self):
        self.listen = True
        self.log("Listening...")
        timeout = 1000
        # 持续监听事件
        while self.listen:
            result = ctypes.windll.kernel32.WaitForSingleObject(self.event_handle, timeout)
            # 事件触发
            if result == 0x0:
                # 轮询尝试接收数据
                while True:
                    xl_event = XLevent()
                    xl_size = c_uint(1)
                    status = self.vxlapi.xlReceive(self.port_handle, byref(xl_size), byref(xl_event))
                    # 接收成功
                    if XLStatus(status) == XLStatus.XL_SUCCESS:
                        dlc = xl_event.tagData.msg.dlc
                        data = [xl_event.tagData.msg.data[i] for i in range(dlc)]
                        self.log("Received Message ID:", hex(xl_event.tagData.msg.id),"; Received message: " + " ".join(f"{b:02X}" for b in data))
                    # 接收完成，队列中已没有数据
                    elif XLStatus(status) == XLStatus.XL_ERR_QUEUE_IS_EMPTY:
                        # 跳出循环，回到等待事件
                        break
                    # 接收失败
                    else:
                        raise Exception(f"Receive error: {XLStatus(status).name}")
            # 超时
            elif result == 0x102:
                # 继续监听
                self.log("Listening...")
            else:
                raise Exception("WaitForSingleObject error: ",result)

    def stop_listen(self):
        self.listen = False
