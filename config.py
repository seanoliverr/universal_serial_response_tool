"""
串口调试助手配置文件
"""
import os

# 应用配置
APP_NAME = "串口应答调试助手"
APP_VERSION = "1.0.10"

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".uart_tool")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
RULES_FILE = os.path.join(CONFIG_DIR, "rules.json")
QUICK_COMMANDS_FILE = os.path.join(CONFIG_DIR, "quick_commands.json")
BATCH_COMMANDS_FILE = os.path.join(CONFIG_DIR, "batch_commands.json")

# 串口参数默认值
DEFAULT_BAUDRATE = 9600
DEFAULT_BYTESIZE = 8
DEFAULT_STOPBITS = 1
DEFAULT_PARITY = 'N'
DEFAULT_TIMEOUT = 0.1

# 波特率列表
BAUDRATES = [
    110, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 
    57600, 115200, 230400, 460800, 921600
]

# 数据位
BYTESIZES = [5, 6, 7, 8]

# 停止位
STOPBITS = [1, 1.5, 2]

# 校验位
PARITIES = ['None', 'Odd', 'Even', 'Mark', 'Space']

# 流控制
FLOWCONTROLS = ['None', 'RTS/CTS', 'XON/XOFF']

# UI 配置
DEFAULT_FONT_SIZE = 9
MAX_HISTORY_COUNT = 20

# 帧单元长度上限：fixed / wildcard 等按字节填充的单元放开到 65535；
# increment 数值单元按二进制宽度实际有意义的上限为 16 字节（再大起始值无法表达）。
MAX_FRAME_UNIT_LENGTH = 65535
MAX_INCREMENT_UNIT_LENGTH = 16
