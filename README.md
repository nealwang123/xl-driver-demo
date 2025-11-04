# xl-driver-demo

通过 Python 调用 [XL-Driver-Library](https://www.vector.com/us/en/products/products-a-z/libraries-drivers/xl-driver-library/#) 实现收发 [Vector 硬件](https://www.vector.com/us/en/products/products-a-z/hardware/#) 的消息

## 预览

![image](https://github.com/user-attachments/assets/2050443e-39fa-4f28-98ec-e19d60b87e28)

## 项目概述

这是一个使用PySide6开发的Vector硬件驱动程序演示应用程序，用于通过Python调用Vector XL-Driver-Library实现收发Vector硬件消息。

## 项目结构

```
xl-driver-demo/
├── src/
│   ├── main.py              # 应用程序入口点
│   ├── ui/
│   │   └── app.py           # PySide6 GUI应用程序
│   └── driver/
│       ├── xl_driver.py     # Vector硬件驱动程序
│       ├── dll/
│       │   ├── vxlapi64.dll # Vector驱动程序库
│       │   ├── vxlapi64.lib # 库文件
│       │   └── vxlapi.h     # 头文件
│       ├── enums/           # 枚举定义
│       └── structures/      # 数据结构定义
├── test_app.py              # 测试应用程序（不依赖硬件）
├── requirements.txt         # Python依赖包列表
└── README.md                # 项目说明
```

## 功能

- 选择 CAN 硬件的通道
- 建立连接
- 发送报文
- 监听总线

## 运行要求

### 硬件要求
- Vector硬件设备（如CANalyzer、CANoe等）
- 已安装Vector硬件驱动程序

### 软件要求
- Python 3.7+
- PySide6
- ctypes（Python标准库）

## 安装和运行

### 1. 安装依赖
```bash
# 使用requirements.txt安装所有依赖
pip install -r requirements.txt

# 或者手动安装
pip install PySide6
```

### 2. 激活虚拟环境（如果使用虚拟环境）
```bash
.venv\Scripts\activate
```

### 3. 运行主应用程序（需要Vector硬件）
```bash
python src/main.py
```

### 4. 运行测试应用程序（无需硬件）
```bash
python test_app.py
```

## 应用程序功能

### 主应用程序功能
- **初始化**: 初始化Vector硬件驱动程序
- **发送**: 发送CAN消息到总线
- **开始监听**: 开始监听CAN总线消息
- **停止监听**: 停止监听CAN总线消息
- **通道选择**: 选择CAN硬件通道

### 当前状态

✅ **已完成**:
- PySide6 GUI应用程序框架
- Vector硬件驱动程序封装
- 基本的UI组件和布局
- 依赖项安装和配置

⚠️ **需要Vector硬件**:
- 实际的硬件通信功能需要连接Vector硬件设备
- 需要在Vector Hardware Manager中配置应用程序通道

## 故障排除

### 常见问题

1. **"Not configured channel!" 错误**
   - 原因：没有在Vector Hardware Manager中配置应用程序通道
   - 解决：在Vector Hardware Manager中创建或配置应用程序

2. **"ModuleNotFoundError: No module named 'PySide6'"**
   - 原因：PySide6未安装
   - 解决：运行 `pip install PySide6`

3. **DLL加载失败**
   - 原因：vxlapi64.dll文件缺失或路径错误
   - 解决：确保dll文件位于正确路径

### 测试模式

如果无法连接Vector硬件，可以使用测试模式：
```bash
python test_app.py
```

测试模式提供：
- 完整的UI界面
- 模拟的按钮响应
- 不依赖实际硬件的功能演示

## 开发说明

### 项目特点
- 使用PySide6构建现代GUI界面
- 通过ctypes调用Vector原生API
- 多线程消息处理
- 模块化设计，易于扩展

## 注意

通过 Vector 提供的 Xl-Driver-Library 开发工具***过于繁琐***，建议使用 python 第三方库：[udsoncan](https://udsoncan.readthedocs.io/en/latest/index.html)，参考 udsoncan 的[官方示例](https://udsoncan.readthedocs.io/en/latest/udsoncan/examples.html#using-uds-over-python-can)

## 联系方式

如有问题，请参考项目GitHub页面或联系开发人员。
