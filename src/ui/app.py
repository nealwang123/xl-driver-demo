from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QWidget, QLabel, QComboBox

from src.driver.xl_driver import XLDriver
from PySide6.QtCore import QThread, Signal


class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window_size_ratio = 0.5
        self.height_default = 25
        self.height_btn = self.height_default * 2

        self.init_window()
        self.init_ui()
        self.init_config()

    def init_window(self):
        self.setWindowTitle("XL Driver Demo")
        self.set_window_size(self.window_size_ratio)
        self.set_window_center()

    def set_window_size(self, ratio):
        screen_width, screen_height = self.get_screen_size()
        self.resize(screen_width * ratio, screen_height * ratio)

    def set_window_center(self):
        screen_width, screen_height = self.get_screen_size()
        self.move((screen_width - self.width()) // 2, (screen_height - self.height()) // 2)

    def get_screen_size(self):
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        return geometry.width(), geometry.height()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 垂直主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 水平按钮栏
        button_layout = QHBoxLayout()
        self.btn_init = QPushButton("初始化")
        self.btn_init.setFixedHeight(self.height_btn)
        self.btn_init.clicked.connect(self.init_driver)
        button_layout.addWidget(self.btn_init)

        self.btn_send = QPushButton("发送")
        self.btn_send.setFixedHeight(self.height_btn)
        self.btn_send.clicked.connect(self.send_msg)
        button_layout.addWidget(self.btn_send)

        self.btn_start_listen = QPushButton("开始监听")
        self.btn_start_listen.setFixedHeight(self.height_btn)
        self.btn_start_listen.clicked.connect(self.start_listen)
        button_layout.addWidget(self.btn_start_listen)

        self.btn_stop_listen = QPushButton("停止监听")
        self.btn_stop_listen.setFixedHeight(self.height_btn)
        self.btn_stop_listen.clicked.connect(self.stop_listen)
        button_layout.addWidget(self.btn_stop_listen)

        main_layout.addLayout(button_layout)

        # 文本输入框
        input_layout = QHBoxLayout()

        # 请求报文输入框
        self.input_label_msg = QLabel("请求报文:")
        input_layout.addWidget(self.input_label_msg)

        self.input_msg = QTextEdit()
        self.input_msg.setFixedHeight(self.height_default)
        input_layout.addWidget(self.input_msg)

        # 请求 ID 输入框
        self.input_label_id = QLabel("请求 ID:")
        input_layout.addWidget(self.input_label_id)

        self.input_id = QTextEdit()
        self.input_id.setFixedHeight(self.height_default)
        input_layout.addWidget(self.input_id)

        # ECU 通道下拉选择框
        # self.label_ecu = QLabel("选择 ECU:")
        # input_layout.addWidget(self.label_ecu)
        
        # self.combobox_ecu = QComboBox(self)
        # input_layout.addWidget(self.combobox_ecu)

        main_layout.addLayout(input_layout)

        # 下拉选择框
        self.label_channel = QLabel("CAN 通道:")
        input_layout.addWidget(self.label_channel)
        
        self.combobox_channel = QComboBox(self)
        self.combobox_channel.setFixedWidth(200)
        input_layout.addWidget(self.combobox_channel)
        self.combobox_channel.currentIndexChanged.connect(self.on_channel_selected)

        # 文本提示框
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        main_layout.addWidget(self.text_output)

    def log(self, msg):
        self.text_output.append(msg)

    def init_config(self):
        self.driver = XLDriver()
        # 建立连接，用于日志输出
        self.driver.log_signal.connect(self.log)
        self.driver_config = self.driver.init_config()

        # 清空下拉框
        self.combobox_channel.clear()
        # 遍历 driver_config 中的通道信息并添加到下拉框中
        for i in range(self.driver_config.channelCount):
            channel_name = self.driver_config.channel[i].name.decode("utf-8")
            self.combobox_channel.addItem(channel_name)

    def init_driver(self):
        self.driver.init_driver()

    def on_channel_selected(self, index):
        selected_channel = self.driver_config.channel[index]
        self.log(f"Selected channel: {selected_channel.name.decode('utf-8')}")
        self.log(f"Selected hwtype: {selected_channel.hwType}")
        self.log(f"Selected hwindex: {selected_channel.hwIndex}")
        self.log(f"Selected hwchannel: {selected_channel.hwChannel}")
        self.driver.set_app_config(selected_channel.hwType,selected_channel.hwIndex,selected_channel.hwChannel)

    def send_msg(self):
        self.driver.send_message(int(self.input_id.toPlainText(),16),self.input_msg.toPlainText())

    def start_listen(self):
        self.worker = WorkerThread(self.driver)
        self.worker.log_signal.connect(self.log)
        self.worker.start()

    def stop_listen(self):
        self.driver.stop_listen()

class WorkerThread(QThread):
    log_signal = Signal(str)

    def __init__(self, driver):
        super().__init__()
        self.driver = driver

    def run(self):
        self.driver.receive_message()
