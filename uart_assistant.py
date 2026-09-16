"""
串口调试助手 - 主窗口（修复版）
"""
import sys
import json
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QLabel, QPushButton, 
                             QComboBox, QSpinBox, QCheckBox, QTextEdit, QGroupBox,
                             QStatusBar, QMessageBox, QFileDialog, QShortcut, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
                             QDialog, QTabWidget, QSizePolicy, QScrollArea, QLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QRect, QSize, QPoint
from PyQt5.QtGui import QFont, QKeySequence, QTextCursor

import serial
import serial.tools.list_ports

from config import *


# ==================== 国际化（中文 / English） ====================
CURRENT_LANG = 'zh'  # 'zh' 或 'en'

# 中文 -> 英文 翻译表（key 为代码中使用的中文原文）
EN_TRANSLATIONS = {
    # 串口设置
    "串口设置": "Serial Settings",
    "端口:": "Port:",
    "刷新": "Refresh",
    "波特率:": "Baud Rate:",
    "数据位:": "Data Bits:",
    "停止位:": "Stop Bits:",
    "校验位:": "Parity:",
    "流控制:": "Flow Control:",
    "打开串口": "Open Port",
    "关闭串口": "Close Port",
    "● 未连接": "● Disconnected",
    "● 已连接": "● Connected",
    "显示:": "Display:",
    "文本": "Text",
    "时间戳": "Timestamp",
    "保存": "Save",
    "清除": "Clear",
    # 标签页
    "批量发送": "Batch Send",
    "单次发送": "Single Send",
    "自动应答": "Auto Reply",
    # 批量发送
    "启用批量发送": "Enable Batch Send",
    "发送指令列表": "Command List",
    "添加指令": "Add Command",
    "删除指令": "Delete Command",
    "导入指令": "Import Commands",
    "导出指令": "Export Commands",
    "间隔 (ms):": "Interval (ms):",
    "次数:": "Count:",
    "无限循环": "Loop Forever",
    "全部固定间隔": "Fixed Interval for All",
    "指定发送间隔": "Custom Interval",
    "清空指令": "Clear All",
    "当前没有可清空的快捷指令": "There are no quick commands to clear.",
    "确定要清空全部 ": "Are you sure you want to clear all ",
    " 条快捷指令吗？此操作不可撤销。": " quick commands? This action cannot be undone.",
    "换行间隔...": "Line-break Interval...",
    "显示设置": "Display Settings",
    "换行间隔:": "Line-break Interval:",
    "恢复默认(33 ms)": "Reset Default (33 ms)",
    "接收显示换行间隔：\n在收到最后一个字节后，静默超过此时间未再收到新数据，\n才把当前累积的数据显示为一行。\n值越大：更容易把一整帧数据合并到一行；\n值越小：接收显示更及时。": "Line-break interval for the receive view:\nAfter the last byte arrives, if no new data comes in during this idle period,\nthe accumulated bytes are shown as a single line.\nLarger value: more likely to merge a whole frame into one line.\nSmaller value: receive view updates more responsively.",
    "已启用『全部固定间隔』，不能再为单条指令设置自定义间隔。请先取消『全部固定间隔』。": "『Fixed Interval for All』 is enabled. Cannot set a custom interval for a single command. Please disable it first.",
    "存在已配置自定义发送间隔的指令，无法启用全局固定间隔：": "Some commands have a custom interval configured, cannot enable global fixed interval:",
    "请先在指令编辑中取消其自定义间隔，或不勾选此项。": "Please clear their custom interval in the command edit dialog, or do not enable this option.",
    "开始": "Start",
    "停止": "Stop",
    # 单次发送
    "格式:": "Format:",
    "显示发送": "Show Sent",
    "发送": "Send",
    "清空": "Clear",
    # 自动应答
    "启用自动应答": "Enable Auto Reply",
    "失配按帧头判定": "Strict Mismatch by Frame Head",
    "配置规则": "Configure Rules",
    "规则列表": "Rule List",
    "添加规则": "Add Rule",
    "编辑规则": "Edit Rule",
    "自动换行": "Word Wrap",
    "递增值": "Increment",
    "普通数值": "Normal",
    "BCD十进制": "BCD Decimal",
    "递增值的数值模式：普通数值按二进制加；BCD 按十进制加(HEX 显示跳过 A~F)": "Increment number mode: Normal uses binary +; BCD uses decimal + (HEX skips A~F)",
    "使用说明": "Help",
    "步进": "Step",
    "快捷指令": "Quick Commands",
    "发送指令": "Send Command",
    "上移": "Move Up",
    "下移": "Move Down",
    "没有指令可导出": "No commands to export",
    "起始值（十进制或0x前缀）": "Initial value (decimal or 0x-prefixed)",
    "起始值超出字节长度可表示的最大值": "Initial value exceeds max representable by byte length",
    "起始值格式无效": "Invalid initial value format",
    "删除规则": "Delete Rule",
    "导入规则": "Import Rules",
    "导出规则": "Export Rules",
    # 折叠箭头
    "隐藏左侧面板": "Hide left panel",
    "显示左侧面板": "Show left panel",
    # 日志/状态栏
    "保存日志": "Save Log",
    "日志未开启": "Logging Off",
    "日志已开启（等待打开串口写入）": "Logging On (waiting for port to open)",
    "就绪": "Ready",
    # 菜单
    "设置": "Settings",
    "语言": "Language",
    "中文": "中文",
    "English": "English",
    # 齿轮菜单 - 系统日志排查后门
    "系统日志(仅排查问题用)": "System Log (Troubleshooting Only)",
    "系统日志": "System Log",
    "系统日志已开启，之后的运行信息将写入：": "System log enabled. Subsequent runtime output will be written to:",
    "该设置已保存，重启程序后仍保持开启。": "This setting is saved and remains enabled after restart.",
    "系统日志开启失败，请检查日志保存路径是否可写。": "Failed to enable system log. Please check whether the log save path is writable.",
    "系统日志已关闭，重启程序后保持关闭。": "System log disabled. It remains off after restart.",
    # 表头
    "选中": "Select",
    "指令": "Command",
    "格式": "Format",
    "操作": "Action",
    "启用": "Enable",
    "名称": "Name",
    "匹配条件": "Match",
    "应答数据": "Response",
    # 动态文本模板片段
    "长度：": "Length: ",
    " 字节": " bytes",
    "字节": "bytes",
    "进度：": "Progress: ",
    "已配置 ": "Configured ",
    " 条规则": " rule(s)",
    "当前日志: ": "Current log: ",
    "串口 ": "Port ",
    " 已打开": " opened",
    "串口已关闭": "Port closed",
    "数据已保存到 ": "Data saved to ",
    "版本: ": "Version: ",
    "接收：": "RX: ",
    "发送：": "TX: ",
    # 对话框 / 消息框通用
    "警告": "Warning",
    "错误": "Error",
    "成功": "Success",
    "确认": "Confirm",
    "确定": "OK",
    "取消": "Cancel",
    "编辑": "Edit",
    "串口未打开": "Serial port not open",
    "请先选择要编辑的指令": "Please select a command to edit first",
    "请先选择要删除的指令": "Please select command(s) to delete first",
    "没有指令可导出": "No commands to export",
    "请至少选择一条指令": "Please select at least one command",
    "请先选择要删除的规则": "Please select rule(s) to delete first",
    "没有规则可导出": "No rules to export",
    "添加指令": "Add Command",
    "编辑指令": "Edit Command",
    "日志文件夹不存在": "Log folder does not exist",
    # 日志设置对话框
    "日志设置": "Log Settings",
    "保存接收日志": "Save Receive Log",
    "保存控制台日志": "Save Console Log",
    "保存路径:": "Save Path:",
    "留空则使用默认日志目录": "Leave empty to use default log directory",
    "浏览...": "Browse...",
    "打开文件夹": "Open Folder",
    "使用自定义文件名（不勾选则按 时间_端口.log 自动命名）": "Use custom file name (otherwise auto-named as time_port.log)",
    "文件名:": "File Name:",
    "文件名: (自动命名：时间_端口.log)": "File Name: (auto-named: time_port.log)",
    "例如 my_log.log（可省略 .log 后缀）": "e.g. my_log.log (.log suffix optional)",
    "选择日志保存目录": "Select Log Save Directory",
    # 规则对话框
    "自动应答规则配置": "Auto Reply Rule Configuration",
    "规则配置": "Rule Configuration",
    "规则名称:": "Rule Name:",
    "  数据格式:": "  Data Format:",
    "匹配帧配置": "Match Frame Configuration",
    "应答帧配置": "Response Frame Configuration",
    "应答帧 #": "Response Frame #",
    "添加应答帧": "Add Response Frame",
    "删除本条应答": "Remove This Response",
    "至少需要保留一条应答帧": "At least one response frame is required",
    "提示": "Info",
    "添加匹配单元": "Add Match Unit",
    "添加应答单元": "Add Response Unit",
    "应答延迟 (ms):": "Response Delay (ms):",
    "删除": "Delete",
    "名称": "Name",
    "固定值": "Fixed",
    "通配符": "Wildcard",
    "校验": "Checksum",
    "引用匹配值": "Reference",
    "值 (HEX 或 文本)": "Value (HEX or Text)",
    "任意值（按长度跳过）": "Any value (skip by length)",
    "校验自动比对": "Checksum auto-compared",
    "校验自动计算": "Checksum auto-calculated",
    "引用的匹配单元名称": "Referenced match unit name",
    "起:": "From:",
    "止:": "To:",
    "高位在前": "Big-endian",
    "低位在前": "Little-endian",
    "单元字节长度错误": "Unit Byte Length Error",
    # 消息提示
    "打开串口失败：": "Failed to open port: ",
    "发送失败：": "Send failed: ",
    "保存失败：": "Save failed: ",
    "导入失败：": "Import failed: ",
    "导出失败：": "Export failed: ",
    "请先选择要编辑的指令": "Please select a command to edit first",
    "确定要删除选中的 ": "Delete the selected ",
    " 条指令吗？": " command(s)?",
    " 条规则吗？": " rule(s)?",
    "成功导入 ": "Imported ",
    "成功导出 ": "Exported ",
    " 条指令": " command(s)",
    " 条规则": " rule(s)",
    "请至少选择一条指令": "Please select at least one command",
    "数据已保存到 ": "Data saved to ",
    "请修正以下单元后再保存：\n\n": "Please fix the following units before saving:\n\n",
    # 指令编辑对话框
    "指令名称:": "Command Name:",
    "指令内容:": "Command Content:",
    "发送格式:": "Send Format:",
    "默认选中": "Selected by default",
    "保存接收数据": "Save Received Data",
    "添加规则": "Add Rule",
    "编辑规则": "Edit Rule",
    "发送帧配置": "Send Frame Configuration",
    "发送帧单元配置": "Send Frame Unit Configuration",
    "添加帧单元": "Add Frame Unit",
    "生成指令失败：": "Failed to generate command: ",
}


def tr(s):
    """根据当前语言返回翻译文本，未收录时返回原文。"""
    if CURRENT_LANG == 'en':
        return EN_TRANSLATIONS.get(s, s)
    return s


def set_language(lang):
    global CURRENT_LANG
    CURRENT_LANG = lang


class FlowLayout(QLayout):
    """流式布局：子控件按行排列，空间不足时自动换行到下一行"""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self._items = []

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(),
                      margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        if spacing < 0:
            spacing = 5
        for item in self._items:
            next_x = x + item.sizeHint().width() + spacing
            if next_x - spacing > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + spacing
                next_x = x + item.sizeHint().width() + spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()


class PortComboBox(QComboBox):
    """端口下拉框：点击展开（showPopup）时发出 about_to_popup 信号，
    用于在弹出列表前自动重新扫描串口，省去独立的刷新按钮。"""
    about_to_popup = pyqtSignal()

    def showPopup(self):
        self.about_to_popup.emit()
        super().showPopup()


class TitledActionGroup(QGroupBox):
    """标题行右侧可放置操作按钮的分组框。

    通过 add_title_action() 加入的按钮不作为内容参与布局，而是作为浮动
    子控件定位在分组标题同一行的最右端，从而无需为其额外占用一整行。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._title_actions = []

    def add_title_action(self, widget):
        widget.setParent(self)
        self._title_actions.append(widget)
        widget.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._title_actions:
            return
        margin = 8
        gap = 2
        h = 20
        y = max(0, (self.fontMetrics().height() - h) // 2)
        x = self.width() - margin
        for w in reversed(self._title_actions):
            w.setFixedHeight(h)
            w.adjustSize()
            width = max(w.sizeHint().width(), w.width())
            x -= width
            w.setGeometry(x, y, width, h)
            x -= gap


class ReceiveThread(QThread):
    """串口接收线程"""
    data_received = pyqtSignal(bytes)
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True
    
    def run(self):
        print("[DEBUG] 接收线程启动")
        while self.running and self.serial_port.is_open:
            try:
                n = self.serial_port.in_waiting
                if n > 0:
                    # 有数据立即读取，不再固定等待 10ms 合大包
                    # 更多字节会通过下一次循环 (msleep 1ms 后) 继续追加，
                    # 并由 on_data_received 中的 auto_reply_buffer 做完整帧拼装
                    data = self.serial_port.read(n)
                    if isinstance(data, (bytes, bytearray)):
                        self.data_received.emit(bytes(data))
                else:
                    # 空闲时短暂让出 CPU；1ms 足够快且开销可忽略
                    self.msleep(1)
            except Exception as e:
                print(f"[DEBUG] 接收线程异常: {e}")
                break
    
    def stop(self):
        print("[DEBUG] 接收线程停止")
        self.running = False
        self.wait()


class UartAssistantWindow(QMainWindow):
    """主窗口类"""

    # 失配判定使用的「帧引导前缀」最大字节数。
    # 取每条规则首个 fixed 单元的前若干字节（而非整个单元）作为帧头定位键：
    # 首固定单元里可能含有随帧变化的字段（如 AT+RECV 的长度位 64/69），
    # 用完整单元会把「同类但该字段不同」的真失配帧漏定位；有界引导前缀只用于
    # 在缓冲中找到该协议数据帧的起点，再按匹配帧配置「总长度」做收齐判定。
    _MISMATCH_PREFIX_MAXLEN = 8

    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_open = False
        self.receive_thread = None
        self.receive_count = 0
        self.receive_packet_count = 0
        self.send_count = 0
        self.send_packet_count = 0
        # 自动应答「缓冲区超时（100ms 静默期内未匹配任何规则）」次数统计。
        # 每次超时意味着一帧疑似失配数据被丢弃，仅用于排查，不参与任何收发逻辑、不持久化。
        self.auto_reply_timeout_count = 0
        self.hex_mode = False
        self.show_timestamp = True
        self.batch_sending = False
        self.batch_timer = None
        self.batch_count = 0
        self.batch_total = 0
        self.auto_reply_enabled = False
        # 失配统计口径：True=精确判定（找到规则帧头且收满匹配帧总长仍未命中才计失配，
        # 排除 OK/+RECV:ERROR 等无关回应与分片截断）；False=宽松判定（缓冲超时未命中即计）。
        # 仅影响「应答失配」计数，不影响应答命中（命中始终全量滑动匹配）。默认 True。
        self.auto_reply_head_match = True
        self.reply_rules = []
        # 自动应答规则命中次数计数器：{规则标识: 已命中次数}
        # 作为应答帧「递增值」单元的 iteration（首次命中为 0，即取起始值），仅运行时有效不持久化。
        # 由 _precompile_rules() 在规则集合变动时裁剪失效 key，避免长期运行内存增长。
        self._reply_increment_counters = {}
        # 已启用规则的「失配判定规格」列表：每项 dict(head=帧引导前缀或 None, total_len=匹配帧总长度)。
        # head 取每条规则首个 fixed 单元前 _MISMATCH_PREFIX_MAXLEN 字节（避开尾部随帧变化的字段），
        # 仅用于在缓冲中定位该协议数据帧的起点；首单元非 fixed 时 head=None（只能从缓冲起点算）。
        # total_len 为匹配帧各单元长度之和（与 match_frame 的最小匹配长度同口径）。
        # 缓冲超时丢弃时，从定位到的帧头起收满 total_len 字节却仍未命中，才计「真正失配」；
        # 未收满 total_len 视为不完整帧，不含任何帧头的无关数据（如模组回应 OK/+RECV:ERROR）静默丢弃，均不计失配。
        # 由 _precompile_rules() 在规则变动后重建。
        self._rules_mismatch_specs = []
        self.quick_commands = []
        self.send_history = []
        self.start_time = None
        self.last_receive_count = 0
        self.speed_timer = QTimer()
        self.show_send_data = True
        
        # 接收显示缓冲区（静默期分帧 + 双兜底）：
        # - 每次收到新字节，重置静默计时器 buffer_timeout；静默期无新数据到达才 flush（保证一帧一行）
        # - 兜底1：缓冲达 buffer_flush_threshold 立即 flush（避免超大帧一直不 flush）
        # - 兜底2：首字节到达后累计等待超过 buffer_max_wait_ms 立即 flush（避免慢速数据流永远等）
        self.receive_buffer = bytearray()
        self.buffer_timer = QTimer()
        self.buffer_timer.timeout.connect(self.flush_buffer)
        self.buffer_timer.setSingleShot(True)
        self.buffer_timeout = 33            # 静默期长度：33ms（≈30 FPS）无新字节即视为一帧结束
        self.buffer_flush_threshold = 4096  # 缓冲区超过 4KB 立即 flush，避免一次 insert 过大导致 UI 卡顿
        self.buffer_max_wait_ms = 200       # 首字节到达后最长等待时间兜底（ms）
        self._buffer_first_byte_ms = 0      # 当前缓冲首字节到达的 monotonic 毫秒时间戳（0 表示无数据）
        
        # 自动应答接收缓冲区
        self.auto_reply_buffer = bytearray()
        self.auto_reply_buffer_timer = QTimer()
        self.auto_reply_buffer_timer.timeout.connect(self.flush_auto_reply_buffer)
        self.auto_reply_buffer_timer.setSingleShot(True)
        self.auto_reply_buffer_timeout = 100  # 自动应答缓冲区超时时间100ms
        self.auto_reply_max_buffer_size = 1024  # 自动应答缓冲区最大1KB
        
        # 行状态跟踪
        self.current_line_has_timestamp = False
        
        # 接收显示区最大缓存（1MB）
        self.MAX_RECEIVE_DISPLAY_SIZE = 1024 * 1024  # 1MB
        self.receive_display_size = 0  # 跟踪显示区内容大小
        
        # 日志相关配置
        self.save_receive_log = True
        # 系统日志（控制台/调试日志）默认不保存，仅在齿轮菜单的排查后门中手动开启
        self.save_console_log = False
        self.log_save_path = ''
        self.receive_log_file = None
        self.receive_log_filename = None
        self.console_log_file = None
        self.console_log_filename = None
        self.use_custom_log_name = False
        self.custom_log_name = ''
        
        # 国际化：需要在语言切换时更新文本的控件登记表
        self._i18n_widgets = []
        # 提前读取语言设置，使界面首次构建即按所选语言
        try:
            _s = QSettings("UartTool", "UartAssistant")
            set_language(_s.value("language", "zh", type=str))
        except Exception:
            pass
        
        print("[DEBUG] 程序初始化完成")
        print(f"[DEBUG] show_send_data = {self.show_send_data}")
        
        self.init_ui()
        self.load_config()
        self.load_rules()
        self.load_batch_commands()
        self.load_quick_commands()
        self.setup_shortcuts()
        self.start_speed_timer()

        # 系统（控制台）日志默认关闭，仅当用户在齿轮菜单排查后门中开启后，启动时才初始化
        if self.save_console_log:
            self.init_console_log_file()
    
    def init_log_file(self):
        """初始化日志文件"""
        try:
            # 确定日志目录位置
            import sys
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller打包环境
                # 获取可执行文件所在目录
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
                log_dir = os.path.join(exe_dir, 'log')
            else:
                # 正常Python环境
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
            os.makedirs(log_dir, exist_ok=True)
            
            # 生成日志文件名（时间精度到秒）
            self.log_filename = os.path.join(log_dir, f"uart_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            print(f"[DEBUG] 日志文件路径: {self.log_filename}")
            
            # 尝试打开日志文件
            self.log_file = open(self.log_filename, 'w', encoding='utf-8')
            print(f"[DEBUG] 日志文件打开成功")
            
            # 测试写入
            self.log_file.write("日志文件初始化成功\n")
            self.log_file.flush()
            print("[DEBUG] 测试写入成功")
        except Exception as e:
            print(f"[DEBUG] 日志文件初始化失败: {e}")
            import traceback
            traceback.print_exc()
            self.log_file = None
    
    def init_console_log_file(self):
        """初始化控制台（系统）日志文件

        幂等：若已在记录系统日志则不重复重定向，避免文件句柄泄漏与 stdout 嵌套包装。
        """
        # 已存在有效日志句柄，说明系统日志已开启，直接返回
        if getattr(self, 'console_log_file', None) is not None:
            return
        try:
            # 确定日志目录位置
            log_dir = self.log_save_path or self.get_default_log_dir()
            os.makedirs(log_dir, exist_ok=True)
            
            # 生成控制台日志文件名（时间精度到秒）
            self.console_log_filename = os.path.join(log_dir, f"console_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            print(f"[DEBUG] 控制台日志文件路径: {self.console_log_filename}")
            
            # 尝试打开控制台日志文件
            self.console_log_file = open(self.console_log_filename, 'w', encoding='utf-8')
            print(f"[DEBUG] 控制台日志文件打开成功")
            
            # 测试写入
            self.console_log_file.write("控制台日志文件初始化成功\n")
            self.console_log_file.flush()
            print("[DEBUG] 控制台日志测试写入成功")
            
            # 重定向标准输出和标准错误到控制台日志文件
            import sys
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr
            
            class ConsoleLogger:
                def __init__(self, console_log_file, original_stdout):
                    self.console_log_file = console_log_file
                    self.original_stdout = original_stdout
                
                def write(self, text):
                    if self.console_log_file:
                        try:
                            self.console_log_file.write(text)
                            self.console_log_file.flush()
                        except:
                            pass
                    if self.original_stdout:
                        try:
                            self.original_stdout.write(text)
                        except:
                            pass
                
                def flush(self):
                    if self.console_log_file:
                        try:
                            self.console_log_file.flush()
                        except:
                            pass
                    if self.original_stdout:
                        try:
                            self.original_stdout.flush()
                        except:
                            pass
            
            sys.stdout = ConsoleLogger(self.console_log_file, self.original_stdout)
            sys.stderr = ConsoleLogger(self.console_log_file, self.original_stderr)
            
        except Exception as e:
            print(f"[DEBUG] 控制台日志文件初始化失败: {e}")
            import traceback
            traceback.print_exc()
            self.console_log_file = None
    
    def close_console_log_file(self):
        """关闭控制台（系统）日志文件并恢复标准输出/标准错误"""
        # 先取出并关闭日志句柄（关闭前不再向其写入，避免把关闭信息写进日志）
        f = getattr(self, 'console_log_file', None)
        if f:
            try:
                f.close()
            except Exception as e:
                print(f"[DEBUG] 关闭系统日志文件失败: {e}")
            self.console_log_file = None

        # 恢复标准输出和标准错误（恢复目标是开启前捕获的、None 安全的原始流）
        if hasattr(self, 'original_stdout') and hasattr(self, 'original_stderr'):
            import sys
            try:
                sys.stdout = self.original_stdout
                sys.stderr = self.original_stderr
            except Exception as e:
                print(f"[DEBUG] 恢复标准输出和标准错误失败: {e}")
        if f:
            print("[DEBUG] 系统日志已关闭")
    
    def close_log_file(self):
        """关闭所有日志文件"""
        # 关闭接收日志文件
        self.close_receive_log_file()
        # 关闭控制台日志文件
        self.close_console_log_file()

    def on_toggle_console_log(self, checked):
        """齿轮菜单排查后门：开启/关闭系统（控制台）日志。

        开启后立即初始化系统日志并持久化保存到配置；关闭则停止记录。
        该选项默认关闭，仅供开发/技术支持排查问题时使用。
        """
        from PyQt5.QtWidgets import QMessageBox
        if checked:
            self.save_console_log = True
            self.save_config()
            self.init_console_log_file()
            # 初始化成功后 console_log_file 非空；据此给出真实落盘路径
            if getattr(self, 'console_log_file', None):
                log_dir = os.path.dirname(self.console_log_filename)
                QMessageBox.information(
                    self, self._tr("系统日志"),
                    self._tr("系统日志已开启，之后的运行信息将写入：") + "\n"
                    + log_dir + "\n\n" + self._tr("该设置已保存，重启程序后仍保持开启。"))
            else:
                QMessageBox.warning(
                    self, self._tr("系统日志"),
                    self._tr("系统日志开启失败，请检查日志保存路径是否可写。"))
                # 初始化失败：回滚勾选态与配置
                self.save_console_log = False
                self.save_config()
                if hasattr(self, 'action_console_log'):
                    self.action_console_log.blockSignals(True)
                    self.action_console_log.setChecked(False)
                    self.action_console_log.blockSignals(False)
        else:
            self.save_console_log = False
            self.save_config()
            self.close_console_log_file()
            QMessageBox.information(
                self, self._tr("系统日志"),
                self._tr("系统日志已关闭，重启程序后保持关闭。"))
    
    # ==================== 国际化辅助方法 ====================
    def _tr(self, s):
        """翻译快捷方式"""
        return tr(s)

    def _reg(self, setter_fn, text_key):
        """注册控件文本，切换语言时统一刷新。用法: self._reg(w.setText, "中文")"""
        self._i18n_widgets.append((setter_fn, text_key))
        setter_fn(self._tr(text_key))

    def _mklabel(self, text_key):
        """创建一个支持语言切换的 QLabel"""
        lbl = QLabel()
        self._reg(lbl.setText, text_key)
        return lbl

    def switch_language(self, lang):
        """切换界面语言并保存设置"""
        if lang == CURRENT_LANG:
            return
        set_language(lang)
        try:
            QSettings("UartTool", "UartAssistant").setValue("language", lang)
        except Exception:
            pass
        self.retranslate_ui()

    def retranslate_ui(self):
        """运行时切换：刷新所有已注册控件的文本"""
        for setter_fn, text_key in self._i18n_widgets:
            try:
                setter_fn(self._tr(text_key))
            except Exception:
                pass
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        # 标签页标题
        if hasattr(self, 'left_tabs'):
            self.left_tabs.setTabText(0, self._tr("批量发送"))
            self.left_tabs.setTabText(1, self._tr("单次发送"))
            self.left_tabs.setTabText(2, self._tr("自动应答"))
            if self.left_tabs.count() > 3:
                self.left_tabs.setTabText(3, self._tr("快捷指令"))
        # 表头
        if hasattr(self, 'commands_table'):
            self.commands_table.setHorizontalHeaderLabels(
                [self._tr("操作"), self._tr("选中"), self._tr("名称"),
                 self._tr("指令"), self._tr("格式")])
        if hasattr(self, 'rules_table'):
            self.rules_table.setHorizontalHeaderLabels(
                [self._tr("操作"), self._tr("启用"), self._tr("名称"),
                 self._tr("匹配条件"), self._tr("应答数据")])
        if hasattr(self, 'quick_commands_table'):
            self.quick_commands_table.setHorizontalHeaderLabels(
                [self._tr("操作"), self._tr("名称"), self._tr("指令"), self._tr("格式")])
            # 重新构建操作列按钮以刷新按钮文本
            self.refresh_quick_commands_table()
        # 连接状态 / 按钮
        if hasattr(self, 'open_close_btn'):
            self.open_close_btn.setText(self._tr("关闭串口") if self.is_open else self._tr("打开串口"))
        if hasattr(self, 'status_label'):
            self.status_label.setText(self._tr("● 已连接") if self.is_open else self._tr("● 未连接"))
        # 折叠箭头提示
        if hasattr(self, 'toggle_left_btn'):
            visible = self.left_widget.isVisible()
            self.toggle_left_btn.setToolTip(self._tr("隐藏左侧面板") if visible else self._tr("显示左侧面板"))
        # 带变量的标签
        if hasattr(self, 'send_stats_label'):
            self.update_send_stats()
        if hasattr(self, 'rules_count_label'):
            self.rules_count_label.setText(f"{self._tr('已配置 ')}{len(self.reply_rules)}{self._tr(' 条规则')}")
        if hasattr(self, 'version_label'):
            self.version_label.setText(f"{self._tr('版本: ')}v{APP_VERSION}")
        if hasattr(self, 'current_log_label'):
            self.update_current_log_label()
        if hasattr(self, 'temp_status_label'):
            self.update_status_bar()
        # 设置菜单
        if hasattr(self, 'gear_btn'):
            self.gear_btn.setToolTip(self._tr("设置"))
        if hasattr(self, 'language_menu'):
            self.language_menu.setTitle(self._tr("语言"))

    def init_ui(self):
        """初始化界面"""
        print("[DEBUG] 开始初始化界面")
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(420, 360)
        
        # 定位图标资源：兼容 PyInstaller (_MEIPASS)、Nuitka onefile (__compiled__)、以及直接源码运行
        icon_path = None
        candidates = []
        if hasattr(sys, '_MEIPASS'):
            candidates.append(os.path.join(sys._MEIPASS, 'icon.ico'))
        # Nuitka onefile: __compiled__.containing_dir 指向临时解压目录；也放 exe 同目录
        if '__compiled__' in globals() or hasattr(sys, 'frozen'):
            try:
                exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                candidates.append(os.path.join(exe_dir, 'icon.ico'))
            except Exception:
                pass
        # 源码运行或作为兜底
        candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico'))
        for p in candidates:
            if p and os.path.exists(p):
                icon_path = p
                break
        if icon_path:
            from PyQt5.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局：水平分割器（左栏 + 右栏）
        main_layout = QHBoxLayout(central_widget)
        
        # 左栏：批量发送、单次发送、自动应答（Tab 标签页形式）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 功能标签页：切换时高亮并填充整个左半部分
        self.left_tabs = QTabWidget()
        left_layout.addWidget(self.left_tabs)
        
        # 批量发送（标签页内容容器）
        batch_group = QWidget()
        batch_layout = QVBoxLayout(batch_group)
        
        enable_layout = QHBoxLayout()
        self.batch_enable_check = QCheckBox()
        self._reg(self.batch_enable_check.setText, "启用批量发送")
        self.batch_enable_check.toggled.connect(self.on_batch_enabled)
        enable_layout.addWidget(self.batch_enable_check)
        enable_layout.addStretch()
        batch_layout.addLayout(enable_layout)
        
        # 指令列表
        self.batch_commands = []
        
        commands_layout = QVBoxLayout()
        commands_group = QGroupBox()
        self._reg(commands_group.setTitle, "发送指令列表")
        commands_inner_layout = QVBoxLayout(commands_group)
        
        # 指令表格
        self.commands_table = QTableWidget()
        self.commands_table.setColumnCount(5)
        self.commands_table.setHorizontalHeaderLabels([self._tr("操作"), self._tr("选中"), self._tr("名称"), self._tr("指令"), self._tr("格式")])
        # 允许用户手动拖动列宽（Interactive）；指令列自适应填满剩余空间
        h_header = self.commands_table.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.Interactive)
        h_header.setSectionResizeMode(3, QHeaderView.Stretch)
        h_header.setStretchLastSection(False)
        # 允许用户手动拖动行高
        self.commands_table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.commands_table.setColumnWidth(0, 52)   # 操作：单个按钮，容纳2个汉字
        self.commands_table.setColumnWidth(1, 110)  # 选中：复选框 + 间隔标签
        self.commands_table.setColumnWidth(2, 100)  # 名称
        self.commands_table.setColumnWidth(4, 60)   # 格式
        # 允许右键菜单：上移/下移
        self.commands_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.commands_table.customContextMenuRequested.connect(self.on_batch_commands_context_menu)
        commands_inner_layout.addWidget(self.commands_table)
        
        # 按钮布局
        commands_buttons_layout = QHBoxLayout()
        add_cmd_btn = QPushButton()
        self._reg(add_cmd_btn.setText, "添加指令")
        add_cmd_btn.clicked.connect(self.add_batch_command)
        commands_buttons_layout.addWidget(add_cmd_btn)
        

        
        del_cmd_btn = QPushButton()
        self._reg(del_cmd_btn.setText, "删除指令")
        del_cmd_btn.clicked.connect(self.delete_batch_command)
        commands_buttons_layout.addWidget(del_cmd_btn)
        
        import_cmd_btn = QPushButton()
        self._reg(import_cmd_btn.setText, "导入指令")
        import_cmd_btn.clicked.connect(self.import_batch_commands)
        commands_buttons_layout.addWidget(import_cmd_btn)
        
        export_cmd_btn = QPushButton()
        self._reg(export_cmd_btn.setText, "导出指令")
        export_cmd_btn.clicked.connect(self.export_batch_commands)
        commands_buttons_layout.addWidget(export_cmd_btn)
        
        commands_buttons_layout.addStretch()
        commands_inner_layout.addLayout(commands_buttons_layout)
        
        commands_layout.addWidget(commands_group)
        batch_layout.addLayout(commands_layout)
        
        settings_layout = QHBoxLayout()
        # 全部固定间隔开关：勾选后所有指令按 batch_interval_spin 间隔轮询，忽略单条 interval
        # 未勾选时，若单条指令配置了自定义 interval 则用它；否则等待 0ms 立即发下一条
        self.batch_fixed_interval_check = QCheckBox()
        self._reg(self.batch_fixed_interval_check.setText, "全部固定间隔")
        self.batch_fixed_interval_check.setChecked(True)
        self.batch_fixed_interval_check.toggled.connect(self.on_batch_fixed_interval_toggled)
        settings_layout.addWidget(self.batch_fixed_interval_check)
        self.batch_interval_spin = QSpinBox()
        self.batch_interval_spin.setRange(1, 60000)
        self.batch_interval_spin.setValue(1000)
        self.batch_interval_spin.setSuffix(" ms")
        # 全局间隔数值变化时，若处于"全部固定间隔"模式则实时刷新表格中的显示
        self.batch_interval_spin.valueChanged.connect(self._on_batch_global_interval_changed)
        settings_layout.addWidget(self.batch_interval_spin)
        
        settings_layout.addWidget(self._mklabel("次数:"))
        self.batch_count_spin = QSpinBox()
        self.batch_count_spin.setRange(1, 99999)
        self.batch_count_spin.setValue(10)
        settings_layout.addWidget(self.batch_count_spin)
        
        self.batch_infinite_check = QCheckBox()
        self._reg(self.batch_infinite_check.setText, "无限循环")
        self.batch_infinite_check.toggled.connect(self.on_batch_infinite_toggled)
        settings_layout.addWidget(self.batch_infinite_check)
        settings_layout.addStretch()
        batch_layout.addLayout(settings_layout)
        
        control_layout = QHBoxLayout()
        self.batch_start_btn = QPushButton()
        self._reg(self.batch_start_btn.setText, "开始")
        self.batch_start_btn.clicked.connect(self.start_batch_send)
        self.batch_start_btn.setEnabled(False)
        control_layout.addWidget(self.batch_start_btn)
        
        self.batch_stop_btn = QPushButton()
        self._reg(self.batch_stop_btn.setText, "停止")
        self.batch_stop_btn.clicked.connect(self.stop_batch_send)
        self.batch_stop_btn.setEnabled(False)
        control_layout.addWidget(self.batch_stop_btn)
        
        self.batch_progress_label = QLabel("进度：0/0")
        control_layout.addWidget(self.batch_progress_label)
        control_layout.addStretch()
        batch_layout.addLayout(control_layout)
        
        self.left_tabs.addTab(batch_group, self._tr("批量发送"))
        
        # 单次发送（标签页内容容器）
        single_group = QWidget()
        single_layout = QVBoxLayout(single_group)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(self._mklabel("格式:"))
        
        self.send_text_radio = QCheckBox()
        self._reg(self.send_text_radio.setText, "文本")
        self.send_text_radio.setChecked(True)
        self.send_text_radio.toggled.connect(self.on_send_text_toggled)
        format_layout.addWidget(self.send_text_radio)
        
        self.send_hex_radio = QCheckBox("HEX")
        self.send_hex_radio.toggled.connect(self.on_send_hex_toggled)
        format_layout.addWidget(self.send_hex_radio)
        
        # 显示发送开关
        self.show_send_check = QCheckBox()
        self._reg(self.show_send_check.setText, "显示发送")
        self.show_send_check.setChecked(True)
        self.show_send_check.toggled.connect(lambda: setattr(self, 'show_send_data', self.show_send_check.isChecked()))
        format_layout.addWidget(self.show_send_check)
        
        format_layout.addStretch()
        single_layout.addLayout(format_layout)
        
        self.send_text = QTextEdit()
        self.send_text.setFont(QFont("Consolas", DEFAULT_FONT_SIZE))
        self.send_text.setMinimumHeight(100)
        self.send_text.textChanged.connect(self.update_send_stats)
        single_layout.addWidget(self.send_text, 1)
        
        btn_layout = QHBoxLayout()
        self.send_btn = QPushButton()
        self._reg(self.send_btn.setText, "发送")
        self.send_btn.clicked.connect(lambda: self.send_data())
        self.send_btn.setDefault(True)
        btn_layout.addWidget(self.send_btn)
        
        clear_send_btn = QPushButton()
        self._reg(clear_send_btn.setText, "清空")
        clear_send_btn.clicked.connect(self.send_text.clear)
        btn_layout.addWidget(clear_send_btn)
        
        self.send_stats_label = QLabel("长度：0 字节")
        btn_layout.addWidget(self.send_stats_label)
        btn_layout.addStretch()
        single_layout.addLayout(btn_layout)
        
        self.left_tabs.addTab(single_group, self._tr("单次发送"))
        
        # 自动应答（标签页内容容器）
        reply_group = QWidget()
        reply_layout = QVBoxLayout(reply_group)
        
        enable_layout = QHBoxLayout()
        self.auto_reply_check = QCheckBox()
        self._reg(self.auto_reply_check.setText, "启用自动应答")
        self.auto_reply_check.toggled.connect(self.on_auto_reply_toggled)
        enable_layout.addWidget(self.auto_reply_check)
        # 失配统计口径开关：勾选=按帧头+匹配帧总长精确判定（默认）；不勾选=超时未命中即计。
        # 只影响「应答失配」计数，不影响应答命中行为。
        self.head_match_check = QCheckBox()
        self._reg(self.head_match_check.setText, "失配按帧头判定")
        self.head_match_check.setChecked(True)
        self.head_match_check.setToolTip(self._tr(
            "勾选：仅当收到规则帧头且收满配置总长却未命中时才计失配（排除 OK/ERROR 等回应与不完整帧）\n"
            "不勾选：接收缓冲超时未命中即计失配（适合无固定帧头的协议或宽松排查）"))
        self.head_match_check.toggled.connect(self.on_head_match_toggled)
        enable_layout.addWidget(self.head_match_check)
        enable_layout.addStretch()
        reply_layout.addLayout(enable_layout)
        
        # 规则列表
        rules_table_group = QGroupBox()
        self._reg(rules_table_group.setTitle, "规则列表")
        rules_table_layout = QVBoxLayout(rules_table_group)
        
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels([self._tr("操作"), self._tr("启用"), self._tr("名称"), self._tr("匹配条件"), self._tr("应答数据")])
        # 允许用户手动拖动列宽/行高；匹配条件、应答数据两列均分填满剩余空间
        h_header = self.rules_table.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.Interactive)
        h_header.setSectionResizeMode(3, QHeaderView.Stretch)
        h_header.setSectionResizeMode(4, QHeaderView.Stretch)
        h_header.setStretchLastSection(False)
        self.rules_table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.rules_table.setColumnWidth(0, 52)  # 操作：单个按钮，容纳2个汉字
        self.rules_table.setColumnWidth(1, 50)  # 启用
        self.rules_table.setColumnWidth(2, 90)  # 名称
        # 加高规则表，更完整显示规则列表内容
        self.rules_table.setMinimumHeight(220)
        # 允许右键菜单：上移/下移
        self.rules_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rules_table.customContextMenuRequested.connect(self.on_rules_context_menu)
        rules_table_layout.addWidget(self.rules_table)
        
        # 规则操作按钮
        rules_buttons_layout = QHBoxLayout()
        add_rule_btn = QPushButton()
        self._reg(add_rule_btn.setText, "添加规则")
        add_rule_btn.clicked.connect(self.add_rule)
        rules_buttons_layout.addWidget(add_rule_btn)
        
        del_rule_btn = QPushButton()
        self._reg(del_rule_btn.setText, "删除规则")
        del_rule_btn.clicked.connect(self.delete_rule)
        rules_buttons_layout.addWidget(del_rule_btn)
        
        import_rule_btn = QPushButton()
        self._reg(import_rule_btn.setText, "导入规则")
        import_rule_btn.clicked.connect(self.import_rules)
        rules_buttons_layout.addWidget(import_rule_btn)
        
        export_rule_btn = QPushButton()
        self._reg(export_rule_btn.setText, "导出规则")
        export_rule_btn.clicked.connect(self.export_rules)
        rules_buttons_layout.addWidget(export_rule_btn)
        
        rules_buttons_layout.addStretch()
        rules_table_layout.addLayout(rules_buttons_layout)
        
        reply_layout.addWidget(rules_table_group)
        
        self.rules_count_label = QLabel("已配置 0 条规则")
        reply_layout.addWidget(self.rules_count_label)
        
        self.left_tabs.addTab(reply_group, self._tr("自动应答"))
        
        # 快捷指令（标签页内容容器）
        quick_group = QWidget()
        quick_layout = QVBoxLayout(quick_group)
        
        quick_table_group = QGroupBox()
        self._reg(quick_table_group.setTitle, "发送指令列表")
        quick_table_layout = QVBoxLayout(quick_table_group)
        
        self.quick_commands_table = QTableWidget()
        self.quick_commands_table.setColumnCount(4)
        self.quick_commands_table.setHorizontalHeaderLabels(
            [self._tr("操作"), self._tr("名称"), self._tr("指令"), self._tr("格式")])
        # 允许用户手动拖动列宽/行高；指令列自适应填满剩余空间
        h_header = self.quick_commands_table.horizontalHeader()
        h_header.setSectionResizeMode(QHeaderView.Interactive)
        h_header.setSectionResizeMode(2, QHeaderView.Stretch)
        h_header.setStretchLastSection(False)
        self.quick_commands_table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.quick_commands_table.setColumnWidth(0, 108)  # 操作：编辑+发送两个按钮
        self.quick_commands_table.setColumnWidth(1, 100)  # 名称
        self.quick_commands_table.setColumnWidth(3, 60)   # 格式
        self.quick_commands_table.setMinimumHeight(220)
        # 允许右键菜单：上移/下移
        self.quick_commands_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.quick_commands_table.customContextMenuRequested.connect(self.on_quick_commands_context_menu)
        quick_table_layout.addWidget(self.quick_commands_table)
        
        quick_buttons_layout = QHBoxLayout()
        add_quick_btn = QPushButton()
        self._reg(add_quick_btn.setText, "添加指令")
        add_quick_btn.clicked.connect(self.add_quick_command)
        quick_buttons_layout.addWidget(add_quick_btn)
        
        del_quick_btn = QPushButton()
        self._reg(del_quick_btn.setText, "删除指令")
        del_quick_btn.clicked.connect(self.delete_quick_command)
        quick_buttons_layout.addWidget(del_quick_btn)
        
        import_quick_btn = QPushButton()
        self._reg(import_quick_btn.setText, "导入指令")
        import_quick_btn.clicked.connect(self.import_quick_commands)
        quick_buttons_layout.addWidget(import_quick_btn)
        
        export_quick_btn = QPushButton()
        self._reg(export_quick_btn.setText, "导出指令")
        export_quick_btn.clicked.connect(self.export_quick_commands)
        quick_buttons_layout.addWidget(export_quick_btn)
        
        clear_quick_btn = QPushButton()
        self._reg(clear_quick_btn.setText, "清空指令")
        clear_quick_btn.clicked.connect(self.clear_quick_commands)
        quick_buttons_layout.addWidget(clear_quick_btn)
        
        quick_buttons_layout.addStretch()
        quick_table_layout.addLayout(quick_buttons_layout)
        
        quick_layout.addWidget(quick_table_group)
        self.left_tabs.addTab(quick_group, self._tr("快捷指令"))
        # 三个功能以标签页切换，单页内容填充整个左半部分
        
        # 右栏：仅显示区
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 串口设置区（放在顶部）
        self.create_serial_settings(right_layout)
        
        # 接收窗口（显示区，占据最大空间）
        receive_panel = self.create_receive_panel()
        right_layout.addWidget(receive_panel, 1)  # 接收窗口占主要空间
        
        # 保存左栏引用，供折叠/展开使用
        self.left_widget = left_widget

        # 左右栏之间的折叠/展开箭头控件（短竖条，垂直居中）
        self.toggle_left_btn = QPushButton("◀")
        self.toggle_left_btn.setFixedWidth(14)
        self.toggle_left_btn.setFixedHeight(60)
        self.toggle_left_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.toggle_left_btn.setToolTip(self._tr("隐藏左侧面板"))
        self.toggle_left_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_left_btn.setStyleSheet(
            "QPushButton { border: none; background: #e0e0e0; color: #666; border-radius: 4px; }"
            "QPushButton:hover { background: #c8c8c8; color: #000; }"
        )
        self.toggle_left_btn.clicked.connect(self.toggle_left_panel)

        # 将折叠按钮包进一个垂直居中的窄容器，放在左右面板之间
        toggle_container = QWidget()
        toggle_container.setFixedWidth(16)
        toggle_v = QVBoxLayout(toggle_container)
        toggle_v.setContentsMargins(1, 0, 1, 0)
        toggle_v.addStretch()
        toggle_v.addWidget(self.toggle_left_btn)
        toggle_v.addStretch()

        # 设置布局比例，左栏标签页适当加宽以完整显示指令内容
        # 使用 QSplitter 允许用户手动拖动左右分栏边界
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(toggle_container)
        main_splitter.addWidget(right_widget)
        # 中间的折叠按钮容器不可拉伸、不作为可拖动分栏
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 0)
        main_splitter.setStretchFactor(2, 5)
        main_splitter.handle(1).setEnabled(False)
        main_splitter.setSizes([320, 16, 800])
        # 保存分割器引用，供折叠按钮使用
        self.main_splitter = main_splitter
        main_layout.addWidget(main_splitter, 1)
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 创建日志控制区域
        self.create_log_control_panel()
        
        # 版本号标签
        self.version_label = QLabel(f"{self._tr('版本: ')}v{APP_VERSION}")
        self.statusBar.addPermanentWidget(self.version_label)
        
        # 帮助(?)与设置(⚙)按钮在「串口设置」分组标题行右侧创建（见 create_serial_settings），
        # 不再占用菜单栏，从而省下菜单栏那一行的高度

        self.update_status_bar()
        print("[DEBUG] 界面初始化完成")
    
    def create_settings_menu(self):
        """创建齿轮设置按钮 + 帮助按钮（含语言切换子菜单）。

        不再占用菜单栏，按钮返回后由「串口设置」分组标题行右侧挂载，节省一行高度。
        """
        from PyQt5.QtWidgets import QToolButton, QMenu, QActionGroup

        # 帮助按钮 (?)
        help_btn = QToolButton()
        help_btn.setText("?")
        help_btn.setToolTip(self._tr("使用说明"))
        help_btn.setAutoRaise(True)
        help_btn.setStyleSheet("QToolButton { font-size: 14px; font-weight: bold; border: none; padding: 0 4px; }")
        help_btn.clicked.connect(self.open_help_dialog)
        self.help_btn = help_btn

        gear_btn = QToolButton()
        gear_btn.setText("\u2699")  # ⚙ 齿轮符号
        gear_btn.setToolTip(self._tr("设置"))
        gear_btn.setPopupMode(QToolButton.InstantPopup)
        gear_btn.setAutoRaise(True)
        gear_btn.setStyleSheet("QToolButton { font-size: 14px; border: none; padding: 0 4px; }"
                               "QToolButton::menu-indicator { image: none; }")

        settings_menu = QMenu(gear_btn)
        self.settings_menu = settings_menu

        # 语言子菜单
        self.language_menu = settings_menu.addMenu(self._tr("语言"))
        lang_group = QActionGroup(self)
        lang_group.setExclusive(True)

        self.action_lang_zh = self.language_menu.addAction("中文")
        self.action_lang_zh.setCheckable(True)
        self.action_lang_zh.triggered.connect(lambda: self.switch_language('zh'))
        lang_group.addAction(self.action_lang_zh)

        self.action_lang_en = self.language_menu.addAction("English")
        self.action_lang_en.setCheckable(True)
        self.action_lang_en.triggered.connect(lambda: self.switch_language('en'))
        lang_group.addAction(self.action_lang_en)

        self.action_lang_zh.setChecked(CURRENT_LANG == 'zh')
        self.action_lang_en.setChecked(CURRENT_LANG == 'en')

        # 分隔线
        settings_menu.addSeparator()

        # 换行间隔设置：控制接收显示静默期（越大越倾向合并成一行；越小越及时刷新）
        self.action_display_settings = settings_menu.addAction(self._tr("换行间隔..."))
        self.action_display_settings.triggered.connect(self.open_display_settings_dialog)

        # 分隔线 + 系统日志排查后门（默认关闭，仅排查问题时手动开启；开启后持久化，重启生效）
        settings_menu.addSeparator()
        self.action_console_log = settings_menu.addAction(self._tr("系统日志(仅排查问题用)"))
        self.action_console_log.setCheckable(True)
        # 初始勾选态与配置一致（UI 在 load_config 之后创建）
        self.action_console_log.setChecked(bool(getattr(self, 'save_console_log', False)))
        self.action_console_log.triggered.connect(self.on_toggle_console_log)

        gear_btn.setMenu(settings_menu)
        self.gear_btn = gear_btn
        return help_btn, gear_btn
    
    def open_help_dialog(self):
        """打开使用说明对话框"""
        dlg = HelpDialog(self)
        dlg.exec_()
    
    def open_display_settings_dialog(self):
        """打开"显示设置"对话框：修改接收显示的换行间隔（静默期，ms）"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                     QSpinBox, QPushButton, QDialogButtonBox)
        dlg = QDialog(self)
        dlg.setWindowTitle(self._tr("显示设置"))
        dlg.setMinimumWidth(360)
        layout = QVBoxLayout(dlg)
        
        # 说明
        desc = QLabel(self._tr(
            "接收显示换行间隔：\n"
            "在收到最后一个字节后，静默超过此时间未再收到新数据，\n"
            "才把当前累积的数据显示为一行。\n"
            "值越大：更容易把一整帧数据合并到一行；\n"
            "值越小：接收显示更及时。"
        ))
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # 输入行
        row = QHBoxLayout()
        row.addWidget(QLabel(self._tr("换行间隔:")))
        spin = QSpinBox()
        spin.setRange(1, 10000)
        spin.setSuffix(" ms")
        spin.setValue(int(getattr(self, 'buffer_timeout', 33)))
        row.addWidget(spin)
        row.addStretch()
        # 恢复默认按钮
        reset_btn = QPushButton(self._tr("恢复默认(33 ms)"))
        reset_btn.clicked.connect(lambda: spin.setValue(33))
        row.addWidget(reset_btn)
        layout.addLayout(row)
        
        # 确定/取消
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        
        if dlg.exec_() == QDialog.Accepted:
            new_val = int(spin.value())
            self.buffer_timeout = new_val
            # 持久化
            try:
                settings = QSettings("UartTool", "UartAssistant")
                settings.setValue("buffer_timeout", new_val)
            except Exception as e:
                print(f"[ERROR] 保存换行间隔失败: {e}")
    
    def create_log_control_panel(self):
        """创建日志控制面板（精简为一个按钮 + 当前日志标签）"""
        from PyQt5.QtWidgets import QHBoxLayout, QPushButton

        log_widget = QWidget()
        log_layout = QHBoxLayout(log_widget)
        log_layout.setContentsMargins(5, 2, 5, 2)
        log_layout.setSpacing(10)

        # 保存日志按钮：点击弹出配置对话框
        self.log_settings_btn = QPushButton()
        self._reg(self.log_settings_btn.setText, "保存日志")
        self.log_settings_btn.setMaximumWidth(90)
        self.log_settings_btn.clicked.connect(self.open_log_settings_dialog)
        log_layout.addWidget(self.log_settings_btn)

        # 当前日志状态标签
        self.current_log_label = QLabel("日志未开启")
        log_layout.addWidget(self.current_log_label)

        log_layout.addStretch()

        # 将日志控件添加到状态栏
        self.statusBar.addWidget(log_widget, 1)

        # 添加临时状态消息标签（在右侧）
        self.temp_status_label = QLabel(self._tr("就绪"))
        self.statusBar.addPermanentWidget(self.temp_status_label, 0)

    def open_log_settings_dialog(self):
        """打开日志设置对话框，运行时可修改保存开关、路径和文件名"""
        dialog = LogSettingsDialog(self)
        if dialog.exec_():
            cfg = dialog.get_config()
            old_receive = self.save_receive_log
            self.save_receive_log = cfg['save_receive_log']
            self.save_console_log = cfg['save_console_log']
            self.log_save_path = cfg['log_save_path']
            self.use_custom_log_name = cfg['use_custom_log_name']
            self.custom_log_name = cfg['custom_log_name']

            # 应用接收日志设置（运行时修改：重建文件以应用新路径/文件名）
            if self.save_receive_log:
                if self.is_open:
                    self.close_receive_log_file()
                    self.init_receive_log_file()
            else:
                self.close_receive_log_file()

            # 应用控制台日志设置（系统日志后门已开启时，先关后开以应用新的保存路径；
            # 默认关闭时此处为空操作）
            if self.save_console_log:
                self.close_console_log_file()
                self.init_console_log_file()
            else:
                self.close_console_log_file()

            self.update_current_log_label()
            self.save_config()

    def browse_log_path(self):
        """浏览选择日志保存路径"""
        path = QFileDialog.getExistingDirectory(self, "选择日志保存目录", self.log_save_path)
        return path
    def get_default_log_dir(self):
        """获取默认日志目录"""
        if hasattr(sys, '_MEIPASS'):
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            return os.path.join(exe_dir, 'log')
        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
    
    def init_receive_log_file(self):
        """初始化接收日志文件

        注意：这里只确定文件路径并创建一个空文件，不长期持有文件句柄，
        这样在串口打开期间日志文件也可被外部随时删除/重命名。
        实际写入见 write_receive_log()，每次短开追加，文件被删后会自动重建。
        """
        if not self.save_receive_log or not self.is_open:
            return

        try:
            log_dir = self.log_save_path or self.get_default_log_dir()
            os.makedirs(log_dir, exist_ok=True)

            if self.use_custom_log_name and self.custom_log_name:
                # 使用自定义文件名
                custom_name = self.custom_log_name
                # 确保扩展名是.log
                if not custom_name.lower().endswith('.log'):
                    custom_name += '.log'
                self.receive_log_filename = os.path.join(log_dir, custom_name)
            else:
                # 使用默认命名规则
                port = self.port_combo.currentText().replace(':', '').replace('\\', '').replace('/', '')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self.receive_log_filename = os.path.join(log_dir, f"{timestamp}_{port}.log")

            # 创建/清空日志文件后立即关闭，不占用句柄
            with open(self.receive_log_filename, 'w', encoding='utf-8'):
                pass

            self.update_current_log_label()
            print(f"[DEBUG] 接收日志文件已创建: {self.receive_log_filename}")
        except Exception as e:
            print(f"[DEBUG] 初始化接收日志文件失败: {e}")

    def write_receive_log(self, log_text):
        """短开文件句柄追加写入一行，写完立即关闭，避免长期占用导致无法删除。

        若日志文件已被外部删除（或重命名），则按原路径重新创建后继续写入；
        连续写入失败（如目录被删/磁盘不可用）时安静返回，不影响串口收发。
        """
        if not self.save_receive_log or not self.receive_log_filename:
            return
        try:
            # 文件已被删除时自动重建（目录可能也被一起删了，需一并补建）
            if not os.path.exists(self.receive_log_filename):
                os.makedirs(os.path.dirname(self.receive_log_filename), exist_ok=True)
            # 追加模式短开短关，句柄在 with 结束时释放
            with open(self.receive_log_filename, 'a', encoding='utf-8') as f:
                f.write(log_text + '\n')
        except Exception as e:
            print(f"[ERROR] 写入日志文件失败: {e}")

    def close_receive_log_file(self):
        """关闭接收日志（仅清理路径状态；无句柄需要关闭）"""
        if self.receive_log_filename:
            self.receive_log_file = None
            self.receive_log_filename = None
            self.update_current_log_label()
            print("[DEBUG] 接收日志已停止（文件句柄已释放）")
    
    def update_current_log_label(self):
        """更新当前日志文件标签"""
        if self.receive_log_filename and os.path.exists(self.receive_log_filename):
            filename = os.path.basename(self.receive_log_filename)
            try:
                size = os.path.getsize(self.receive_log_filename)
                if size >= 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                elif size >= 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size} B"
                self.current_log_label.setText(f"{self._tr('当前日志: ')}[{filename}] [{size_str}]")
            except:
                self.current_log_label.setText(f"{self._tr('当前日志: ')}[{filename}]")
        elif self.save_receive_log:
            self.current_log_label.setText(self._tr("日志已开启（等待打开串口写入）"))
        else:
            self.current_log_label.setText(self._tr("日志未开启"))
    
    def create_serial_settings(self, parent_layout):
        """创建串口设置区域"""
        settings_group = TitledActionGroup()
        self._reg(settings_group.setTitle, "串口设置")
        # 帮助(?)与设置(⚙)按钮挂到标题行最右端，不再单独占用菜单栏一行
        help_btn, gear_btn = self.create_settings_menu()
        settings_group.add_title_action(help_btn)
        settings_group.add_title_action(gear_btn)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setContentsMargins(5, 5, 5, 5)
        settings_layout.setSpacing(5)
        
        # 第一行：基本设置（使用流式布局，空间不足时自动换行）
        top_layout = FlowLayout(spacing=5)

        def make_field(label_text, widget):
            """将标签与控件组合成一个整体，便于换行时一起移动"""
            field = QWidget()
            field_layout = QHBoxLayout(field)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(3)
            field_layout.addWidget(self._mklabel(label_text))
            field_layout.addWidget(widget)
            return field

        self.port_combo = PortComboBox()
        self.port_combo.setMinimumWidth(80)
        self.port_combo.setMaximumHeight(25)
        self.refresh_ports()
        # 点击下拉框展开时自动重新扫描串口，替代独立的刷新按钮
        self.port_combo.about_to_popup.connect(self.refresh_ports)

        port_field = QWidget()
        port_layout = QHBoxLayout(port_field)
        port_layout.setContentsMargins(0, 0, 0, 0)
        port_layout.setSpacing(3)
        port_layout.addWidget(self._mklabel("端口:"))
        port_layout.addWidget(self.port_combo)
        top_layout.addWidget(port_field)

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.setEditable(True)
        self.baudrate_combo.setMaximumHeight(25)
        for br in BAUDRATES:
            self.baudrate_combo.addItem(str(br))
        self.baudrate_combo.setCurrentText(str(DEFAULT_BAUDRATE))
        top_layout.addWidget(make_field("波特率:", self.baudrate_combo))

        self.bytesize_combo = QComboBox()
        self.bytesize_combo.setMaximumHeight(25)
        for bs in BYTESIZES:
            self.bytesize_combo.addItem(str(bs))
        self.bytesize_combo.setCurrentText(str(DEFAULT_BYTESIZE))
        top_layout.addWidget(make_field("数据位:", self.bytesize_combo))

        self.stopbits_combo = QComboBox()
        self.stopbits_combo.setMaximumHeight(25)
        for sb in STOPBITS:
            self.stopbits_combo.addItem(str(sb))
        self.stopbits_combo.setCurrentText(str(DEFAULT_STOPBITS))
        top_layout.addWidget(make_field("停止位:", self.stopbits_combo))

        self.parity_combo = QComboBox()
        self.parity_combo.setMaximumHeight(25)
        for p in PARITIES:
            self.parity_combo.addItem(p)
        self.parity_combo.setCurrentText(PARITIES[0])
        top_layout.addWidget(make_field("校验位:", self.parity_combo))

        self.flowcontrol_combo = QComboBox()
        self.flowcontrol_combo.setMaximumHeight(25)
        for fc in FLOWCONTROLS:
            self.flowcontrol_combo.addItem(fc)
        self.flowcontrol_combo.setCurrentText(FLOWCONTROLS[0])
        top_layout.addWidget(make_field("流控制:", self.flowcontrol_combo))

        settings_layout.addLayout(top_layout)
        
        # 第二行：控制按钮、状态、显示选项、保存/清除（集中到同一行）
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(5)
        
        self.open_close_btn = QPushButton()
        self._reg(self.open_close_btn.setText, "打开串口")
        self.open_close_btn.setMaximumHeight(25)
        self.open_close_btn.setMinimumWidth(100)
        self.open_close_btn.clicked.connect(self.toggle_serial)
        bottom_layout.addWidget(self.open_close_btn)
        
        self.status_label = QLabel()
        self._reg(self.status_label.setText, "● 未连接")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        bottom_layout.addWidget(self.status_label)
        
        bottom_layout.addSpacing(15)
        
        # 显示选项：文本 / HEX / 时间戳
        bottom_layout.addWidget(self._mklabel("显示:"))
        self.receive_text_radio = QCheckBox()
        self._reg(self.receive_text_radio.setText, "文本")
        self.receive_text_radio.setChecked(True)
        self.receive_text_radio.toggled.connect(self.on_receive_text_toggled)
        bottom_layout.addWidget(self.receive_text_radio)
        
        self.receive_hex_radio = QCheckBox("HEX")
        self.receive_hex_radio.toggled.connect(self.on_receive_hex_toggled)
        bottom_layout.addWidget(self.receive_hex_radio)
        
        self.timestamp_check = QCheckBox()
        self._reg(self.timestamp_check.setText, "时间戳")
        self.timestamp_check.setChecked(self.show_timestamp)
        self.timestamp_check.toggled.connect(lambda: setattr(self, 'show_timestamp', self.timestamp_check.isChecked()))
        bottom_layout.addWidget(self.timestamp_check)
        
        # 自动换行：勾选后接收区按窗口宽度自适应换行
        self.wrap_check = QCheckBox()
        self._reg(self.wrap_check.setText, "自动换行")
        self.wrap_check.setChecked(False)
        self.wrap_check.toggled.connect(self.on_wrap_toggled)
        bottom_layout.addWidget(self.wrap_check)
        
        bottom_layout.addStretch()
        
        # 保存 / 清除 接收区
        save_btn = QPushButton()
        self._reg(save_btn.setText, "保存")
        save_btn.setMaximumHeight(25)
        save_btn.clicked.connect(self.save_receive_data)
        bottom_layout.addWidget(save_btn)
        
        clear_receive_btn = QPushButton()
        self._reg(clear_receive_btn.setText, "清除")
        clear_receive_btn.setMaximumHeight(25)
        clear_receive_btn.clicked.connect(self.clear_receive)
        bottom_layout.addWidget(clear_receive_btn)
        
        settings_layout.addLayout(bottom_layout)
        
        # 高度自适应：参数换行时设置区可自动增高
        settings_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        parent_layout.addWidget(settings_group)
    
    def create_receive_panel(self):
        """创建接收面板（仅文本显示区，最大化显示面积）"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)
        self.receive_text.setFont(QFont("Consolas", DEFAULT_FONT_SIZE))
        self.receive_text.setLineWrapMode(QTextEdit.NoWrap)  # 禁用自动换行
        layout.addWidget(self.receive_text)
        
        return widget
    
    def refresh_ports(self):
        print("[DEBUG] 刷新串口列表")
        # 记录当前选中项，刷新后尽量保留（点击下拉框自动刷新时不打断已选端口）
        prev_port = self.port_combo.currentText()
        self.port_combo.blockSignals(True)
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)
        restore_index = self.port_combo.findText(prev_port)
        if restore_index >= 0:
            self.port_combo.setCurrentIndex(restore_index)
        self.port_combo.blockSignals(False)
        print(f"[DEBUG] 找到串口: {[port.device for port in ports]}")
    
    def toggle_serial(self):
        print(f"[DEBUG] 切换串口状态，当前状态: {self.is_open}")
        if not self.is_open:
            self.open_serial()
        else:
            self.close_serial()
    
    def open_serial(self):
        print("[DEBUG] 尝试打开串口")
        try:
            port = self.port_combo.currentText()
            baudrate = int(self.baudrate_combo.currentText())
            bytesize = int(self.bytesize_combo.currentText())
            stopbits = float(self.stopbits_combo.currentText())
            parity_map = {'None': 'N', 'Odd': 'O', 'Even': 'E', 'Mark': 'M', 'Space': 'S'}
            parity = parity_map.get(self.parity_combo.currentText(), 'N')
            
            print(f"[DEBUG] 串口参数: port={port}, baudrate={baudrate}, bytesize={bytesize}, stopbits={stopbits}, parity={parity}")
            
            # 清空缓冲区
            self.receive_buffer.clear()
            self._buffer_first_byte_ms = 0
            self.auto_reply_buffer.clear()
            self.auto_reply_buffer_timer.stop()
            
            self.serial_port = serial.Serial(
                port=port, baudrate=baudrate, bytesize=bytesize,
                stopbits=stopbits, parity=parity, timeout=DEFAULT_TIMEOUT
            )
            
            self.is_open = True
            self.open_close_btn.setText(self._tr("关闭串口"))
            self.status_label.setText(self._tr("● 已连接"))
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            self.receive_thread = ReceiveThread(self.serial_port)
            self.receive_thread.data_received.connect(self.on_data_received)
            self.receive_thread.start()
            
            # 初始化接收日志文件
            self.init_receive_log_file()
            
            self.start_time = datetime.now()
            if hasattr(self, 'temp_status_label'):
                self.temp_status_label.setText(f"{self._tr('串口 ')}{port}{self._tr(' 已打开')}")
            print(f"[DEBUG] 串口 {port} 打开成功")
            
        except Exception as e:
            print(f"[DEBUG] 打开串口失败: {e}")
            QMessageBox.critical(self, self._tr("错误"), f"{self._tr('打开串口失败：')}{str(e)}")
            self.is_open = False
    
    def close_serial(self):
        print("[DEBUG] 关闭串口")
        
        # 关闭接收日志文件
        self.close_receive_log_file()
        
        if self.receive_thread:
            self.receive_thread.stop()
            self.receive_thread.wait()
        
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
        
        # 清空缓冲区
        self.receive_buffer.clear()
        self._buffer_first_byte_ms = 0
        self.auto_reply_buffer.clear()
        self.auto_reply_buffer_timer.stop()
        
        self.is_open = False
        self.open_close_btn.setText(self._tr("打开串口"))
        self.status_label.setText(self._tr("● 未连接"))
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        if hasattr(self, 'temp_status_label'):
            self.temp_status_label.setText(self._tr("串口已关闭"))
        print("[DEBUG] 串口已关闭")
    
    def on_data_received(self, data):
        """处理接收到的数据"""
        if not isinstance(data, bytes):
            return
        
        # 将数据添加到接收显示缓冲区
        self.receive_buffer.extend(data)
        self.receive_count += len(data)
        
        # 静默期分帧调度：
        # 1) 缓冲达阈值 → 立即 flush（避免一次 insert 过大数据导致 UI 卡顿）
        # 2) 首字节到达后累计等待超过 max_wait_ms → 立即 flush（慢速流兜底）
        # 3) 否则每次到数据都重置静默计时器，静默期结束（无新字节）才 flush
        #    → 一整帧数据(即使被驱动分多批)会聚合成一次显示，避免同一帧被分成多行
        import time as _time
        now_ms = int(_time.monotonic() * 1000)
        if not self._buffer_first_byte_ms:
            self._buffer_first_byte_ms = now_ms
        
        if len(self.receive_buffer) >= self.buffer_flush_threshold:
            self.buffer_timer.stop()
            self.flush_buffer()
        elif now_ms - self._buffer_first_byte_ms >= self.buffer_max_wait_ms:
            self.buffer_timer.stop()
            self.flush_buffer()
        else:
            # 重置静默计时器：只要还在陆续收到数据，就把 flush 推后
            self.buffer_timer.start(self.buffer_timeout)
        
        # 处理自动应答
        if self.auto_reply_enabled and self.reply_rules:
            # 将数据添加到自动应答缓冲区
            self.auto_reply_buffer.extend(data)
            
            # 限制自动应答缓冲区大小
            if len(self.auto_reply_buffer) > self.auto_reply_max_buffer_size:
                # 超出限制，从开头删除超出部分
                excess = len(self.auto_reply_buffer) - self.auto_reply_max_buffer_size
                self.auto_reply_buffer = self.auto_reply_buffer[excess:]
            
            # 对整个缓冲区进行匹配（首字节预索引快速过滤）
            buf_bytes = bytes(self.auto_reply_buffer)
            matched_rule = None
            matched_captures = {}
            candidate_rules = self._filter_candidate_rules(buf_bytes)
            for rule in candidate_rules:
                try:
                    match_frame = rule.get('match_frame', [])
                    fmt = rule.get('format', 'HEX')
                    is_match, captures = self.match_frame(buf_bytes, match_frame, fmt)
                    if is_match:
                        matched_rule = rule
                        matched_captures = captures
                        break
                except Exception as e:
                    print(f"[ERROR] 匹配规则异常: {e}")
                    continue
            
            if matched_rule:
                # 命中后立刻发送应答：应答延迟由每条应答帧自带的 delay_ms 通过 QTimer 控制
                # 显示刷新异步投递，避免阻塞发送路径
                QTimer.singleShot(0, self.flush_buffer)
                # 仅浅拷贝需要的字段，避免整规则 deepcopy 的额外开销
                responses_snapshot = self._get_rule_responses(matched_rule)
                rule_snapshot = {
                    'name': matched_rule.get('name'),
                    'format': matched_rule.get('format', 'HEX'),
                    'responses': responses_snapshot,
                }
                # 命中次数按原规则对象统计，供应答帧「递增值」单元计算当前值
                iteration = self._take_reply_iteration(matched_rule)
                self.send_reply(rule_snapshot, dict(matched_captures) if matched_captures else {}, iteration)
                # 匹配成功后清空缓冲区，避免重复匹配
                self.auto_reply_buffer.clear()
                self.auto_reply_buffer_timer.stop()
            else:
                # 没有匹配成功，重置超时定时器
                self.auto_reply_buffer_timer.start(self.auto_reply_buffer_timeout)
        
        # 不再直接显示，由 flush_buffer 处理
        # self.display_receive_data(data)
    
    # 预建的文本过滤映射表：删除所有 0-31 中除 \t \r \n 之外的控制字符 + DEL(127)
    # 用 str.translate() 在 C 层批量删除，比 Python 循环 isprintable() 快 30~50 倍
    _TEXT_STRIP_TABLE = dict.fromkeys(
        [c for c in list(range(0, 32)) + [127] if c not in (9, 10, 13)],
        None
    )

    def display_receive_data(self, data, direction='RX'):
        """显示接收数据"""
        if not isinstance(data, bytes) or len(data) == 0:
            return
        
        # 每次显示数据都在新行开始
        timestamp = ""
        if self.show_timestamp:
            timestamp = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
        
        if self.hex_mode:
            hex_str = data.hex(' ').upper()
            text = f"{timestamp}[{direction}] {hex_str}\n"
        else:
            text_str = data.decode('utf-8', errors='replace')
            # 快速过滤：删除除 \t \r \n 以外的控制字符（C 层实现，速度远快于 Python 循环）
            text_str = text_str.translate(self._TEXT_STRIP_TABLE)
            if '\n' in text_str:
                # 保留原有"每行都带 timestamp + [dir]"的显示风格
                lines = text_str.split('\n')
                text = ''.join(f"{timestamp}[{direction}] {line}\n" for line in lines)
            else:
                text = f"{timestamp}[{direction}] {text_str}\n"
        
        # 冻结重绘，把插入 + 裁剪 + 滚动条更新一起打包，只触发一次 repaint
        receive_text = self.receive_text
        receive_text.setUpdatesEnabled(False)
        try:
            scrollbar = receive_text.verticalScrollBar()
            at_bottom = scrollbar.value() >= scrollbar.maximum() - 4

            cursor = receive_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            
            # 简单的行数限制方案 - 不跟踪字节大小，只跟踪行数
            # 每次累计行数超过阈值就删除前面部分
            if not hasattr(self, 'receive_line_count'):
                self.receive_line_count = 0
            
            self.receive_line_count += text.count('\n')
            
            if self.receive_line_count > 2000:
                doc = receive_text.document()
                block_count = doc.blockCount()
                if block_count > 2000:
                    delete_count = block_count - 1500
                    if delete_count > 0:
                        del_cursor = receive_text.textCursor()
                        del_cursor.setPosition(0)
                        for _ in range(delete_count):
                            del_cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor)
                        del_cursor.removeSelectedText()
                        self.receive_line_count = 1500
                        # 若用户正在查看历史（不在底部），补偿滚动条位置，避免视图跳动
                        if not at_bottom:
                            line_height = receive_text.fontMetrics().lineSpacing()
                            new_val = scrollbar.value() - delete_count * line_height
                            scrollbar.setValue(max(0, new_val))
            
            # 仅当插入前位于底部时才自动滚到最新；否则保持当前查看位置
            if at_bottom:
                scrollbar.setValue(scrollbar.maximum())
        finally:
            receive_text.setUpdatesEnabled(True)
        
        # 将显示的内容写入接收日志文件（短开追加，不占用句柄，日志可随时删除）
        if self.save_receive_log and self.receive_log_filename:
            log_text = text.rstrip()
            if log_text:
                self.write_receive_log(log_text)
                # 延迟更新日志标签，避免频繁 UI 操作
                if not hasattr(self, 'log_label_update_count'):
                    self.log_label_update_count = 0
                self.log_label_update_count += 1
                if self.log_label_update_count >= 50:
                    self.update_current_log_label()
                    self.log_label_update_count = 0
    
    def flush_buffer(self):
        """刷新接收缓冲区，将数据一次性显示"""
        if len(self.receive_buffer) > 0:
            data_to_display = bytes(self.receive_buffer)
            # 每刷新一次缓冲区计为接收到一条数据
            self.receive_packet_count += 1
            self.current_line_has_timestamp = False  # 强制在新行显示
            self.display_receive_data(data_to_display, 'RX')
            # 清空缓冲区
            self.receive_buffer.clear()
        # 重置首字节时间戳，让下一帧重新计时
        self._buffer_first_byte_ms = 0
    
    @staticmethod
    def _format_hex_dump(data, max_bytes=512):
        """把字节缓冲格式化成 hex 转储文本（每行最多16字节：偏移 + HEX + ASCII），仅用于排查日志。

        超过 max_bytes 时只转储开头部分，避免异常长缓冲刷屏。
        """
        total = len(data)
        show = data[:max_bytes]
        lines = []
        for off in range(0, len(show), 16):
            chunk = show[off:off + 16]
            hex_part = " ".join(f"{b:02X}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            lines.append(f"    {off:04X}  {hex_part:<47}  {ascii_part}")
        text = "\n".join(lines)
        if total > len(show):
            text += f"\n    ... 共 {total} 字节，仅转储前 {len(show)} 字节"
        return text

    def _is_real_mismatch_buffer(self, buf_bytes):
        """判定一份「最终未命中任何规则」的超时缓冲是否为真正失配。

        依据失配统计口径开关 self.auto_reply_head_match：
        - 精确判定（True，默认）：对每条已启用规则，先用其有界帧引导前缀 head 在缓冲中
          定位该协议数据帧的起点（head=None 表示首单元非固定值，只能从缓冲起点算）；
          从帧头起可用字节数 >= 该规则匹配帧总长度 total_len，说明一整帧已收齐却仍未
          命中 → 真失配；帧头后不足 total_len 视为不完整帧，找不到任何帧头视为无关数据，
          均不计失配（如模组回应 OK/+RECV:ERROR、分片截断）。
        - 宽松判定（False）：不做帧头/长度过滤，只要有启用规则且缓冲非空、超时未命中即计
          失配。适合无固定帧头的协议或需要统计任何异常回应的排查场景（此时 OK/ERROR 等
          无关回应也会被计入，属预期行为）。
        """
        if not hasattr(self, '_rules_mismatch_specs'):
            self._precompile_rules()
        # 宽松模式：只要存在启用规则（规格非空），超时未命中即计失配
        if not getattr(self, 'auto_reply_head_match', True):
            return bool(self._rules_mismatch_specs)
        n = len(buf_bytes)
        for spec in self._rules_mismatch_specs:
            head = spec.get('head')
            total_len = spec.get('total_len', 0)
            if total_len <= 0:
                continue
            if head:
                idx = buf_bytes.find(head)
                if idx < 0:
                    continue  # 缓冲中没有该协议帧头
            else:
                idx = 0  # 帧头未知，只能从缓冲起点估算
            # 从帧头起到缓冲末尾的可用字节数
            if n - idx >= total_len:
                return True
            # 不足总长：可能是不完整帧，继续看其它规则（不据此计失配）
        return False

    def flush_auto_reply_buffer(self):
        """刷新自动应答缓冲区，超时后清空缓冲区。

        失配统计口径见 _is_real_mismatch_buffer()：仅当某规则的目标数据帧已按配置
        总长度收齐、却仍未命中时才计失配；不完整帧与完全无关数据静默清空、不计失配。
        """
        if len(self.auto_reply_buffer) > 0:
            buf_bytes = bytes(self.auto_reply_buffer)
            is_real_mismatch = self._is_real_mismatch_buffer(buf_bytes)
            if is_real_mismatch:
                self.auto_reply_timeout_count += 1
                print(f"[DEBUG] 自动应答缓冲区超时，清空缓冲区，长度: {len(buf_bytes)}，"
                      f"累计失配次数: {self.auto_reply_timeout_count}")
                print("[DEBUG] 失配缓冲转储(HEX/ASCII):\n"
                      + self._format_hex_dump(buf_bytes))
            else:
                print(f"[DEBUG] 自动应答缓冲区超时，丢弃不完整/无关数据（不计失配），长度: {len(buf_bytes)}")
            self.auto_reply_buffer.clear()
    
    def send_data(self, data=None, show_errors=True, _skip_stats=False):
        """发送数据"""
        if not self.is_open or not self.serial_port:
            if show_errors:
                QMessageBox.warning(self, self._tr("警告"), self._tr("串口未打开"))
            return False
        
        try:
            # 处理非预期的参数类型（如布尔值）
            if data is not None and not isinstance(data, bytes):
                data = None
            
            if data is None:
                input_text = self.send_text.toPlainText()
                
                if self.send_hex_radio.isChecked():
                    try:
                        data = bytes.fromhex(input_text.replace(' ', ''))
                    except Exception:
                        # HEX 解析失败：回退到文本模式（处理转义字符）
                        processed_text = input_text
                        processed_text = processed_text.replace('\\r', '\r')
                        processed_text = processed_text.replace('\\n', '\n')
                        processed_text = processed_text.replace('\\t', '\t')
                        processed_text = processed_text.replace('\\\\', '\\')
                        data = processed_text.encode('utf-8')
                else:
                    # 处理转义字符
                    processed_text = input_text
                    processed_text = processed_text.replace('\\r', '\r')
                    processed_text = processed_text.replace('\\n', '\n')
                    processed_text = processed_text.replace('\\t', '\t')
                    processed_text = processed_text.replace('\\\\', '\\')
                    data = processed_text.encode('utf-8')
            
            if isinstance(data, bytes) and len(data) > 0:
                # 写串口 -> 校验实际写入字节数，再更新统计（关键路径，最短完成）
                total = len(data)
                written = self.serial_port.write(data)
                # pyserial write 返回实际写入字节数；个别封装可能返回 None，则不据此判失败。
                # 仅当返回明确整数且小于应发长度时，记录「不完整写入」——纯排查：不补发、不重试、不改字节。
                if isinstance(written, int) and written < total:
                    print(f"[ERROR] 串口写入不完整: 应发 {total} 字节，实际仅写入 {written} 字节"
                          f"（未补发，本次发送判定失败）")
                    return False
                self.send_count += total
                self.send_packet_count += 1
                
                # 显示发送 & 更新输入框长度统计：非关键路径 -> 异步投递，避免阻塞当前 slot
                show_send = self.show_send_check.isChecked()
                def _post_send_ui(_d=data, _show=show_send, _skip=_skip_stats):
                    if _show:
                        self.display_receive_data(_d, 'TX')
                    if not _skip:
                        self.update_send_stats()
                QTimer.singleShot(0, _post_send_ui)
                return True
            else:
                return False
            
        except Exception as e:
            print(f"[ERROR] 发送失败: {e}")
            import traceback
            traceback.print_exc()
            if show_errors:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('发送失败：')}{str(e)}")
            return False
    
    def update_send_stats(self):
        text = self.send_text.toPlainText()
        if self.send_hex_radio.isChecked():
            try:
                byte_count = len(bytes.fromhex(text.replace(' ', '')))
            except:
                byte_count = 0
        else:
            byte_count = len(text.encode('utf-8'))
        self.send_stats_label.setText(f"{self._tr('长度：')}{byte_count}{self._tr(' 字节')}")
    
    def _build_increment_bytes(self, unit, iteration=0, fmt='HEX'):
        """构造「递增值」单元的字节序列（批量发送与自动应答共用）。

        unit 相关字段：
        - value：起始值，十进制或 0x 前缀十六进制，解析失败按 0 处理；
        - length：占用字节数；
        - step：步进量，默认 1，允许负数实现递减；
        - num_mode：'normal' 按二进制加，'bcd' 按十进制加并 BCD 编码；
        - byte_order：'big' 高位在前（默认）/ 'little' 低位在前。

        iteration 为当前轮次（从 0 开始），实际值 = 起始值 + iteration * step，
        超出长度可表示范围后取模回绕（Python 取模结果恒为非负，故负步进同样安全）。

        fmt：'文本' 时输出 ASCII 十进制数字串（与文本格式固定值单元的编码方式对齐，
        避免把 0x00 等不可见控制字节发给文本终端）；普通数值占 length 位、BCD 占 2*length 位，
        右对齐补 '0'。HEX 等其他格式输出二进制 / BCD 原始字节。
        """
        length = max(1, int(unit.get('length', 1) or 1))
        # 防御：increment 为数值宽度，超过 16 字节起始值无法表达且 to_bytes 会申请超大内存，
        # 钳制到 MAX_INCREMENT_UNIT_LENGTH（正常配置经 UI/校验已限制，此处兜底外部编辑的规则文件）。
        if length > MAX_INCREMENT_UNIT_LENGTH:
            print(f"[WARN] 递增值单元长度 {length} 超过上限 {MAX_INCREMENT_UNIT_LENGTH}，已按上限处理")
            length = MAX_INCREMENT_UNIT_LENGTH
        raw_val = (unit.get('value', '') or '').strip()
        try:
            start_val = int(raw_val, 16) if raw_val.lower().startswith('0x') else (int(raw_val) if raw_val else 0)
        except Exception:
            start_val = 0
        try:
            step = int(unit.get('step', 1))
        except Exception:
            step = 1
        order = 'big' if unit.get('byte_order', 'big') == 'big' else 'little'
        it = max(0, int(iteration))
        is_bcd = unit.get('num_mode', 'normal') == 'bcd'

        # 文本格式：统一输出 ASCII 十进制数字串；字节序仅对多字节原始数值有意义，文本下不适用。
        if fmt == '文本':
            width = length * 2 if is_bcd else length
            current_dec = (start_val + it * step) % (10 ** width)
            return str(current_dec).rjust(width, '0').encode('ascii')

        if is_bcd:
            # BCD 十进制递增：十进制加步进后按 BCD 编码到 length 字节
            max_dec = 10 ** (length * 2)  # length 字节 BCD 可表示 0 ~ 10^(2L)-1
            current_dec = (start_val + it * step) % max_dec
            digits = str(current_dec).rjust(length * 2, '0')
            bcd_bytes = bytearray(
                (int(digits[i]) << 4) | int(digits[i + 1])
                for i in range(0, len(digits), 2))
            if order != 'big':
                bcd_bytes.reverse()
            return bytes(bcd_bytes)

        modulo = 1 << (length * 8)
        current = (start_val + it * step) % modulo
        return current.to_bytes(length, byteorder=order)

    def build_batch_frame_bytes(self, frame_units, fmt='HEX', iteration=0):
        """根据批量发送帧单元配置生成实际发送字节。
        复用自动应答匹配帧的单元类型：fixed / wildcard / checksum，
        以及批量发送特有的 increment（递增值）。
        - wildcard 在发送场景中按长度填充 00。
        - increment：起始值 + 当前轮次（iteration），按 length 字节表示，
          超过长度可表示的最大值后自动回 0 循环。"""
        data = bytearray()
        for unit in frame_units:
            unit_type = unit.get('type', 'fixed')
            length = unit.get('length', 1)

            if unit_type == 'fixed':
                raw = self.parse_unit_value(unit.get('value', ''), fmt)
                if len(raw) < length:
                    raw += b'\x00' * (length - len(raw))
                elif len(raw) > length:
                    raw = raw[:length]
                data.extend(raw)
            elif unit_type == 'wildcard':
                data.extend(b'\x00' * length)
            elif unit_type == 'increment':
                data.extend(self._build_increment_bytes(unit, iteration, fmt))
            elif unit_type == 'checksum':
                algo = unit.get('algorithm', 'xor8')
                if algo == 'xor':
                    algo = 'xor8'
                elif algo == 'sum':
                    algo = 'sum8'
                crc_start = unit.get('crc_start', 0)
                crc_end = unit.get('crc_end', -1)
                end = len(data) - 1 if (crc_end is None or crc_end < 0) else crc_end
                start_i = max(0, crc_start)
                end_i = min(len(data) - 1, end)
                target = bytes(data[start_i:end_i + 1]) if start_i <= end_i else b''
                checksum_bytes = self.calc_checksum(target, algo)
                if unit.get('byte_order', 'big') == 'little' and len(checksum_bytes) > 1:
                    checksum_bytes = checksum_bytes[::-1]
                data.extend(checksum_bytes)
        return bytes(data)

    def configure_batch_command_frame(self, content_edit, format_combo, frame_state):
        """打开批量发送帧配置窗口，并将配置结果写回指令内容。"""
        rule = {
            'name': '',
            'enabled': True,
            'match_frame': frame_state.get('frame_units', []),
            'response_frame': [],
            'response_delay_ms': 0,
            'format': frame_state.get('frame_format', 'HEX')
        }
        dialog = BatchFrameConfigDialog(self, rule)
        if dialog.exec_():
            try:
                frame_fmt = dialog.frame_format
                frame_data = self.build_batch_frame_bytes(dialog.frame_units, frame_fmt)
                # 预览内容需与所选发送格式对齐：文本帧按 UTF-8 可逆显示，HEX 帧按两位十六进制显示。
                # 实际发送始终以 frame_units 动态组帧为准，此处文本框仅作预览/兼容旧读取路径。
                if frame_fmt == '文本':
                    preview = frame_data.decode('utf-8', errors='replace')
                    preview = preview.replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')
                    content_edit.setText(preview)
                    format_combo.setCurrentText('文本')
                else:
                    content_edit.setText(' '.join(f'{b:02X}' for b in frame_data))
                    format_combo.setCurrentText('HEX')
                frame_state['frame_units'] = dialog.frame_units
                frame_state['frame_format'] = frame_fmt
            except Exception as e:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('生成指令失败：')}{str(e)}")
    
    def add_batch_command(self):
        """添加批量发送指令"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox, QSpinBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self._tr("添加指令"))
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # 指令名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(self._tr("指令名称:")))
        name_edit = QLineEdit()
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        # 指令内容
        content_layout = QHBoxLayout()
        content_layout.addWidget(QLabel(self._tr("指令内容:")))
        content_edit = QLineEdit()
        content_layout.addWidget(content_edit)
        layout.addLayout(content_layout)
        
        # 发送格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(self._tr("发送格式:")))
        format_combo = QComboBox()
        format_combo.addItems(["文本", "HEX"])
        format_layout.addWidget(format_combo)
        frame_state = {'frame_units': [], 'frame_format': 'HEX'}
        add_rule_btn = QPushButton(self._tr("添加规则"))
        add_rule_btn.clicked.connect(lambda: self.configure_batch_command_frame(content_edit, format_combo, frame_state))
        format_layout.addWidget(add_rule_btn)
        layout.addLayout(format_layout)
        
        # 指定发送间隔（仅在"全部固定间隔"未勾选时生效；发完当前指令后等此间隔再发下一条）
        interval_layout = QHBoxLayout()
        interval_check = QCheckBox(self._tr("指定发送间隔"))
        interval_layout.addWidget(interval_check)
        interval_spin = QSpinBox()
        interval_spin.setRange(0, 600000)
        interval_spin.setValue(1000)
        interval_spin.setSuffix(" ms")
        interval_spin.setEnabled(False)
        def _on_interval_toggled(chk, _cb=interval_check, _sp=interval_spin):
            # 防呆：若外部"全部固定间隔"已勾选则拒绝
            if chk and getattr(self, 'batch_fixed_interval_check', None) is not None \
                    and self.batch_fixed_interval_check.isChecked():
                _cb.blockSignals(True)
                _cb.setChecked(False)
                _cb.blockSignals(False)
                _sp.setEnabled(False)
                QMessageBox.warning(
                    dialog,
                    self._tr("警告"),
                    self._tr("已启用『全部固定间隔』，不能再为单条指令设置自定义间隔。请先取消『全部固定间隔』。")
                )
                return
            _sp.setEnabled(chk)
        interval_check.toggled.connect(_on_interval_toggled)
        interval_layout.addWidget(interval_spin)
        interval_layout.addStretch()
        layout.addLayout(interval_layout)
        
        # 选中状态
        check_layout = QHBoxLayout()
        enabled_check = QCheckBox(self._tr("默认选中"))
        enabled_check.setChecked(True)
        check_layout.addWidget(enabled_check)
        check_layout.addStretch()
        layout.addLayout(check_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(self._tr("确定"))
        cancel_btn = QPushButton(self._tr("取消"))
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        def on_ok():
            command = {
                'name': name_edit.text() or f'指令{len(self.batch_commands) + 1}',
                'content': content_edit.text(),
                'format': format_combo.currentText(),
                'enabled': enabled_check.isChecked(),
                'use_custom_interval': interval_check.isChecked(),
                'custom_interval_ms': int(interval_spin.value()),
            }
            if frame_state.get('frame_units'):
                command['frame_units'] = frame_state['frame_units']
                command['frame_format'] = frame_state['frame_format']
            self.batch_commands.append(command)
            self.save_batch_commands()
            self.refresh_commands_table()
            dialog.accept()
        
        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def edit_batch_command(self):
        """编辑批量发送指令"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox, QSpinBox
        
        selected_row = self.commands_table.currentRow()
        if selected_row < 0 or selected_row >= len(self.batch_commands):
            QMessageBox.warning(self, self._tr("警告"), self._tr("请先选择要编辑的指令"))
            return
        
        command = self.batch_commands[selected_row]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self._tr("编辑指令"))
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # 指令名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(self._tr("指令名称:")))
        name_edit = QLineEdit(command.get('name', f'指令{selected_row + 1}'))
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        # 指令内容
        content_layout = QHBoxLayout()
        content_layout.addWidget(QLabel(self._tr("指令内容:")))
        content_edit = QLineEdit(command['content'])
        content_layout.addWidget(content_edit)
        layout.addLayout(content_layout)
        
        # 发送格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(self._tr("发送格式:")))
        format_combo = QComboBox()
        format_combo.addItems(["文本", "HEX"])
        format_combo.setCurrentText(command['format'])
        format_layout.addWidget(format_combo)
        frame_state = {
            'frame_units': command.get('frame_units', []),
            'frame_format': command.get('frame_format', 'HEX')
        }
        edit_rule_btn = QPushButton(self._tr("编辑规则") if frame_state.get('frame_units') else self._tr("添加规则"))
        edit_rule_btn.clicked.connect(lambda: self.configure_batch_command_frame(content_edit, format_combo, frame_state))
        format_layout.addWidget(edit_rule_btn)
        layout.addLayout(format_layout)
        
        # 指定发送间隔
        interval_layout = QHBoxLayout()
        interval_check = QCheckBox(self._tr("指定发送间隔"))
        interval_check.setChecked(bool(command.get('use_custom_interval', False)))
        interval_layout.addWidget(interval_check)
        interval_spin = QSpinBox()
        interval_spin.setRange(0, 600000)
        interval_spin.setValue(int(command.get('custom_interval_ms', 1000) or 1000))
        interval_spin.setSuffix(" ms")
        interval_spin.setEnabled(interval_check.isChecked())
        def _on_interval_toggled(chk, _cb=interval_check, _sp=interval_spin):
            # 防呆：若外部"全部固定间隔"已勾选则拒绝
            if chk and getattr(self, 'batch_fixed_interval_check', None) is not None \
                    and self.batch_fixed_interval_check.isChecked():
                _cb.blockSignals(True)
                _cb.setChecked(False)
                _cb.blockSignals(False)
                _sp.setEnabled(False)
                QMessageBox.warning(
                    dialog,
                    self._tr("警告"),
                    self._tr("已启用『全部固定间隔』，不能再为单条指令设置自定义间隔。请先取消『全部固定间隔』。")
                )
                return
            _sp.setEnabled(chk)
        interval_check.toggled.connect(_on_interval_toggled)
        interval_layout.addWidget(interval_spin)
        interval_layout.addStretch()
        layout.addLayout(interval_layout)
        
        # 选中状态
        check_layout = QHBoxLayout()
        enabled_check = QCheckBox(self._tr("默认选中"))
        enabled_check.setChecked(command['enabled'])
        check_layout.addWidget(enabled_check)
        check_layout.addStretch()
        layout.addLayout(check_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(self._tr("确定"))
        cancel_btn = QPushButton(self._tr("取消"))
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        def on_ok():
            updated_command = {
                'name': name_edit.text() or f'指令{selected_row + 1}',
                'content': content_edit.text(),
                'format': format_combo.currentText(),
                'enabled': enabled_check.isChecked(),
                'use_custom_interval': interval_check.isChecked(),
                'custom_interval_ms': int(interval_spin.value()),
            }
            if frame_state.get('frame_units'):
                updated_command['frame_units'] = frame_state['frame_units']
                updated_command['frame_format'] = frame_state['frame_format']
            self.batch_commands[selected_row] = updated_command
            self.save_batch_commands()
            self.refresh_commands_table()
            dialog.accept()
        
        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def delete_batch_command(self):
        """删除批量发送指令"""
        # 收集所有选中的指令索引（第 1 列是容器 QWidget，需从中取出 QCheckBox）
        selected_indices = []
        for i in range(min(self.commands_table.rowCount(), len(self.batch_commands))):
            cell = self.commands_table.cellWidget(i, 1)
            check_box = cell.findChild(QCheckBox) if cell else None
            if check_box is not None and check_box.isChecked():
                selected_indices.append(i)
        
        if not selected_indices:
            QMessageBox.warning(self, self._tr("警告"), self._tr("请先选择要删除的指令"))
            return
        
        if QMessageBox.question(self, self._tr("确认"), f"{self._tr('确定要删除选中的 ')}{len(selected_indices)}{self._tr(' 条指令吗？')}", 
                              QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # 按索引从大到小删除，避免索引错位
            for i in sorted(selected_indices, reverse=True):
                if 0 <= i < len(self.batch_commands):
                    self.batch_commands.pop(i)
            self.save_batch_commands()
            self.refresh_commands_table()
    
    def on_batch_commands_context_menu(self, pos):
        """批量发送表格右键菜单：上移/下移当前行的指令"""
        from PyQt5.QtWidgets import QMenu
        index = self.commands_table.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        if row < 0 or row >= len(self.batch_commands):
            return
        menu = QMenu(self.commands_table)
        up_action = menu.addAction(self._tr("上移"))
        down_action = menu.addAction(self._tr("下移"))
        up_action.setEnabled(row > 0)
        down_action.setEnabled(row < len(self.batch_commands) - 1)
        chosen = menu.exec_(self.commands_table.viewport().mapToGlobal(pos))
        if chosen is up_action:
            self.move_batch_command(row, row - 1)
        elif chosen is down_action:
            self.move_batch_command(row, row + 1)
    
    def move_batch_command(self, src, dst):
        """将 batch_commands 中 src 位置的指令移动到 dst 位置，并刷新表格。"""
        if not (0 <= src < len(self.batch_commands)):
            return
        if not (0 <= dst < len(self.batch_commands)):
            return
        if src == dst:
            return
        cmd = self.batch_commands.pop(src)
        self.batch_commands.insert(dst, cmd)
        self.save_batch_commands()
        self.refresh_commands_table()
        self.commands_table.selectRow(dst)
    
    def import_batch_commands(self):
        """导入批量发送指令"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self._tr("导入指令"), "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.batch_commands = data.get('commands', [])
                self.save_batch_commands()
                self.refresh_commands_table()
                QMessageBox.information(self, self._tr("成功"), f"{self._tr('成功导入 ')}{len(self.batch_commands)}{self._tr(' 条指令')}")
            except Exception as e:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('导入失败：')}{str(e)}")
    
    def export_batch_commands(self):
        """导出批量发送指令"""
        if not self.batch_commands:
            QMessageBox.warning(self, self._tr("警告"), self._tr("没有指令可导出"))
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, self._tr("导出指令"), "batch_commands.json", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({'commands': self.batch_commands}, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, self._tr("成功"), f"{self._tr('成功导出 ')}{len(self.batch_commands)}{self._tr(' 条指令')}")
            except Exception as e:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('导出失败：')}{str(e)}")
    
    # ==================== 批量发送指令持久化 ====================
    def load_batch_commands(self):
        """从磁盘加载批量发送指令"""
        try:
            if os.path.exists(BATCH_COMMANDS_FILE):
                with open(BATCH_COMMANDS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.batch_commands = data.get('commands', [])
                print(f"[DEBUG] 加载了 {len(self.batch_commands)} 条批量发送指令")
        except Exception as e:
            print(f"[DEBUG] 加载批量发送指令失败: {e}")
            self.batch_commands = []
        finally:
            if hasattr(self, 'commands_table'):
                self.refresh_commands_table()
    
    def save_batch_commands(self):
        """保存批量发送指令到磁盘"""
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(BATCH_COMMANDS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'commands': self.batch_commands}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DEBUG] 保存批量发送指令失败: {e}")
    
    # ==================== 快捷指令 ====================
    def load_quick_commands(self):
        """从磁盘加载快捷指令"""
        try:
            if os.path.exists(QUICK_COMMANDS_FILE):
                with open(QUICK_COMMANDS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quick_commands = data.get('commands', [])
                print(f"[DEBUG] 加载了 {len(self.quick_commands)} 条快捷指令")
        except Exception as e:
            print(f"[DEBUG] 加载快捷指令失败: {e}")
            self.quick_commands = []
        finally:
            if hasattr(self, 'quick_commands_table'):
                self.refresh_quick_commands_table()
    
    def save_quick_commands(self):
        """保存快捷指令到磁盘"""
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(QUICK_COMMANDS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'commands': self.quick_commands}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DEBUG] 保存快捷指令失败: {e}")
    
    def add_quick_command(self):
        """添加快捷指令（复用批量发送的编辑对话框结构，支持帧规则）"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self._tr("添加指令"))
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(self._tr("指令名称:")))
        name_edit = QLineEdit()
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        content_layout = QHBoxLayout()
        content_layout.addWidget(QLabel(self._tr("指令内容:")))
        content_edit = QLineEdit()
        content_layout.addWidget(content_edit)
        layout.addLayout(content_layout)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(self._tr("发送格式:")))
        format_combo = QComboBox()
        format_combo.addItems(["文本", "HEX"])
        format_layout.addWidget(format_combo)
        frame_state = {'frame_units': [], 'frame_format': 'HEX'}
        add_rule_btn = QPushButton(self._tr("添加规则"))
        add_rule_btn.clicked.connect(lambda: self.configure_batch_command_frame(content_edit, format_combo, frame_state))
        format_layout.addWidget(add_rule_btn)
        layout.addLayout(format_layout)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(self._tr("确定"))
        cancel_btn = QPushButton(self._tr("取消"))
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        def on_ok():
            command = {
                'name': name_edit.text() or f'指令{len(self.quick_commands) + 1}',
                'content': content_edit.text(),
                'format': format_combo.currentText(),
            }
            if frame_state.get('frame_units'):
                command['frame_units'] = frame_state['frame_units']
                command['frame_format'] = frame_state['frame_format']
            self.quick_commands.append(command)
            self.save_quick_commands()
            self.refresh_quick_commands_table()
            dialog.accept()
        
        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec_()
    
    def edit_quick_command_idx(self, index):
        """编辑指定索引的快捷指令"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
        
        if not (0 <= index < len(self.quick_commands)):
            return
        command = self.quick_commands[index]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self._tr("编辑指令"))
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(self._tr("指令名称:")))
        name_edit = QLineEdit(command.get('name', f'指令{index + 1}'))
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        content_layout = QHBoxLayout()
        content_layout.addWidget(QLabel(self._tr("指令内容:")))
        content_edit = QLineEdit(command.get('content', ''))
        content_layout.addWidget(content_edit)
        layout.addLayout(content_layout)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(self._tr("发送格式:")))
        format_combo = QComboBox()
        format_combo.addItems(["文本", "HEX"])
        format_combo.setCurrentText(command.get('format', '文本'))
        format_layout.addWidget(format_combo)
        frame_state = {
            'frame_units': command.get('frame_units', []),
            'frame_format': command.get('frame_format', 'HEX')
        }
        edit_rule_btn = QPushButton(self._tr("编辑规则") if frame_state.get('frame_units') else self._tr("添加规则"))
        edit_rule_btn.clicked.connect(lambda: self.configure_batch_command_frame(content_edit, format_combo, frame_state))
        format_layout.addWidget(edit_rule_btn)
        layout.addLayout(format_layout)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(self._tr("确定"))
        cancel_btn = QPushButton(self._tr("取消"))
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        def on_ok():
            updated = {
                'name': name_edit.text() or f'指令{index + 1}',
                'content': content_edit.text(),
                'format': format_combo.currentText(),
            }
            if frame_state.get('frame_units'):
                updated['frame_units'] = frame_state['frame_units']
                updated['frame_format'] = frame_state['frame_format']
            self.quick_commands[index] = updated
            self.save_quick_commands()
            self.refresh_quick_commands_table()
            dialog.accept()
        
        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec_()
    
    def delete_quick_command(self):
        """删除当前选中行的快捷指令"""
        row = self.quick_commands_table.currentRow()
        if row < 0 or row >= len(self.quick_commands):
            QMessageBox.warning(self, self._tr("警告"), self._tr("请先选择要删除的指令"))
            return
        if QMessageBox.question(self, self._tr("确认"),
                                f"{self._tr('确定要删除选中的 ')}1{self._tr(' 条指令吗？')}",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.quick_commands.pop(row)
            self.save_quick_commands()
            self.refresh_quick_commands_table()
    
    def clear_quick_commands(self):
        """清空所有快捷指令（带二次确认）"""
        if not self.quick_commands:
            QMessageBox.information(self, self._tr("提示"), self._tr("当前没有可清空的快捷指令"))
            return
        count = len(self.quick_commands)
        if QMessageBox.question(
                self, self._tr("确认"),
                f"{self._tr('确定要清空全部 ')}{count}{self._tr(' 条快捷指令吗？此操作不可撤销。')}",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.quick_commands.clear()
            self.save_quick_commands()
            self.refresh_quick_commands_table()
    
    def import_quick_commands(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, self._tr("导入指令"), "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quick_commands = data.get('commands', [])
                self.save_quick_commands()
                self.refresh_quick_commands_table()
                QMessageBox.information(self, self._tr("成功"),
                                        f"{self._tr('成功导入 ')}{len(self.quick_commands)}{self._tr(' 条指令')}")
            except Exception as e:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('导入失败：')}{str(e)}")
    
    def export_quick_commands(self):
        if not self.quick_commands:
            QMessageBox.warning(self, self._tr("警告"), self._tr("没有指令可导出"))
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, self._tr("导出指令"), "quick_commands.json", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({'commands': self.quick_commands}, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, self._tr("成功"),
                                        f"{self._tr('成功导出 ')}{len(self.quick_commands)}{self._tr(' 条指令')}")
            except Exception as e:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('导出失败：')}{str(e)}")
    
    def send_quick_command(self, index):
        """点击列表中的发送按钮时立即单次发送该指令"""
        if not (0 <= index < len(self.quick_commands)):
            return
        if not self.is_open:
            QMessageBox.warning(self, self._tr("警告"), self._tr("串口未打开"))
            return
        cmd = self.quick_commands[index]
        # 若配置了帧规则，按帧规则动态构造字节（无递增，iteration=0）
        frame_units = cmd.get('frame_units')
        if frame_units:
            try:
                data = self.build_batch_frame_bytes(frame_units, cmd.get('frame_format', 'HEX'), iteration=0)
            except Exception as e:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('发送失败：')}{str(e)}")
                return
            if data:
                self.send_data(data)
            return
        # 否则按 content + format 直接发送
        content = cmd.get('content', '')
        fmt = cmd.get('format', '文本')
        if fmt == 'HEX':
            try:
                data = bytes.fromhex(content.replace(' ', ''))
            except Exception as e:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('发送失败：')}{str(e)}")
                return
        else:
            text = content.replace('\\r', '\r').replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')
            data = text.encode('utf-8')
        if data:
            self.send_data(data)
    
    def on_quick_commands_context_menu(self, pos):
        """快捷指令表格右键菜单：上移/下移选中的指令"""
        from PyQt5.QtWidgets import QMenu
        index = self.quick_commands_table.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        if row < 0 or row >= len(self.quick_commands):
            return
        menu = QMenu(self.quick_commands_table)
        up_action = menu.addAction(self._tr("上移"))
        down_action = menu.addAction(self._tr("下移"))
        up_action.setEnabled(row > 0)
        down_action.setEnabled(row < len(self.quick_commands) - 1)
        chosen = menu.exec_(self.quick_commands_table.viewport().mapToGlobal(pos))
        if chosen is up_action:
            self.move_quick_command(row, row - 1)
        elif chosen is down_action:
            self.move_quick_command(row, row + 1)
    
    def move_quick_command(self, src, dst):
        """在快捷指令列表中把 src 位置移动到 dst 位置，持久化并刷新表格。"""
        if not (0 <= src < len(self.quick_commands)):
            return
        if not (0 <= dst < len(self.quick_commands)):
            return
        if src == dst:
            return
        cmd = self.quick_commands.pop(src)
        self.quick_commands.insert(dst, cmd)
        self.save_quick_commands()
        self.refresh_quick_commands_table()
        self.quick_commands_table.selectRow(dst)
    
    def refresh_quick_commands_table(self):
        """刷新快捷指令表格：操作(编辑+发送)/名称/指令/格式"""
        self.quick_commands_table.setRowCount(len(self.quick_commands))
        for i, cmd in enumerate(self.quick_commands):
            # 操作列（第0列）：编辑 + 发送
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(2)
            edit_btn = self._make_table_action_btn(self._tr("编辑"))
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_quick_command_idx(idx))
            action_layout.addWidget(edit_btn)
            send_btn = self._make_table_action_btn(self._tr("发送"))
            send_btn.clicked.connect(lambda checked, idx=i: self.send_quick_command(idx))
            action_layout.addWidget(send_btn)
            self.quick_commands_table.setCellWidget(i, 0, action_widget)

            self.quick_commands_table.setItem(i, 1, QTableWidgetItem(cmd.get('name', f'指令{i + 1}')))
            self.quick_commands_table.setItem(i, 2, QTableWidgetItem(cmd.get('content', '')))
            self.quick_commands_table.setItem(i, 3, QTableWidgetItem(cmd.get('format', '文本')))

    def _make_table_action_btn(self, text):
        """生成列表操作列的窄按钮：宽度仅容纳2个汉字，不被遮挡。"""
        btn = QPushButton(text)
        # 收紧内边距，避免默认样式把按钮撑宽
        btn.setStyleSheet("QPushButton { padding: 1px 2px; }")
        fm = btn.fontMetrics()
        width = fm.horizontalAdvance(text) if hasattr(fm, 'horizontalAdvance') else fm.width(text)
        # 文字宽 + 左右内边距(4) + 边框(2) + 少量余量(6)
        btn.setFixedWidth(width + 12)
        return btn

    def refresh_commands_table(self):
        """刷新指令表格"""
        self.commands_table.setRowCount(len(self.batch_commands))
        # 当前是否处于"全部固定间隔"模式
        use_global = (getattr(self, 'batch_fixed_interval_check', None) is not None
                      and self.batch_fixed_interval_check.isChecked())
        global_ms = int(self.batch_interval_spin.value()) if use_global else 0

        for i, cmd in enumerate(self.batch_commands):
            # 操作列（第0列）：编辑按钮
            edit_btn = self._make_table_action_btn(self._tr("编辑"))
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_batch_command_idx(idx))
            self.commands_table.setCellWidget(i, 0, edit_btn)

            # 选中复选框 + 间隔标签（第1列）
            # - 全部固定间隔=True：所有行显示全局间隔
            # - 全部固定间隔=False：仅在指令开启了"指定发送间隔"时显示自身间隔
            cell = QWidget()
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(4, 0, 4, 0)
            cell_layout.setSpacing(4)
            check_box = QCheckBox()
            check_box.setChecked(cmd.get('enabled', True))
            check_box.stateChanged.connect(lambda state, idx=i: self.update_command_enabled(idx, state))
            cell_layout.addWidget(check_box)
            if use_global:
                interval_label = QLabel(f"{global_ms} ms")
                interval_label.setStyleSheet("color: #2A82DA;")
                cell_layout.addWidget(interval_label)
            elif cmd.get('use_custom_interval', False):
                interval_ms = int(cmd.get('custom_interval_ms', 0) or 0)
                interval_label = QLabel(f"{interval_ms} ms")
                interval_label.setStyleSheet("color: #888;")
                cell_layout.addWidget(interval_label)
            cell_layout.addStretch()
            self.commands_table.setCellWidget(i, 1, cell)

            # 指令名称
            name_item = QTableWidgetItem(cmd.get('name', f'指令{i + 1}'))
            self.commands_table.setItem(i, 2, name_item)

            # 指令内容
            content_item = QTableWidgetItem(cmd.get('content', ''))
            self.commands_table.setItem(i, 3, content_item)

            # 格式
            format_item = QTableWidgetItem(cmd.get('format', '文本'))
            self.commands_table.setItem(i, 4, format_item)
    
    def update_command_enabled(self, index, state):
        """更新指令的选中状态"""
        if 0 <= index < len(self.batch_commands):
            self.batch_commands[index]['enabled'] = state == Qt.Checked
            self.save_batch_commands()
    
    def edit_batch_command_idx(self, index):
        """通过索引编辑指令"""
        if 0 <= index < len(self.batch_commands):
            self.commands_table.setCurrentCell(index, 2)  # 定位到名称列（第0列已为操作按钮）
            self.edit_batch_command()
    
    def on_wrap_toggled(self, checked):
        """自动换行切换：勾选后按窗口宽度自适应换行；未勾选则保持原始换行不自动换行。"""
        if not hasattr(self, 'receive_text'):
            return
        if checked:
            self.receive_text.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.receive_text.setLineWrapMode(QTextEdit.NoWrap)
    
    def on_receive_text_toggled(self, checked):
        """接收文本模式切换：文本/HEX 互斥，且至少保留一个选中"""
        if checked:
            self.receive_hex_radio.blockSignals(True)
            self.receive_hex_radio.setChecked(False)
            self.receive_hex_radio.blockSignals(False)
            self.hex_mode = False
            print(f"[DEBUG] 接收模式改变: hex_mode=False")
        elif not self.receive_hex_radio.isChecked():
            self.receive_hex_radio.blockSignals(True)
            self.receive_hex_radio.setChecked(True)
            self.receive_hex_radio.blockSignals(False)
            self.hex_mode = True
            print(f"[DEBUG] 接收文本取消，自动切换到HEX模式")
    
    def on_receive_hex_toggled(self, checked):
        """接收HEX模式切换：文本/HEX 互斥，且至少保留一个选中"""
        if checked:
            self.receive_text_radio.blockSignals(True)
            self.receive_text_radio.setChecked(False)
            self.receive_text_radio.blockSignals(False)
            self.hex_mode = True
            print(f"[DEBUG] 接收模式改变: hex_mode=True")
        elif not self.receive_text_radio.isChecked():
            self.receive_text_radio.blockSignals(True)
            self.receive_text_radio.setChecked(True)
            self.receive_text_radio.blockSignals(False)
            self.hex_mode = False
            print(f"[DEBUG] 接收HEX取消，自动切换到文本模式")
    
    def on_send_text_toggled(self, checked):
        """发送文本模式切换：文本/HEX 互斥，且至少保留一个选中"""
        if checked:
            self.send_hex_radio.blockSignals(True)
            self.send_hex_radio.setChecked(False)
            self.send_hex_radio.blockSignals(False)
            print(f"[DEBUG] 发送模式改变: 文本模式")
            self.update_send_stats()
        elif not self.send_hex_radio.isChecked():
            self.send_hex_radio.blockSignals(True)
            self.send_hex_radio.setChecked(True)
            self.send_hex_radio.blockSignals(False)
            print(f"[DEBUG] 发送文本取消，自动切换到HEX模式")
            self.update_send_stats()
    
    def on_send_hex_toggled(self, checked):
        """发送HEX模式切换：文本/HEX 互斥，且至少保留一个选中"""
        if checked:
            self.send_text_radio.blockSignals(True)
            self.send_text_radio.setChecked(False)
            self.send_text_radio.blockSignals(False)
            print(f"[DEBUG] 发送模式改变: HEX模式")
            self.update_send_stats()
        elif not self.send_text_radio.isChecked():
            self.send_text_radio.blockSignals(True)
            self.send_text_radio.setChecked(True)
            self.send_text_radio.blockSignals(False)
            print(f"[DEBUG] 发送HEX取消，自动切换到文本模式")
            self.update_send_stats()
    
    def on_send_mode_changed(self):
        print(f"[DEBUG] 发送模式改变")
        self.update_send_stats()
    
    def toggle_left_panel(self):
        """折叠/展开左侧功能面板"""
        if self.left_widget.isVisible():
            self.left_widget.hide()
            self.toggle_left_btn.setText("▶")
            self.toggle_left_btn.setToolTip(self._tr("显示左侧面板"))
        else:
            self.left_widget.show()
            self.toggle_left_btn.setText("◀")
            self.toggle_left_btn.setToolTip(self._tr("隐藏左侧面板"))

    def clear_receive(self):
        print("[DEBUG] 清除接收区")
        self.receive_text.clear()
        self.receive_display_size = 0
        if hasattr(self, 'receive_line_count'):
            self.receive_line_count = 0
        # 同时清零收发字节统计和收发条数统计
        self.receive_count = 0
        self.receive_packet_count = 0
        self.send_count = 0
        self.send_packet_count = 0
        self.auto_reply_timeout_count = 0
        self.last_receive_count = 0
        if hasattr(self, 'temp_status_label'):
            self.temp_status_label.setText(
                f"{self._tr('接收：')}{self.receive_count}{self._tr('字节')} | {self._tr('发送：')}{self.send_count}{self._tr('字节')} | "
                f"{self.receive_packet_count}/{self.send_packet_count} | "
                f"{self._tr('应答失配：')}0 | "
                f"0.0 B/s"
            )
    
    def save_receive_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, self._tr("保存接收数据"), "", "Text Files (*.txt);;Log Files (*.log);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.receive_text.toPlainText())
                if hasattr(self, 'temp_status_label'):
                    self.temp_status_label.setText(f"{self._tr('数据已保存到 ')}{file_path}")
                print(f"[DEBUG] 数据已保存到: {file_path}")
            except Exception as e:
                print(f"[DEBUG] 保存失败: {e}")
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('保存失败：')}{str(e)}")
    
    def on_batch_enabled(self, enabled):
        print(f"[DEBUG] 批量发送启用状态: {enabled}")
        self.batch_start_btn.setEnabled(enabled)
    
    def on_batch_infinite_toggled(self, checked):
        print(f"[DEBUG] 无限循环状态: {checked}")
        self.batch_count_spin.setEnabled(not checked)
    
    def on_batch_fixed_interval_toggled(self, checked):
        """全部固定间隔开关：勾选时使用全局间隔 spinbox；未勾选时使用每条指令的自定义 interval。
        防呆：勾选此项时若存在任何指令已开启"指定发送间隔"，弹窗提示并回退。"""
        if checked:
            conflict_names = [
                (c.get('name') or f'指令{i + 1}')
                for i, c in enumerate(self.batch_commands)
                if c.get('use_custom_interval', False)
            ]
            if conflict_names:
                # 阻止本次勾选：先断开信号避免递归触发
                self.batch_fixed_interval_check.blockSignals(True)
                self.batch_fixed_interval_check.setChecked(False)
                self.batch_fixed_interval_check.blockSignals(False)
                self.batch_interval_spin.setEnabled(False)
                QMessageBox.warning(
                    self,
                    self._tr("警告"),
                    f"{self._tr('存在已配置自定义发送间隔的指令，无法启用全局固定间隔：')}\n"
                    + '\n'.join(f'  • {n}' for n in conflict_names)
                    + f"\n\n{self._tr('请先在指令编辑中取消其自定义间隔，或不勾选此项。')}"
                )
                return
        self.batch_interval_spin.setEnabled(bool(checked))
        # 状态切换后刷新表格，让每行的间隔标签实时同步
        if hasattr(self, 'commands_table'):
            self.refresh_commands_table()
    def _on_batch_global_interval_changed(self, _value):
        """全局间隔 spinbox 数值变化：若处于固定模式，同步刷新表格显示。"""
        if getattr(self, 'batch_fixed_interval_check', None) is not None \
                and self.batch_fixed_interval_check.isChecked() \
                and hasattr(self, 'commands_table'):
            self.refresh_commands_table()
    
    def _get_next_batch_interval(self):
        """根据"全部固定间隔"开关及下一条指令的自定义 interval，计算下一条指令发送前的等待时间(ms)。
        - 勾选"全部固定间隔"：始终返回全局间隔
        - 未勾选：若下一条指令 use_custom_interval=True 返回它的 custom_interval_ms；否则 0（立即发下一条）
        """
        if getattr(self, 'batch_fixed_interval_check', None) is not None and self.batch_fixed_interval_check.isChecked():
            return max(0, int(self.batch_interval_spin.value()))
        # 未勾选：读取下一条指令的自定义间隔
        try:
            next_cmd = self.selected_commands[self.current_command_index]
        except (IndexError, AttributeError):
            return 0
        if next_cmd.get('use_custom_interval', False):
            return max(0, int(next_cmd.get('custom_interval_ms', 0) or 0))
        return 0
    
    def start_batch_send(self):
        print("[DEBUG] 开始批量发送")
        if not self.is_open:
            print("[DEBUG] 串口未打开")
            QMessageBox.warning(self, self._tr("警告"), self._tr("串口未打开"))
            return
        
        # 过滤出选中的指令
        self.selected_commands = [cmd for cmd in self.batch_commands if cmd.get('enabled', True)]
        if not self.selected_commands:
            QMessageBox.warning(self, self._tr("警告"), self._tr("请至少选择一条指令"))
            return
        
        self.batch_sending = True
        self.batch_count = 0
        self.batch_total = self.batch_count_spin.value() if not self.batch_infinite_check.isChecked() else 0
        self.current_command_index = 0
        self.batch_start_btn.setEnabled(False)
        self.batch_stop_btn.setEnabled(True)
        
        # 立即发送第一条（不需要等待）；后续按"发完后等间隔时间再发下一条"语义调度
        QTimer.singleShot(0, self._batch_send_next)
    
    def _batch_send_next(self):
        """发送下一条选中指令；发完后按下一条指令(或全局)的间隔调度下一次执行。"""
        if not self.batch_sending:
            return
        if not self.selected_commands:
            self.stop_batch_send()
            return
        
        # 取出当前指令
        cmd = self.selected_commands[self.current_command_index]
        content = cmd.get('content', '')
        format_type = cmd.get('format', '文本')
        
        # 优先按帧规则构造（支持递增值等），否则回退到 content 字段
        data = None
        frame_units = cmd.get('frame_units')
        if frame_units:
            try:
                frame_fmt = cmd.get('frame_format', 'HEX')
                data = self.build_batch_frame_bytes(frame_units, frame_fmt, iteration=self.batch_count)
            except Exception as e:
                print(f"[ERROR] 帧规则构造失败: {e}，回退到 content 字段")
                data = None
        if data is None:
            if format_type == 'HEX':
                try:
                    data = bytes.fromhex(content.replace(' ', ''))
                except Exception as e:
                    print(f"[ERROR] HEX 解析失败: {e}，跳过该条")
                    data = b''
            else:
                processed_content = content
                processed_content = processed_content.replace('\\r', '\r')
                processed_content = processed_content.replace('\\n', '\n')
                processed_content = processed_content.replace('\\t', '\t')
                processed_content = processed_content.replace('\\\\', '\\')
                data = processed_content.encode('utf-8')
        
        if data and len(data) > 0:
            self.send_data(data)
        
        # 更新索引
        self.current_command_index += 1
        if self.current_command_index >= len(self.selected_commands):
            # 完成一轮
            self.batch_count += 1
            self.current_command_index = 0
            if self.batch_infinite_check.isChecked():
                self.batch_progress_label.setText(f"{self._tr('进度：')}{self.batch_count}/∞")
            else:
                self.batch_progress_label.setText(f"{self._tr('进度：')}{self.batch_count}/{self.batch_total}")
                if self.batch_count >= self.batch_total:
                    print("[DEBUG] 批量发送完成")
                    self.stop_batch_send()
                    return
        
        # 语义：发完当前指令后，等 next_interval 再发下一条
        next_interval = self._get_next_batch_interval()
        QTimer.singleShot(next_interval, self._batch_send_next)
    
    # 保留兼容性：老 API 名字仍可被外部调用（如翻译测试、快捷键），但走新路径
    def batch_send_timeout(self):
        self._batch_send_next()
    
    def stop_batch_send(self):
        print("[DEBUG] 停止批量发送")
        self.batch_sending = False
        # 老实现的 batch_timer 已被移除；这里只是保留字段清理避免残留
        if getattr(self, 'batch_timer', None):
            try:
                self.batch_timer.stop()
            except Exception:
                pass
            self.batch_timer = None
        self.batch_start_btn.setEnabled(self.batch_enable_check.isChecked())
        self.batch_stop_btn.setEnabled(False)
    
    def on_auto_reply_toggled(self, enabled):
        print(f"[DEBUG] 自动应答状态: {enabled}")
        self.auto_reply_enabled = enabled

    def on_head_match_toggled(self, enabled):
        print(f"[DEBUG] 失配按帧头判定: {enabled}")
        self.auto_reply_head_match = enabled
        self.save_config()
    
    def load_rules(self):
        print("[DEBUG] 加载自动应答规则")
        try:
            if os.path.exists(RULES_FILE):
                with open(RULES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reply_rules = data.get('rules', [])
                print(f"[DEBUG] 加载了 {len(self.reply_rules)} 条规则")
        except Exception as e:
            print(f"[DEBUG] 加载规则失败: {e}")
            self.reply_rules = []
        finally:
            # 刷新规则表格
            if hasattr(self, 'rules_table'):
                self.refresh_rules_table()
            # 预编译规则索引（首字节 -> rules）供 on_data_received 快速过滤
            self._precompile_rules()
    
    def save_rules(self):
        print("[DEBUG] 保存自动应答规则")
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(RULES_FILE, 'w', encoding='utf-8') as f:
                json.dump({'rules': self.reply_rules}, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] 保存了 {len(self.reply_rules)} 条规则")
        except:
            pass
        # 每次保存后重建规则索引（enabled / match_frame 可能变化）
        self._precompile_rules()
    
    def refresh_rules_table(self):
        """刷新规则表格"""
        self.rules_table.setRowCount(len(self.reply_rules))
        for i, rule in enumerate(self.reply_rules):
            # 操作列（第0列）：编辑按钮
            edit_btn = self._make_table_action_btn(self._tr("编辑"))
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_rule(idx))
            self.rules_table.setCellWidget(i, 0, edit_btn)

            check = QCheckBox()
            check.setChecked(rule.get('enabled', True))
            check.toggled.connect(lambda checked, idx=i: self.toggle_rule_enabled(idx, checked))
            self.rules_table.setCellWidget(i, 1, check)

            name_item = QTableWidgetItem(rule.get('name', f'规则{i+1}'))
            self.rules_table.setItem(i, 2, name_item)

            match_preview = self.get_frame_preview(rule.get('match_frame', []))
            self.rules_table.setItem(i, 3, QTableWidgetItem(match_preview))

            responses = self._get_rule_responses(rule)
            first_frame = responses[0]['frame'] if responses else []
            preview_text = self.get_frame_preview(first_frame)
            if len(responses) > 1:
                preview_text = f"{preview_text} (+{len(responses) - 1})"
            response_preview = preview_text
            self.rules_table.setItem(i, 4, QTableWidgetItem(response_preview))
        
        self.rules_count_label.setText(f"{self._tr('已配置 ')}{len(self.reply_rules)}{self._tr(' 条规则')}")
    
    def get_frame_preview(self, frame):
        """获取帧预览"""
        preview = ""
        for unit in frame:
            unit_type = unit.get('type', 'fixed')
            if unit_type == 'fixed':
                preview += unit.get('value', '') + " "
            elif unit_type == 'wildcard':
                preview += "??" * unit.get('length', 1) + " "
            elif unit_type == 'ref':
                preview += f"<{unit.get('value', '')}> "
            elif unit_type == 'increment':
                # 递增值：展示起始值与步进，实际发送值随规则命中次数累加
                start = (unit.get('value', '') or '0').strip()
                preview += f"[{start}+{unit.get('step', 1)}] "
            elif unit_type == 'checksum':
                algo = unit.get('algorithm', 'xor8')
                label = dict((k, l) for l, k in UartAssistantWindow.CHECKSUM_LABELS).get(algo, algo)
                preview += f"[{label}] "
        return preview.strip()
    
    def add_rule(self):
        """添加规则"""
        print("[DEBUG] 添加新规则")
        dialog = RuleConfigDialog(self)
        if dialog.exec_():
            self.reply_rules.append(dialog.rule)
            self.save_rules()
            self.refresh_rules_table()
    
    def edit_rule(self, index):
        """编辑规则"""
        print(f"[DEBUG] 编辑规则: {index}")
        if 0 <= index < len(self.reply_rules):
            dialog = RuleConfigDialog(self, self.reply_rules[index])
            if dialog.exec_():
                self.reply_rules[index] = dialog.rule
                self.save_rules()
                self.refresh_rules_table()
    
    def toggle_rule_enabled(self, index, enabled):
        """切换规则启用状态"""
        if 0 <= index < len(self.reply_rules):
            self.reply_rules[index]['enabled'] = enabled
            self.save_rules()
    
    def import_rules(self):
        """导入规则"""
        print("[DEBUG] 导入规则")
        file_path, _ = QFileDialog.getOpenFileName(
            self, self._tr("导入规则"), "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reply_rules = data.get('rules', [])
                self.save_rules()
                self.refresh_rules_table()
                QMessageBox.information(self, self._tr("成功"), f"{self._tr('成功导入 ')}{len(self.reply_rules)}{self._tr(' 条规则')}")
            except Exception as e:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('导入失败：')}{str(e)}")
    
    def export_rules(self):
        """导出规则"""
        print("[DEBUG] 导出规则")
        if not self.reply_rules:
            QMessageBox.warning(self, self._tr("警告"), self._tr("没有规则可导出"))
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, self._tr("导出规则"), "reply_rules.json", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({'rules': self.reply_rules}, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, self._tr("成功"), f"{self._tr('成功导出 ')}{len(self.reply_rules)}{self._tr(' 条规则')}")
            except Exception as e:
                QMessageBox.critical(self, self._tr("错误"), f"{self._tr('导出失败：')}{str(e)}")
    
    def on_rules_context_menu(self, pos):
        """自动应答规则表格右键菜单：上移/下移当前行的规则"""
        from PyQt5.QtWidgets import QMenu
        index = self.rules_table.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        if row < 0 or row >= len(self.reply_rules):
            return
        menu = QMenu(self.rules_table)
        up_action = menu.addAction(self._tr("上移"))
        down_action = menu.addAction(self._tr("下移"))
        up_action.setEnabled(row > 0)
        down_action.setEnabled(row < len(self.reply_rules) - 1)
        chosen = menu.exec_(self.rules_table.viewport().mapToGlobal(pos))
        if chosen is up_action:
            self.move_rule(row, row - 1)
        elif chosen is down_action:
            self.move_rule(row, row + 1)
    
    def move_rule(self, src, dst):
        """在自动应答规则列表中把 src 位置的规则移动到 dst 位置，持久化并刷新表格。"""
        if not (0 <= src < len(self.reply_rules)):
            return
        if not (0 <= dst < len(self.reply_rules)):
            return
        if src == dst:
            return
        rule = self.reply_rules.pop(src)
        self.reply_rules.insert(dst, rule)
        self.save_rules()
        self.refresh_rules_table()
        self.rules_table.selectRow(dst)
    
    def delete_rule(self):
        """删除选中的规则"""
        # 收集所有选中的规则索引
        selected_indices = []
        for i in range(min(self.rules_table.rowCount(), len(self.reply_rules))):
            check_box = self.rules_table.cellWidget(i, 1)
            if check_box and check_box.isChecked():
                selected_indices.append(i)
        
        if not selected_indices:
            QMessageBox.warning(self, self._tr("警告"), self._tr("请先选择要删除的规则"))
            return
        
        if QMessageBox.question(self, self._tr("确认"), f"{self._tr('确定要删除选中的 ')}{len(selected_indices)}{self._tr(' 条规则吗？')}", 
                              QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # 按索引从大到小删除，避免索引错位
            for i in sorted(selected_indices, reverse=True):
                if 0 <= i < len(self.reply_rules):
                    self.reply_rules.pop(i)
            self.save_rules()
            self.refresh_rules_table()
    
    def process_auto_reply(self, received_data):
        try:
            print(f"[DEBUG] 处理自动应答，规则数: {len(self.reply_rules)}")
            for rule in self.reply_rules:
                try:
                    if not rule.get('enabled', True):
                        continue
                    
                    match_frame = rule.get('match_frame', [])
                    fmt = rule.get('format', 'HEX')
                    is_match, captures = self.match_frame(received_data, match_frame, fmt)
                    if is_match:
                        print(f"[DEBUG] 匹配到规则: {rule.get('name')}")
                        # 仅浅拷贝需要的字段：避免整规则 deepcopy 的额外开销
                        responses_snapshot = self._get_rule_responses(rule)
                        rule_snapshot = {
                            'name': rule.get('name'),
                            'format': rule.get('format', 'HEX'),
                            'responses': responses_snapshot,
                        }
                        # 应答延迟已在每条应答帧自带 delay_ms 内，这里直接触发
                        iteration = self._take_reply_iteration(rule)
                        self.send_reply(rule_snapshot, dict(captures) if captures else {}, iteration)
                        break
                except Exception as e:
                    print(f"[DEBUG] 处理规则异常: {rule.get('name', 'unknown')}, 错误: {e}")
                    import traceback
                    traceback.print_exc()
                    # 继续处理下一个规则，不要因为一个规则错误而停止
                    continue
        except Exception as e:
            print(f"[DEBUG] 自动应答处理异常: {e}")
            import traceback
            traceback.print_exc()
    
    def parse_unit_value(self, value, fmt):
        """将单元的 value 按格式解析为字节串。
        fmt 为 '文本' 时按 UTF-8 编码（支持 \\r \\n \\t \\\\ 转义），
        否则按 HEX 解析。解析失败抛出异常，由调用方处理。"""
        if fmt == '文本':
            text = value
            text = text.replace('\\r', '\r')
            text = text.replace('\\n', '\n')
            text = text.replace('\\t', '\t')
            text = text.replace('\\\\', '\\')
            return text.encode('utf-8')
        else:
            return bytes.fromhex(value.replace(' ', ''))

    def _match_frame_at(self, data, match_frame, fmt, start):
        """从 data 的 start 位置尝试匹配整个 match_frame。
        返回 (是否匹配, 捕获字典, 结束位置)。"""
        captures = {}
        pos = start
        for idx, unit in enumerate(match_frame):
            try:
                unit_type = unit.get('type', 'fixed')
                length = unit.get('length', 1)
                name = unit.get('name', '') or f'unit{idx}'

                if unit_type == 'fixed':
                    value = unit.get('value', '')
                    # 缓存 fixed 单元 parse 结果，加速滑动窗口反复调用
                    mcache = getattr(self, '_match_fixed_cache', None)
                    if mcache is None:
                        mcache = {}
                        self._match_fixed_cache = mcache
                    mkey = id(unit)
                    ce = mcache.get(mkey)
                    if ce is not None and ce[0] == value and ce[1] == fmt:
                        expected = ce[2]
                    else:
                        try:
                            expected = self.parse_unit_value(value, fmt)
                        except Exception:
                            print(f"[ERROR] 匹配帧单元值解析失败: {value} (格式={fmt})")
                            return False, {}, pos
                        mcache[mkey] = (value, fmt, expected)

                    seg_len = length
                    if pos + seg_len > len(data):
                        return False, {}, pos

                    compare_len = min(len(expected), seg_len)
                    if data[pos:pos + compare_len] != expected[:compare_len]:
                        return False, {}, pos
                    # fixed 单元也存入 captures，允许应答帧用"引用匹配值"回传该字段
                    captures[name] = bytes(data[pos:pos + seg_len])
                    pos += seg_len
                elif unit_type == 'wildcard':
                    if pos + length > len(data):
                        return False, {}, pos
                    captures[name] = data[pos:pos + length]
                    pos += length
                elif unit_type == 'checksum':
                    # 对帧内指定范围(相对帧起始的字节索引)计算校验，与接收数据中对应字节比对
                    algo = unit.get('algorithm', 'xor8')
                    if algo == 'xor':
                        algo = 'xor8'
                    elif algo == 'sum':
                        algo = 'sum8'
                    # 校验值字节长度
                    spec = self.CHECKSUM_ALGORITHMS.get(algo)
                    if spec and spec[0] == 'crc':
                        chk_len = spec[1] // 8
                    elif algo in ('sum16', 'sum16_inet'):
                        chk_len = 2
                    else:
                        chk_len = 1
                    if pos + chk_len > len(data):
                        return False, {}, pos
                    # 计算校验范围（相对帧起始 start）
                    crc_start = unit.get('crc_start', 0)
                    crc_end = unit.get('crc_end', -1)
                    frame_len = pos - start  # 当前已匹配的帧内字节数(校验位之前)
                    end_rel = frame_len - 1 if (crc_end is None or crc_end < 0) else crc_end
                    start_rel = max(0, crc_start)
                    end_rel = min(frame_len - 1, end_rel)
                    if start_rel > end_rel:
                        print(f"[DEBUG] 匹配帧校验范围无效: start={start_rel}, end={end_rel}")
                        return False, {}, pos
                    target = bytes(data[start + start_rel:start + end_rel + 1])
                    checksum_bytes = self.calc_checksum(target, algo)
                    byte_order = unit.get('byte_order', 'big')
                    if byte_order == 'little' and len(checksum_bytes) > 1:
                        checksum_bytes = checksum_bytes[::-1]
                    if data[pos:pos + len(checksum_bytes)] != checksum_bytes:
                        return False, {}, pos
                    pos += len(checksum_bytes)
                else:
                    print(f"[DEBUG] 未知匹配单元类型: {unit_type}")
                    return False, {}, pos
            except Exception as e:
                print(f"[DEBUG] 匹配帧单元异常: {e}")
                return False, {}, pos
        return True, captures, pos

    def _match_frame_min_len(self, match_frame):
        """计算匹配帧所需的总长度（各单元权威长度之和；校验单元按算法实际字节数）。
        match_frame 的匹配与失配「收齐」判定共用此口径。无法构成帧时返回 0。"""
        min_len = 0
        for unit in match_frame:
            if unit.get('type') == 'checksum':
                # 校验单元长度由算法决定，而非 length 字段
                algo = unit.get('algorithm', 'xor8')
                if algo == 'xor':
                    algo = 'xor8'
                elif algo == 'sum':
                    algo = 'sum8'
                spec = self.CHECKSUM_ALGORITHMS.get(algo)
                if spec and spec[0] == 'crc':
                    min_len += spec[1] // 8
                elif algo in ('sum16', 'sum16_inet'):
                    min_len += 2
                else:
                    min_len += 1
            else:
                min_len += unit.get('length', 1)
        return min_len

    def match_frame(self, data, match_frame, fmt='HEX'):
        """匹配接收数据是否符合匹配帧配置（支持滑动帧头搜索）。
        返回 (是否匹配, 捕获字典)。捕获字典以单元名称为键，保存通配符匹配到的字节。
        匹配规则：
        - 以 length 为每个单元的权威长度。
        - fixed 单元：按 length 截取数据，与解析后的期望值逐字节比较（期望值不足按已有部分比较）。
        - wildcard 单元：按 length 跳过，并将匹配到的字节存入捕获字典；可用于回传 seq 等字段。
        - 从缓冲区每个偏移位置滑动尝试匹配，容忍帧前存在噪声/上一帧残留字节。
        性能优化：若首个单元是 fixed，用 bytes.find 快速跳到候选偏移。
        """
        try:
            if not match_frame:
                return False, {}
            if not isinstance(data, bytes):
                return False, {}

            # 计算匹配帧所需最小长度，减少无谓的滑动尝试
            min_len = self._match_frame_min_len(match_frame)
            if min_len == 0 or len(data) < min_len:
                return False, {}

            last_start = len(data) - min_len

            # ---- 快速路径：若首个单元是 fixed，用 bytes.find 找候选偏移，避免逐 byte 空转 ----
            first = match_frame[0]
            head_prefix = None
            if first.get('type') == 'fixed':
                # 复用 _match_fixed_cache 的解析结果（若已在滑动分支填过）
                mcache = getattr(self, '_match_fixed_cache', None)
                if mcache is None:
                    mcache = {}
                    self._match_fixed_cache = mcache
                mkey = id(first)
                ce = mcache.get(mkey)
                if ce is not None and ce[0] == first.get('value', '') and ce[1] == fmt:
                    head_prefix = ce[2]
                else:
                    try:
                        head_prefix = self.parse_unit_value(first.get('value', ''), fmt)
                        mcache[mkey] = (first.get('value', ''), fmt, head_prefix)
                    except Exception:
                        head_prefix = None
                # 仅取 length 长度作为搜索键（超出截断，不足退化到滑动）
                if head_prefix is not None:
                    flen = first.get('length', 1)
                    if head_prefix and len(head_prefix) >= flen and flen > 0:
                        head_prefix = head_prefix[:flen]
                    else:
                        head_prefix = None

            if head_prefix:
                start = 0
                while start <= last_start:
                    idx = data.find(head_prefix, start, last_start + len(head_prefix))
                    if idx < 0 or idx > last_start:
                        return False, {}
                    is_match, captures, _ = self._match_frame_at(data, match_frame, fmt, idx)
                    if is_match:
                        return True, captures
                    start = idx + 1
                return False, {}

            # ---- 通用路径：按字节滑动 ----
            for start in range(0, last_start + 1):
                is_match, captures, _ = self._match_frame_at(data, match_frame, fmt, start)
                if is_match:
                    return True, captures
            return False, {}
        except Exception as e:
            print(f"[DEBUG] 匹配帧异常: {e}")
            import traceback
            traceback.print_exc()
            return False, {}
    
    def send_reply(self, rule, captures=None, iteration=0):
        """按规则配置发送应答帧（支持多条应答 + 累计延迟）。

        iteration 为该规则本次命中对应的轮次（从 0 开始），透传给
        build_response_frame 供「递增值」单元计算当前值。同一次命中的多条应答
        使用相同 iteration，保证同批应答内的递增字段取值一致。
        """
        try:
            format_type = rule.get('format', 'HEX')

            # 统一取多条应答：兼容旧格式（response_frame + response_delay_ms）
            responses = self._get_rule_responses(rule)
            if not responses:
                return
            
            cumulative_delay = 0
            for idx, response in enumerate(responses):
                frame = response.get('frame', [])
                delay = int(response.get('delay_ms', 0) or 0)
                cumulative_delay += max(0, delay)
                if not frame:
                    continue
                
                if cumulative_delay <= 0:
                    # 立即发送：无需拷贝，直接使用原 frame / captures
                    try:
                        data = self.build_response_frame(frame, format_type, captures or {}, iteration)
                        if data:
                            success = self.send_data(data, show_errors=False, _skip_stats=True)
                            if not success:
                                print(f"[ERROR] 自动应答#{idx + 1} 发送失败: {rule.get('name')}")
                    except Exception as e:
                        print(f"[ERROR] 应答#{idx + 1} 构造/发送异常: {e}")
                else:
                    # 延时发送：拷贝所需数据，避免延时期间被修改
                    # iteration 同样通过默认参数冻结，防止延时期间计数器变化导致取值错乱
                    import copy
                    frame_copy = copy.deepcopy(frame)
                    captures_copy = copy.deepcopy(captures) if captures else {}
                    def _do_send(f=frame_copy, c=captures_copy, i=idx, it=iteration):
                        try:
                            data = self.build_response_frame(f, format_type, c, it)
                            if data:
                                success = self.send_data(data, show_errors=False, _skip_stats=True)
                                if not success:
                                    print(f"[ERROR] 自动应答#{i + 1} 发送失败: {rule.get('name')}")
                        except Exception as e:
                            print(f"[ERROR] 应答#{i + 1} 构造/发送异常: {e}")
                    QTimer.singleShot(cumulative_delay, _do_send)
        except Exception as e:
            print(f"[ERROR] 发送应答异常: {e}")
            import traceback
            traceback.print_exc()
    
    def _precompile_rules(self):
        """预编译规则：为每条规则计算 first_byte / first_prefix 用于快速过滤。
        - first_byte: 若首个 unit 为 fixed 且可解析，取第一个字节，用于 O(1) 过滤；否则 None（表示需要滑动匹配）。
        - first_prefix: 首个 fixed unit 的完整字节前缀，供 match_frame 快速跳转（已由 match_frame 内部再解析一次，这里冗余提前算是为了避免每次 hot-path 都重复解析）。
        同时构建 self._rules_first_byte_index: dict[int, list[rule]]，first_byte=None 的规则归入 self._rules_no_prefix。
        必须在 reply_rules 变动后调用。"""
        self._rules_first_byte_index = {}
        self._rules_no_prefix = []
        self._rules_mismatch_specs = []
        for rule in self.reply_rules:
            if not rule.get('enabled', True):
                continue
            mf = rule.get('match_frame', [])
            if not mf:
                continue
            # 失配判定规格：匹配帧总长度 + 帧引导前缀（首 fixed 单元有界头部，可能为 None）
            total_len = self._match_frame_min_len(mf)
            first = mf[0]
            first_byte = None
            head = None
            if first.get('type') == 'fixed':
                fmt = rule.get('format', 'HEX')
                try:
                    raw = self.parse_unit_value(first.get('value', ''), fmt)
                    flen = first.get('length', 1)
                    if raw and flen > 0 and len(raw) >= 1:
                        first_byte = raw[0]
                        # 有界帧引导前缀仅用于在缓冲中定位帧头：只取前
                        # _MISMATCH_PREFIX_MAXLEN 字节，避开首 fixed 单元尾部随帧变化的
                        # 字段（如 AT 帧长度位 64/69），否则同类真失配帧无法被定位。
                        head = bytes(raw)[:self._MISMATCH_PREFIX_MAXLEN]
                except Exception:
                    first_byte = None
            if total_len > 0:
                self._rules_mismatch_specs.append({'head': head, 'total_len': total_len})
            if first_byte is None:
                self._rules_no_prefix.append(rule)
            else:
                self._rules_first_byte_index.setdefault(first_byte, []).append(rule)
        # 裁剪递增计数器：只保留仍存在于 reply_rules 中的规则对象
        # 规则被删除/编辑/导入替换后其计数自然清零（下次命中从起始值重新开始），
        # 同时避免 id 被 Python 回收复用后错误继承旧计数（此处已先行删除）。
        alive_ids = {id(r) for r in self.reply_rules}
        if self._reply_increment_counters:
            self._reply_increment_counters = {
                k: v for k, v in self._reply_increment_counters.items() if k in alive_ids}

    def _take_reply_iteration(self, rule):
        """取出并累加指定规则的命中次数，供应答帧「递增值」单元使用。

        返回值为本次命中对应的轮次（首次命中返回 0，即使用配置的起始值），
        随后内部计数 +1。rule 需为 self.reply_rules 中的原始对象（非快照），
        以 id() 作为 key；对象失效时由 _precompile_rules() 统一裁剪。
        全部调用均发生在 Qt 主线程（串口数据经信号投递），故无需额外加锁。
        """
        key = id(rule)
        current = self._reply_increment_counters.get(key, 0)
        # 上限保护：避免长期运行时整数无限增长（1e9 轮后回绕，对任何字节长度均等价）
        self._reply_increment_counters[key] = 0 if current >= 1000000000 else current + 1
        return current

    def _filter_candidate_rules(self, buf_bytes):
        """从当前接收缓冲区中收集可能命中的候选规则列表（保持原顺序）。
        - 若缓冲区中出现过某字节 X，则 first_byte=X 的所有规则都作为候选。
        - first_byte 无法预计算的规则（首个单元非 fixed 等）永远作为候选。
        保证与原顺序一致：直接遍历 self.reply_rules，用命中集合过滤，避免破坏用户配置的优先级顺序。"""
        if not hasattr(self, '_rules_first_byte_index'):
            self._precompile_rules()
        # 若没有任何 first_byte 索引，就退回全量
        if not self._rules_first_byte_index and not self._rules_no_prefix:
            # 缓存为空 = 没有 enabled 规则
            return []
        # 构造命中集合：出现在缓冲区的所有字节所对应的规则
        seen_bytes = set(buf_bytes)
        candidate_set = set(id(r) for r in self._rules_no_prefix)
        for b in seen_bytes:
            rules_for_b = self._rules_first_byte_index.get(b)
            if rules_for_b:
                candidate_set.update(id(r) for r in rules_for_b)
        # 按 reply_rules 顺序返回，保持优先级
        return [r for r in self.reply_rules if r.get('enabled', True) and id(r) in candidate_set]
    
    def _get_rule_responses(self, rule):
        """统一返回规则的应答帧列表 [{'frame':[...], 'delay_ms':N}, ...]。
        - 优先使用新字段 responses
        - 兼容旧字段 response_frame + response_delay_ms（作为单条）"""
        responses = rule.get('responses')
        if isinstance(responses, list) and responses:
            # 只保留合法结构
            normalized = []
            for r in responses:
                if isinstance(r, dict):
                    normalized.append({
                        'frame': r.get('frame', []) or [],
                        'delay_ms': int(r.get('delay_ms', 0) or 0),
                    })
            if normalized:
                return normalized
        # 旧格式回退
        legacy_frame = rule.get('response_frame', [])
        if legacy_frame:
            return [{'frame': legacy_frame, 'delay_ms': int(rule.get('response_delay_ms', 0) or 0)}]
        return []
    
    # 校验算法参数表：CRC 类为 (width, poly, init, refin, refout, xorout)
    # 简单校验类用特殊标记字符串处理
    CHECKSUM_ALGORITHMS = {
        # ---- 简单校验 ----
        'sum8':            ('simple', 'sum8'),
        'sum8_reverse':    ('simple', 'sum8_reverse'),
        'lrc':             ('simple', 'lrc'),
        'sum16':           ('simple', 'sum16'),
        'sum16_inet':      ('simple', 'sum16_inet'),
        'xor8':            ('simple', 'xor8'),
        # ---- CRC-8 系列 ----
        'crc8':            ('crc', 8,  0x07, 0x00, False, False, 0x00),
        'crc8_itu':        ('crc', 8,  0x07, 0x00, False, False, 0x55),
        'crc8_rohc':       ('crc', 8,  0x07, 0xFF, True,  True,  0x00),
        'crc8_maxim':      ('crc', 8,  0x31, 0x00, True,  True,  0x00),
        'crc8_wcdma':      ('crc', 8,  0x9B, 0x00, True,  True,  0x00),
        'crc8_cdma2000':   ('crc', 8,  0x9B, 0xFF, False, False, 0x00),
        # ---- CRC-16 系列 ----
        'crc16_ccitt':       ('crc', 16, 0x1021, 0x0000, True,  True,  0x0000),
        'crc16_ccitt_false': ('crc', 16, 0x1021, 0xFFFF, False, False, 0x0000),
        'crc16_xmodem':      ('crc', 16, 0x1021, 0x0000, False, False, 0x0000),
        'crc16_x25':         ('crc', 16, 0x1021, 0xFFFF, True,  True,  0xFFFF),
        'crc16_ibm':         ('crc', 16, 0x8005, 0x0000, True,  True,  0x0000),
        'crc16_usb':         ('crc', 16, 0x8005, 0xFFFF, True,  True,  0xFFFF),
        'crc16_maxim':       ('crc', 16, 0x8005, 0x0000, True,  True,  0xFFFF),
        'crc16_modbus':      ('crc', 16, 0x8005, 0xFFFF, True,  True,  0x0000),
        'crc16_dnp':         ('crc', 16, 0x3D65, 0x0000, True,  True,  0xFFFF),
        # ---- CRC-32 系列 ----
        'crc32':         ('crc', 32, 0x04C11DB7, 0xFFFFFFFF, True,  True,  0xFFFFFFFF),
        'crc32_mpeg2':   ('crc', 32, 0x04C11DB7, 0xFFFFFFFF, False, False, 0x00000000),
        'crc32_bzip2':   ('crc', 32, 0x04C11DB7, 0xFFFFFFFF, False, False, 0xFFFFFFFF),
        'crc32_posix':   ('crc', 32, 0x04C11DB7, 0x00000000, False, False, 0xFFFFFFFF),
        'crc32_jamcrc':  ('crc', 32, 0x04C11DB7, 0xFFFFFFFF, True,  True,  0x00000000),
        'crc32_zmodem':  ('crc', 32, 0x04C11DB7, 0x00000000, False, False, 0x00000000),
    }

    # 算法显示名 -> 内部 key（用于 UI 下拉与帧预览）
    CHECKSUM_LABELS = [
        ("CHECKSUM-8", 'sum8'),
        ("CHECKSUM-8/REVERSE", 'sum8_reverse'),
        ("CHECKSUM-8/LRC", 'lrc'),
        ("CHECKSUM-16", 'sum16'),
        ("CHECKSUM-16/INTERNET", 'sum16_inet'),
        ("XOR-8/BCC", 'xor8'),
        ("CRC-8", 'crc8'),
        ("CRC-8/ITU", 'crc8_itu'),
        ("CRC-8/ROHC", 'crc8_rohc'),
        ("CRC-8/MAXIM", 'crc8_maxim'),
        ("CRC-8/WCDMA", 'crc8_wcdma'),
        ("CRC-8/CDMA2000", 'crc8_cdma2000'),
        ("CRC-16/CCITT", 'crc16_ccitt'),
        ("CRC-16/CCITT-FALSE", 'crc16_ccitt_false'),
        ("CRC-16/XMODEM", 'crc16_xmodem'),
        ("CRC-16/X25", 'crc16_x25'),
        ("CRC-16/IBM", 'crc16_ibm'),
        ("CRC-16/USB", 'crc16_usb'),
        ("CRC-16/MAXIM", 'crc16_maxim'),
        ("CRC-16/MODBUS", 'crc16_modbus'),
        ("CRC-16/DNP", 'crc16_dnp'),
        ("CRC-32", 'crc32'),
        ("CRC-32/MPEG-2", 'crc32_mpeg2'),
        ("CRC-32/BZIP2", 'crc32_bzip2'),
        ("CRC-32/POSIX", 'crc32_posix'),
        ("CRC-32/JAMCRC", 'crc32_jamcrc'),
        ("CRC-32/ZMODEM", 'crc32_zmodem'),
    ]

    @staticmethod
    def _reflect(value, width):
        """按位反转 value 的低 width 位。"""
        result = 0
        for i in range(width):
            if value & (1 << i):
                result |= 1 << (width - 1 - i)
        return result

    def _crc_generic(self, data, width, poly, init, refin, refout, xorout):
        """通用 CRC 计算（逐位算法），支持任意宽度/参数。
        （曾尝试查表加速，因边界正确性风险回退。CRC 单次开销 <10μs，非热点。）"""
        topbit = 1 << (width - 1)
        mask = (1 << width) - 1
        crc = init & mask
        for byte in data:
            b = self._reflect(byte, 8) if refin else byte
            crc ^= (b << (width - 8)) & mask
            for _ in range(8):
                if crc & topbit:
                    crc = ((crc << 1) ^ poly) & mask
                else:
                    crc = (crc << 1) & mask
        if refout:
            crc = self._reflect(crc, width)
        crc ^= xorout
        return crc & mask

    def calc_checksum(self, data, algo):
        """计算 data 的校验值，返回 bytes（大端）。
        algo 为 CHECKSUM_ALGORITHMS 中的 key。未知算法返回空字节串。"""
        spec = self.CHECKSUM_ALGORITHMS.get(algo)
        if spec is None:
            print(f"[DEBUG] 未知校验算法: {algo}")
            return b''

        if spec[0] == 'simple':
            kind = spec[1]
            if kind == 'sum8':
                return bytes([sum(data) & 0xFF])
            elif kind == 'sum8_reverse':
                # 求和后按位取反（部分设备的反向校验和）
                return bytes([(~sum(data)) & 0xFF])
            elif kind == 'lrc':
                # LRC：求和取二进制补码
                return bytes([(-sum(data)) & 0xFF])
            elif kind == 'sum16':
                s = sum(data) & 0xFFFF
                return bytes([(s >> 8) & 0xFF, s & 0xFF])
            elif kind == 'sum16_inet':
                # Internet 校验和：16位累加+进位回卷后取反
                total = 0
                for i in range(0, len(data), 2):
                    if i + 1 < len(data):
                        total += (data[i] << 8) | data[i + 1]
                    else:
                        total += data[i] << 8
                while total >> 16:
                    total = (total & 0xFFFF) + (total >> 16)
                s = (~total) & 0xFFFF
                return bytes([(s >> 8) & 0xFF, s & 0xFF])
            elif kind == 'xor8':
                x = 0
                for b in data:
                    x ^= b
                return bytes([x & 0xFF])
            return b''
        elif spec[0] == 'crc':
            _, width, poly, init, refin, refout, xorout = spec
            crc = self._crc_generic(data, width, poly, init, refin, refout, xorout)
            nbytes = width // 8
            return crc.to_bytes(nbytes, 'big')
        return b''

    def build_response_frame(self, response_frame, fmt='HEX', captures=None, iteration=0):
        """根据应答帧配置构造应答字节串。
        支持的单元类型：
        - fixed：固定值，按 length 组帧（值不足右侧补 0，超出按 length 截断）。
        - ref：引用匹配帧中通配符捕获到的值（通过 value 指定捕获单元名称）。
        - increment：递增值，每次命中该规则后自动累加，按 length 字节表示。
        - checksum：对指定范围计算校验和（algorithm: xor/sum），追加 1 字节。
        captures 为 match_frame 返回的捕获字典。
        iteration 为该规则已命中次数（从 0 开始），供 increment 单元计算当前值。"""
        if captures is None:
            captures = {}
        data = bytearray()
        # 记录每个单元在 data 中的起止位置，供 checksum 范围计算使用
        unit_spans = []
        for idx, unit in enumerate(response_frame):
            unit_type = unit.get('type', 'fixed')
            length = unit.get('length', 1)
            start = len(data)

            if unit_type == 'fixed':
                value = unit.get('value', '')
                # 用外部字典缓存 (id(unit)) -> (value, fmt, length, raw)
                # 避免把 bytes 塞进 unit dict（否则 json.dump 会失败）
                cache = getattr(self, '_fixed_unit_bytes_cache', None)
                if cache is None:
                    cache = {}
                    self._fixed_unit_bytes_cache = cache
                key = id(unit)
                cached = cache.get(key)
                if (cached is not None
                        and cached[0] == value
                        and cached[1] == fmt
                        and cached[2] == length):
                    raw = cached[3]
                else:
                    try:
                        raw = self.parse_unit_value(value, fmt)
                    except Exception as e:
                        print(f"[ERROR] 应答固定值解析失败: {value} (格式={fmt}), 错误: {e}")
                        raw = b''
                    # 以 length 为权威长度：不足补 0，超出截断
                    if len(raw) < length:
                        raw = raw + b'\x00' * (length - len(raw))
                    elif len(raw) > length:
                        raw = raw[:length]
                    cache[key] = (value, fmt, length, raw)
                data.extend(raw)
            elif unit_type == 'ref':
                ref_name = unit.get('value', '')
                ref_bytes = captures.get(ref_name, b'')
                if not ref_bytes:
                    print(f"[DEBUG] 应答引用单元未找到捕获值: {ref_name}")
                data.extend(ref_bytes)
            elif unit_type == 'increment':
                data.extend(self._build_increment_bytes(unit, iteration, fmt))
            elif unit_type == 'checksum':
                algo = unit.get('algorithm', 'xor8')
                # 兼容旧配置的算法名
                if algo == 'xor':
                    algo = 'xor8'
                elif algo == 'sum':
                    algo = 'sum8'
                # 校验范围：crc_start / crc_end 为字节索引（含端点）。
                # 默认对当前已组帧的全部字节(0 到 校验位前)计算。
                crc_start = unit.get('crc_start', 0)
                crc_end = unit.get('crc_end', -1)
                end = len(data) - 1 if (crc_end is None or crc_end < 0) else crc_end
                start_i = max(0, crc_start)
                end_i = min(len(data) - 1, end)
                if start_i > end_i:
                    print(f"[DEBUG] 校验范围无效: start={start_i}, end={end_i}")
                    target = b''
                else:
                    target = bytes(data[start_i:end_i + 1])
                checksum_bytes = self.calc_checksum(target, algo)
                # 字节序：高位在前(big，默认) / 低位在前(little)
                byte_order = unit.get('byte_order', 'big')
                if byte_order == 'little' and len(checksum_bytes) > 1:
                    checksum_bytes = checksum_bytes[::-1]
                data.extend(checksum_bytes)
            else:
                print(f"[DEBUG] 未知应答单元类型: {unit_type}，已跳过")

            unit_spans.append((start, len(data)))

        return bytes(data)
    
    def add_to_history(self, data):
        hex_str = ' '.join(f'{b:02X}' for b in data)
        if hex_str not in self.send_history:
            self.send_history.append(hex_str)
            if len(self.send_history) > MAX_HISTORY_COUNT:
                self.send_history.pop(0)
    
    def load_config(self):
        print("[DEBUG] 加载配置")
        settings = QSettings("UartTool", "UartAssistant")
        try:
            geometry = settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
            
            last_port = settings.value("last_port")
            if last_port:
                index = self.port_combo.findText(last_port)
                if index >= 0:
                    self.port_combo.setCurrentIndex(index)
            
            last_baudrate = settings.value("last_baudrate", str(DEFAULT_BAUDRATE))
            if last_baudrate:
                index = self.baudrate_combo.findText(last_baudrate)
                if index >= 0:
                    self.baudrate_combo.setCurrentIndex(index)
            
            # 加载日志配置
            self.save_receive_log = settings.value("save_receive_log", True, type=bool)
            # 系统日志默认关闭，且只认齿轮后门写入的新键 console_log_backdoor；
            # 历史遗留的 save_console_log 键（旧版本默认 True）一律忽略并清除，
            # 以保证升级后“首次启动绝不自动生成系统日志”。
            self.save_console_log = settings.value("console_log_backdoor", False, type=bool)
            if settings.contains("save_console_log"):
                settings.remove("save_console_log")
            self.log_save_path = settings.value("log_save_path", "", type=str)
            self.use_custom_log_name = settings.value("use_custom_log_name", False, type=bool)
            self.custom_log_name = settings.value("custom_log_name", "", type=str)
            
            # 加载显示设置：换行间隔（静默期），默认 33ms
            try:
                bt = int(settings.value("buffer_timeout", 33, type=int) or 33)
                if 1 <= bt <= 10000:
                    self.buffer_timeout = bt
            except Exception:
                pass

            # 加载失配统计口径：默认精确判定（按帧头+总长），仅在复选框已创建后同步 UI
            try:
                self.auto_reply_head_match = settings.value(
                    "auto_reply_head_match", True, type=bool)
            except Exception:
                self.auto_reply_head_match = True
            if hasattr(self, 'head_match_check'):
                # 屏蔽信号再 setChecked：加载时不触发 toggled（避免初始化阶段误存配置）
                self.head_match_check.blockSignals(True)
                try:
                    self.head_match_check.setChecked(self.auto_reply_head_match)
                finally:
                    self.head_match_check.blockSignals(False)
            
            # 更新当前日志状态标签
            if hasattr(self, 'current_log_label'):
                self.update_current_log_label()
            
            print(f"[DEBUG] 日志配置加载完成: save_receive_log={self.save_receive_log}, save_console_log={self.save_console_log}, log_save_path={self.log_save_path}")
        except Exception as e:
            print(f"[DEBUG] 加载配置异常: {e}")
            pass
    
    def save_config(self):
        print("[DEBUG] 保存配置")
        settings = QSettings("UartTool", "UartAssistant")
        try:
            settings.setValue("geometry", self.saveGeometry())
            settings.setValue("last_port", self.port_combo.currentText())
            settings.setValue("last_baudrate", self.baudrate_combo.currentText())
            
            # 保存日志配置
            settings.setValue("save_receive_log", self.save_receive_log)
            # 系统日志开关只写齿轮后门键，不再使用旧的 save_console_log 键
            settings.setValue("console_log_backdoor", bool(self.save_console_log))
            settings.setValue("log_save_path", self.log_save_path)
            settings.setValue("use_custom_log_name", self.use_custom_log_name)
            settings.setValue("custom_log_name", self.custom_log_name)
            
            # 保存显示设置：换行间隔
            try:
                settings.setValue("buffer_timeout", int(getattr(self, 'buffer_timeout', 33)))
            except Exception:
                pass

            # 保存失配统计口径（默认 True=按帧头+总长精确判定）
            settings.setValue("auto_reply_head_match", bool(self.auto_reply_head_match))
            
            print(f"[DEBUG] 日志配置已保存")
        except Exception as e:
            print(f"[DEBUG] 保存配置异常: {e}")
            pass
    
    def setup_shortcuts(self):
        print("[DEBUG] 设置快捷键")
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.toggle_serial)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(lambda: self.send_data())
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.clear_receive)
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(lambda: self.zoom_font(1))
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(lambda: self.zoom_font(-1))
    
    def zoom_font(self, delta):
        font = self.receive_text.font()
        size = font.pointSize() + delta
        if 6 <= size <= 20:
            font.setPointSize(size)
            self.receive_text.setFont(font)
            self.send_text.setFont(font)
            print(f"[DEBUG] 字体大小改变: {size}")
    
    def start_speed_timer(self):
        self.speed_timer.timeout.connect(self.update_speed)
        self.speed_timer.start(1000)
        print("[DEBUG] 速度定时器已启动")
    
    def update_speed(self):
        if self.start_time and self.is_open:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if elapsed > 0:
                speed = self.receive_count / elapsed
                if hasattr(self, 'temp_status_label'):
                    self.temp_status_label.setText(
                        f"{self._tr('接收：')}{self.receive_count}{self._tr('字节')} | {self._tr('发送：')}{self.send_count}{self._tr('字节')} | "
                        f"{self.receive_packet_count}/{self.send_packet_count} | "
                        f"{self._tr('应答失配：')}{self.auto_reply_timeout_count} | "
                        f"{speed:.1f} B/s"
                    )
    
    def update_status_bar(self):
        if hasattr(self, 'temp_status_label'):
            self.temp_status_label.setText(self._tr("就绪"))
    
    def closeEvent(self, event):
        print("[DEBUG] 窗口关闭事件")
        self.save_config()
        if self.is_open:
            self.close_serial()
        self.close_log_file()
        event.accept()
        print("[DEBUG] 程序退出")


class LogSettingsDialog(QDialog):
    """日志设置对话框：勾选是否保存日志、配置路径与文件名，可运行时修改"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle(tr("日志设置"))
        self.setMinimumWidth(480)
        self.init_ui()

    def init_ui(self):
        from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QCheckBox,
                                     QLineEdit, QPushButton, QLabel, QGroupBox)
        p = self.parent_window
        layout = QVBoxLayout(self)

        # 当前自定义文件名（留空则自动命名）
        self._custom_name = p.custom_log_name or ''

        # 保存开关
        self.save_receive_check = QCheckBox(tr("保存接收日志"))
        self.save_receive_check.setChecked(p.save_receive_log)
        layout.addWidget(self.save_receive_check)

        # 保存路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel(tr("保存路径:")))
        self.path_edit = QLineEdit()
        self.path_edit.setText(p.log_save_path)
        self.path_edit.setPlaceholderText(tr("留空则使用默认日志目录"))
        path_layout.addWidget(self.path_edit)
        browse_btn = QPushButton(tr("浏览..."))
        browse_btn.setMaximumWidth(70)
        browse_btn.clicked.connect(self.on_browse)
        path_layout.addWidget(browse_btn)
        open_btn = QPushButton(tr("打开文件夹"))
        open_btn.setMaximumWidth(90)
        open_btn.clicked.connect(self.on_open_folder)
        path_layout.addWidget(open_btn)
        layout.addLayout(path_layout)

        # 文件名反馈（只读，浏览时在保存对话框里填写；留空则按 时间_端口.log 自动命名）
        self.name_label = QLabel()
        self.name_label.setStyleSheet("color: #888;")
        self._update_name_label()
        layout.addWidget(self.name_label)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton(tr("确定"))
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QPushButton(tr("取消"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _update_name_label(self):
        name = (self._custom_name or '').strip()
        if name:
            self.name_label.setText(f"{tr('文件名:')} {name}")
        else:
            self.name_label.setText(tr("文件名: (自动命名：时间_端口.log)"))

    def on_browse(self):
        from PyQt5.QtWidgets import QFileDialog
        start_dir = self.path_edit.text().strip() or self.parent_window.get_default_log_dir()
        suggested = os.path.join(start_dir, self._custom_name) if self._custom_name else start_dir
        file_path, _ = QFileDialog.getSaveFileName(
            self, tr("保存日志"), suggested,
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            if directory:
                self.path_edit.setText(directory)
            self._custom_name = filename
            self._update_name_label()

    def on_open_folder(self):
        from PyQt5.QtWidgets import QMessageBox
        path = self.path_edit.text() or self.parent_window.get_default_log_dir()
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self, tr("警告"), tr("日志文件夹不存在"))

    def get_config(self):
        name = (self._custom_name or '').strip()
        return {
            'save_receive_log': self.save_receive_check.isChecked(),
            'save_console_log': self.parent_window.save_console_log,
            'log_save_path': self.path_edit.text().strip(),
            'use_custom_log_name': bool(name),
            'custom_log_name': name,
        }


class RuleConfigDialog(QDialog):
    def __init__(self, parent, rule=None):
        super().__init__(parent)
        self.setWindowTitle(tr("规则配置"))
        self.setMinimumSize(800, 500)
        self.rule = rule.copy() if rule else {
            'name': '新规则', 'enabled': True, 'match_frame': [],
            'response_frame': [], 'response_delay_ms': 0,
            'format': 'HEX'
        }
        print("[DEBUG] 规则配置对话框初始化")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(tr("规则名称:")))
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.rule.get('name', ''))
        name_layout.addWidget(self.name_edit)
        
        # 添加格式选择
        name_layout.addWidget(QLabel(tr("  数据格式:")))
        self.format_combo = QComboBox()
        self.format_combo.addItem("HEX")
        self.format_combo.addItem("文本")
        self.format_combo.setCurrentText(self.rule.get('format', 'HEX'))
        name_layout.addWidget(self.format_combo)
        name_layout.addStretch()
        
        layout.addLayout(name_layout)
        
        # 匹配帧
        match_group = QGroupBox(tr("匹配帧配置"))
        match_layout = QVBoxLayout(match_group)
        self.match_units_widget = QWidget()
        self.match_units_layout = QVBoxLayout(self.match_units_widget)
        self.match_units_layout.addStretch()
        match_scroll_area = QScrollArea()
        match_scroll_area.setWidget(self.match_units_widget)
        match_scroll_area.setWidgetResizable(True)
        match_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        match_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        match_scroll_area.setMaximumHeight(300)
        match_layout.addWidget(match_scroll_area)
        add_match_btn = QPushButton(tr("添加匹配单元"))
        add_match_btn.clicked.connect(self.add_match_unit)
        add_match_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        add_match_btn_layout = QHBoxLayout()
        add_match_btn_layout.addWidget(add_match_btn)
        add_match_btn_layout.addStretch()
        match_layout.addLayout(add_match_btn_layout)
        for unit in self.rule.get('match_frame', []):
            self.add_match_unit(unit)
        layout.addWidget(match_group)
        
        # 应答帧（支持多条，每条独立配置延迟）
        response_group = QGroupBox(tr("应答帧配置"))
        response_layout = QVBoxLayout(response_group)
        self.response_frames_widget = QWidget()
        self.response_frames_layout = QVBoxLayout(self.response_frames_widget)
        self.response_frames_layout.setContentsMargins(0, 0, 0, 0)
        self.response_frames_layout.setSpacing(6)
        self.response_frames_layout.addStretch()
        response_scroll_area = QScrollArea()
        response_scroll_area.setWidget(self.response_frames_widget)
        response_scroll_area.setWidgetResizable(True)
        response_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        response_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        response_scroll_area.setMaximumHeight(360)
        response_layout.addWidget(response_scroll_area)
        # 保留 self.response_units_layout 供 add_response_unit 默认使用（指向第一条应答帧内部单元列表）
        self.response_units_layout = None

        add_response_frame_btn = QPushButton(tr("添加应答帧"))
        add_response_frame_btn.clicked.connect(lambda: self.add_response_frame_group())
        add_response_frame_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        add_frame_btn_layout = QHBoxLayout()
        add_frame_btn_layout.addWidget(add_response_frame_btn)
        add_frame_btn_layout.addStretch()
        response_layout.addLayout(add_frame_btn_layout)
        layout.addWidget(response_group)
        
        # 用统一后的应答列表填充（自动兼容旧格式）
        existing_responses = self._get_existing_responses(self.rule)
        if existing_responses:
            for resp in existing_responses:
                self.add_response_frame_group(resp)
        else:
            self.add_response_frame_group()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton(tr("确定"))
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QPushButton(tr("取消"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def add_match_unit(self, unit=None):
        unit_data = unit or {'name': '', 'length': 1, 'type': 'fixed', 'value': ''}
        unit_widget = QWidget()
        unit_layout = QHBoxLayout(unit_widget)
        unit_layout.setContentsMargins(0, 0, 0, 0)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText(tr("名称"))
        name_edit.setText(unit_data.get('name', ''))
        name_edit.setMaximumWidth(100)
        unit_layout.addWidget(name_edit)
        
        length_spin = QSpinBox()
        length_spin.setRange(1, MAX_FRAME_UNIT_LENGTH)
        length_spin.setValue(unit_data.get('length', 1))
        length_spin.setMaximumWidth(70)
        unit_layout.addWidget(length_spin)
        
        type_combo = QComboBox()
        type_combo.addItem(tr("固定值"), "fixed")
        type_combo.addItem(tr("通配符"), "wildcard")
        type_combo.addItem(tr("校验"), "checksum")
        cur_type = unit_data.get('type', 'fixed')
        type_index = type_combo.findData(cur_type)
        if type_index >= 0:
            type_combo.setCurrentIndex(type_index)
        unit_layout.addWidget(type_combo)
        
        # 校验算法下拉（仅 checksum 类型可用，包含全部校验算法）
        algo_combo = QComboBox()
        for label, key in UartAssistantWindow.CHECKSUM_LABELS:
            algo_combo.addItem(label, key)
        algo_combo.setMaximumWidth(150)
        # 兼容旧配置算法名
        saved_algo = unit_data.get('algorithm', 'xor8')
        if saved_algo == 'xor':
            saved_algo = 'xor8'
        elif saved_algo == 'sum':
            saved_algo = 'sum8'
        algo_index = algo_combo.findData(saved_algo)
        if algo_index >= 0:
            algo_combo.setCurrentIndex(algo_index)
        unit_layout.addWidget(algo_combo)
        
        # 校验范围：起始字节索引、结束字节索引（-1 表示到校验位前一字节）
        start_spin = QSpinBox()
        start_spin.setRange(0, 255)
        start_spin.setValue(unit_data.get('crc_start', 0))
        start_spin.setMaximumWidth(55)
        start_spin.setPrefix(tr("起:"))
        start_spin.setToolTip("校验起始字节索引(从0开始)")
        unit_layout.addWidget(start_spin)
        
        end_spin = QSpinBox()
        end_spin.setRange(-1, 255)
        end_spin.setValue(unit_data.get('crc_end', -1))
        end_spin.setMaximumWidth(60)
        end_spin.setPrefix(tr("止:"))
        end_spin.setToolTip("校验结束字节索引(含)，-1 表示到校验位前一字节")
        unit_layout.addWidget(end_spin)
        
        # 校验字节序：高位在前(大端)/低位在前(小端)，仅多字节校验有意义
        order_combo = QComboBox()
        order_combo.addItem(tr("高位在前"), "big")
        order_combo.addItem(tr("低位在前"), "little")
        order_combo.setMaximumWidth(95)
        order_combo.setToolTip("多字节校验值的字节顺序：高位在前(大端)或低位在前(小端)")
        saved_order = unit_data.get('byte_order', 'big')
        order_index = order_combo.findData(saved_order)
        if order_index >= 0:
            order_combo.setCurrentIndex(order_index)
        unit_layout.addWidget(order_combo)
        
        value_edit = QLineEdit()
        value_edit.setPlaceholderText(tr("值 (HEX 或 文本)"))
        value_edit.setText(unit_data.get('value', ''))
        unit_layout.addWidget(value_edit, 1)
        
        del_btn = QPushButton(tr("删除"))
        del_btn.clicked.connect(lambda: self.match_units_layout.removeWidget(unit_widget) or unit_widget.deleteLater())
        unit_layout.addWidget(del_btn)
        
        def update_controls():
            t = type_combo.currentData()
            if t == 'fixed':
                value_edit.setEnabled(True)
                value_edit.setPlaceholderText(tr("值 (HEX 或 文本)"))
                algo_combo.setVisible(False)
                start_spin.setVisible(False)
                end_spin.setVisible(False)
                order_combo.setVisible(False)
                length_spin.setEnabled(True)
            elif t == 'wildcard':
                value_edit.setEnabled(False)
                value_edit.setPlaceholderText(tr("任意值（按长度跳过）"))
                algo_combo.setVisible(False)
                start_spin.setVisible(False)
                end_spin.setVisible(False)
                order_combo.setVisible(False)
                length_spin.setEnabled(True)
            elif t == 'checksum':
                value_edit.setEnabled(False)
                value_edit.setPlaceholderText(tr("校验自动比对"))
                algo_combo.setVisible(True)
                start_spin.setVisible(True)
                end_spin.setVisible(True)
                order_combo.setVisible(True)
                length_spin.setEnabled(False)
        
        type_combo.currentIndexChanged.connect(lambda _: update_controls())
        update_controls()
        
        def get_unit_data():
            t = type_combo.currentData()
            data = {'name': name_edit.text(), 'length': length_spin.value(),
                    'type': t, 'value': value_edit.text()}
            # 仅校验类型才保存算法和校验范围，避免 fixed/wildcard 单元导出冗余字段
            if t == 'checksum':
                data['algorithm'] = algo_combo.currentData()
                data['crc_start'] = start_spin.value()
                data['crc_end'] = end_spin.value()
                data['byte_order'] = order_combo.currentData()
            return data
        
        unit_widget.get_data = get_unit_data
        self.match_units_layout.insertWidget(self.match_units_layout.count() - 1, unit_widget)

    def add_response_unit(self, unit=None, target_layout=None):
        unit_data = unit or {'name': '', 'length': 1, 'type': 'fixed', 'value': ''}
        # 允许指定要插入的应答帧单元容器（用于多条应答帧）
        if target_layout is None:
            # 兜底：使用最后一个应答帧分组的单元容器
            groups = getattr(self, 'response_frame_groups', [])
            if groups:
                target_layout = groups[-1]['units_layout']
            else:
                target_layout = self.response_units_layout
        unit_widget = QWidget()
        unit_layout = QHBoxLayout(unit_widget)
        unit_layout.setContentsMargins(0, 0, 0, 0)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText(tr("名称"))
        name_edit.setText(unit_data.get('name', ''))
        name_edit.setMaximumWidth(100)
        unit_layout.addWidget(name_edit)
        
        length_spin = QSpinBox()
        length_spin.setRange(1, MAX_FRAME_UNIT_LENGTH)
        length_spin.setValue(unit_data.get('length', 1))
        length_spin.setMaximumWidth(70)
        unit_layout.addWidget(length_spin)
        
        type_combo = QComboBox()
        type_combo.addItem(tr("固定值"), "fixed")
        type_combo.addItem(tr("引用匹配值"), "ref")
        type_combo.addItem(tr("递增值"), "increment")
        type_combo.addItem(tr("校验"), "checksum")
        # 根据已有数据设置当前类型
        cur_type = unit_data.get('type', 'fixed')
        type_index = type_combo.findData(cur_type)
        if type_index >= 0:
            type_combo.setCurrentIndex(type_index)
        unit_layout.addWidget(type_combo)
        
        # 校验算法下拉（仅 checksum 类型可用，包含全部校验算法）
        algo_combo = QComboBox()
        for label, key in UartAssistantWindow.CHECKSUM_LABELS:
            algo_combo.addItem(label, key)
        algo_combo.setMaximumWidth(150)
        # 兼容旧配置算法名
        saved_algo = unit_data.get('algorithm', 'xor8')
        if saved_algo == 'xor':
            saved_algo = 'xor8'
        elif saved_algo == 'sum':
            saved_algo = 'sum8'
        algo_index = algo_combo.findData(saved_algo)
        if algo_index >= 0:
            algo_combo.setCurrentIndex(algo_index)
        unit_layout.addWidget(algo_combo)
        
        # 校验范围：起始字节索引、结束字节索引（-1 表示到校验位前一字节）
        start_spin = QSpinBox()
        start_spin.setRange(0, 255)
        start_spin.setValue(unit_data.get('crc_start', 0))
        start_spin.setMaximumWidth(55)
        start_spin.setPrefix(tr("起:"))
        start_spin.setToolTip("校验起始字节索引(从0开始)")
        unit_layout.addWidget(start_spin)
        
        end_spin = QSpinBox()
        end_spin.setRange(-1, 255)
        end_spin.setValue(unit_data.get('crc_end', -1))
        end_spin.setMaximumWidth(60)
        end_spin.setPrefix(tr("止:"))
        end_spin.setToolTip("校验结束字节索引(含)，-1 表示到校验位前一字节")
        unit_layout.addWidget(end_spin)
        
        # 校验/递增值字节序：高位在前(大端)/低位在前(小端)，仅多字节时有意义
        order_combo = QComboBox()
        order_combo.addItem(tr("高位在前"), "big")
        order_combo.addItem(tr("低位在前"), "little")
        order_combo.setMaximumWidth(95)
        order_combo.setToolTip("多字节校验值/递增值的字节顺序：高位在前(大端)或低位在前(小端)")
        saved_order = unit_data.get('byte_order', 'big')
        order_index = order_combo.findData(saved_order)
        if order_index >= 0:
            order_combo.setCurrentIndex(order_index)
        unit_layout.addWidget(order_combo)

        # 步进值：仅递增值单元使用，默认 1，允许负数实现递减
        step_spin = QSpinBox()
        step_spin.setRange(-1000000, 1000000)
        step_spin.setValue(int(unit_data.get('step', 1)))
        step_spin.setPrefix(tr("步进") + ":")
        step_spin.setMaximumWidth(110)
        step_spin.setToolTip(tr("该规则每命中一次时递增值的步进量，默认1"))
        unit_layout.addWidget(step_spin)

        # 数值模式：仅递增值使用
        num_mode_combo = QComboBox()
        num_mode_combo.addItem(tr("普通数值"), "normal")
        num_mode_combo.addItem(tr("BCD十进制"), "bcd")
        num_mode_combo.setMaximumWidth(110)
        num_mode_combo.setToolTip(tr("递增值的数值模式：普通数值按二进制加；BCD 按十进制加(HEX 显示跳过 A~F)"))
        saved_num_mode = unit_data.get('num_mode', 'normal')
        idx_nm = num_mode_combo.findData(saved_num_mode)
        if idx_nm >= 0:
            num_mode_combo.setCurrentIndex(idx_nm)
        unit_layout.addWidget(num_mode_combo)

        value_edit = QLineEdit()
        value_edit.setText(unit_data.get('value', ''))
        unit_layout.addWidget(value_edit, 1)

        del_btn = QPushButton(tr("删除"))
        del_btn.clicked.connect(lambda: target_layout.removeWidget(unit_widget) or unit_widget.deleteLater())
        unit_layout.addWidget(del_btn)

        def update_controls():
            """按当前单元类型切换各控件的可见性与可编辑状态，避免无关字段干扰。"""
            t = type_combo.currentData()
            if t == 'fixed':
                value_edit.setEnabled(True)
                value_edit.setPlaceholderText(tr("值 (HEX 或 文本)"))
                algo_combo.setVisible(False)
                start_spin.setVisible(False)
                end_spin.setVisible(False)
                order_combo.setVisible(False)
                step_spin.setVisible(False)
                num_mode_combo.setVisible(False)
                length_spin.setEnabled(True)
                length_spin.setMaximum(MAX_FRAME_UNIT_LENGTH)
            elif t == 'ref':
                value_edit.setEnabled(True)
                value_edit.setPlaceholderText(tr("引用的匹配单元名称"))
                algo_combo.setVisible(False)
                start_spin.setVisible(False)
                end_spin.setVisible(False)
                order_combo.setVisible(False)
                step_spin.setVisible(False)
                num_mode_combo.setVisible(False)
                length_spin.setEnabled(False)
            elif t == 'increment':
                value_edit.setEnabled(True)
                value_edit.setPlaceholderText(tr("起始值（十进制或0x前缀）"))
                algo_combo.setVisible(False)
                start_spin.setVisible(False)
                end_spin.setVisible(False)
                order_combo.setVisible(True)
                step_spin.setVisible(True)
                num_mode_combo.setVisible(True)
                length_spin.setEnabled(True)
                length_spin.setMaximum(MAX_INCREMENT_UNIT_LENGTH)
            elif t == 'checksum':
                value_edit.setEnabled(False)
                value_edit.setPlaceholderText(tr("校验自动计算"))
                algo_combo.setVisible(True)
                start_spin.setVisible(True)
                end_spin.setVisible(True)
                order_combo.setVisible(True)
                step_spin.setVisible(False)
                num_mode_combo.setVisible(False)
                length_spin.setEnabled(False)

        type_combo.currentIndexChanged.connect(lambda _: update_controls())
        update_controls()

        def get_unit_data():
            t = type_combo.currentData()
            data = {'name': name_edit.text(), 'length': length_spin.value(),
                    'type': t, 'value': value_edit.text()}
            # 仅按类型保存专属字段，避免 fixed/ref 单元导出冗余字段
            if t == 'checksum':
                data['algorithm'] = algo_combo.currentData()
                data['crc_start'] = start_spin.value()
                data['crc_end'] = end_spin.value()
                data['byte_order'] = order_combo.currentData()
            elif t == 'increment':
                data['byte_order'] = order_combo.currentData()
                data['step'] = step_spin.value()
                data['num_mode'] = num_mode_combo.currentData()
            return data

        unit_widget.get_data = get_unit_data
        target_layout.insertWidget(target_layout.count() - 1, unit_widget)
    
    def _get_existing_responses(self, rule):
        """把规则中的应答帧统一成 [{'frame':[...], 'delay_ms':N}] 结构，兼容旧格式。"""
        responses = rule.get('responses')
        if isinstance(responses, list) and responses:
            normalized = []
            for r in responses:
                if isinstance(r, dict):
                    normalized.append({
                        'frame': r.get('frame', []) or [],
                        'delay_ms': int(r.get('delay_ms', 0) or 0),
                    })
            if normalized:
                return normalized
        legacy_frame = rule.get('response_frame', [])
        if legacy_frame:
            return [{'frame': legacy_frame, 'delay_ms': int(rule.get('response_delay_ms', 0) or 0)}]
        return []
    
    def add_response_frame_group(self, response=None):
        """新增一条"应答帧 #N"分组：分组内包含独立的单元列表 + 应答延迟。"""
        response = response or {'frame': [], 'delay_ms': 0}
        if not hasattr(self, 'response_frame_groups'):
            self.response_frame_groups = []
        
        group_box = QGroupBox()
        group_layout = QVBoxLayout(group_box)
        group_layout.setContentsMargins(6, 6, 6, 6)
        group_layout.setSpacing(4)
        
        # 头部：延迟设置 + 删除按钮
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(tr("应答延迟 (ms):")))
        delay_spin = QSpinBox()
        delay_spin.setRange(0, 600000)
        delay_spin.setValue(int(response.get('delay_ms', 0) or 0))
        delay_spin.setMaximumWidth(120)
        header_layout.addWidget(delay_spin)
        header_layout.addStretch()
        remove_btn = QPushButton(tr("删除本条应答"))
        remove_btn.clicked.connect(lambda: self._remove_response_frame_group(group_box))
        header_layout.addWidget(remove_btn)
        group_layout.addLayout(header_layout)
        
        # 单元列表容器
        units_widget = QWidget()
        units_layout = QVBoxLayout(units_widget)
        units_layout.setContentsMargins(0, 0, 0, 0)
        units_layout.setSpacing(3)
        units_layout.addStretch()
        group_layout.addWidget(units_widget)
        
        add_unit_btn = QPushButton(tr("添加应答单元"))
        add_unit_btn.clicked.connect(lambda: self.add_response_unit(target_layout=units_layout))
        add_unit_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        add_unit_btn_layout = QHBoxLayout()
        add_unit_btn_layout.addWidget(add_unit_btn)
        add_unit_btn_layout.addStretch()
        group_layout.addLayout(add_unit_btn_layout)
        
        # 填充已有单元
        for unit in response.get('frame', []) or []:
            self.add_response_unit(unit, target_layout=units_layout)
        
        # 记录到列表：group_box 与其内部 units_layout / delay_spin 一一对应
        self.response_frame_groups.append({
            'group_box': group_box,
            'units_layout': units_layout,
            'delay_spin': delay_spin,
        })
        # 插到 stretch 之前
        insert_at = self.response_frames_layout.count() - 1
        self.response_frames_layout.insertWidget(insert_at, group_box)
        self._refresh_response_group_titles()
    
    def _remove_response_frame_group(self, group_box):
        """删除某条应答帧分组"""
        # 至少保留一条
        if len(getattr(self, 'response_frame_groups', [])) <= 1:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, tr("提示"), tr("至少需要保留一条应答帧"))
            return
        self.response_frame_groups = [g for g in self.response_frame_groups if g['group_box'] is not group_box]
        self.response_frames_layout.removeWidget(group_box)
        group_box.deleteLater()
        self._refresh_response_group_titles()
    
    def _refresh_response_group_titles(self):
        """刷新每个应答帧分组的标题为"应答帧 #N"。"""
        for i, g in enumerate(getattr(self, 'response_frame_groups', [])):
            g['group_box'].setTitle(f"{tr('应答帧 #')}{i + 1}")
    
    def _collect_response_frames(self):
        """收集所有应答帧数据：返回 [{'frame':[...], 'delay_ms':N}, ...]"""
        from PyQt5.QtWidgets import QWidget as _QW
        results = []
        for g in getattr(self, 'response_frame_groups', []):
            units_layout = g['units_layout']
            frame_units = []
            for i in range(units_layout.count()):
                widget = units_layout.itemAt(i).widget()
                if isinstance(widget, _QW) and hasattr(widget, 'get_data'):
                    frame_units.append(widget.get_data())
            results.append({
                'frame': frame_units,
                'delay_ms': g['delay_spin'].value(),
            })
        return results
    
    def _calc_value_bytes_len(self, value, fmt):
        """按格式计算 value 的字节长度，解析失败返回 None"""
        try:
            if fmt == '文本':
                text = value
                text = text.replace('\\r', '\r').replace('\\n', '\n')
                text = text.replace('\\t', '\t').replace('\\\\', '\\')
                return len(text.encode('utf-8'))
            else:
                return len(bytes.fromhex(value.replace(' ', '')))
        except Exception:
            return None

    def _validate_units(self, frame, fmt, frame_label):
        """校验帧中各 fixed 单元的 value 字节数与 length 是否一致。
        返回错误信息列表（为空表示通过）。"""
        errors = []
        for idx, unit in enumerate(frame):
            if unit.get('type') != 'fixed':
                continue
            name = unit.get('name', '') or f'单元{idx + 1}'
            length = unit.get('length', 1)
            value = unit.get('value', '')
            actual = self._calc_value_bytes_len(value, fmt)
            if actual is None:
                errors.append(f"{frame_label}「{name}」的值无法按{fmt}格式解析：{value}")
            elif actual != length:
                errors.append(
                    f"{frame_label}「{name}」字节长度错误：长度设为 {length}，"
                    f"但值实际为 {actual} 字节（值：{value}）")
        return errors

    def _validate_increment_units(self, frame, frame_label):
        """校验帧中各 increment 单元的起始值：必须可解析、非负，且不超过 length 字节的可表示范围。

        frame_label 用于错误提示中定位所属帧（如「发送帧单元配置」/「应答数据 #1」）。
        返回错误信息列表（为空表示通过）。
        """
        errors = []
        for idx, unit in enumerate(frame):
            if unit.get('type') != 'increment':
                continue
            name = unit.get('name', '') or f'单元{idx + 1}'
            length = unit.get('length', 1)
            if length > MAX_INCREMENT_UNIT_LENGTH:
                errors.append(
                    f"{frame_label}「{name}」递增值单元长度 {length} 超过上限 "
                    f"{MAX_INCREMENT_UNIT_LENGTH} 字节（数值宽度无实际意义），请改小")
                continue
            raw = (unit.get('value', '') or '').strip()
            try:
                start_val = int(raw, 16) if raw.lower().startswith('0x') else (int(raw) if raw else 0)
            except Exception:
                errors.append(f"{frame_label}「{name}」{tr('起始值格式无效')}：{raw}")
                continue
            if start_val < 0:
                errors.append(f"{frame_label}「{name}」{tr('起始值超出字节长度可表示的最大值')}（值：{raw}，长度：{length}）")
                continue
            if unit.get('num_mode', 'normal') == 'bcd':
                max_bcd = 10 ** (length * 2)
                if start_val >= max_bcd:
                    errors.append(f"{frame_label}「{name}」{tr('起始值超出字节长度可表示的最大值')}（值：{raw}，长度：{length}，BCD 最大值 {max_bcd - 1}）")
            elif start_val >= (1 << (length * 8)):
                errors.append(f"{frame_label}「{name}」{tr('起始值超出字节长度可表示的最大值')}（值：{raw}，长度：{length}）")
        return errors

    def accept(self):
        from PyQt5.QtWidgets import QWidget, QMessageBox
        fmt = self.format_combo.currentText()

        match_frame = []
        for i in range(self.match_units_layout.count()):
            widget = self.match_units_layout.itemAt(i).widget()
            if isinstance(widget, QWidget) and hasattr(widget, 'get_data'):
                match_frame.append(widget.get_data())
        
        # 收集所有应答帧数据（支持多条）
        responses = self._collect_response_frames()
        
        # 纠错机制：校验固定值单元的字节长度是否与填写的值一致
        errors = self._validate_units(match_frame, fmt, tr("匹配条件"))
        for idx, resp in enumerate(responses):
            resp_label = f"{tr('应答数据')} #{idx + 1}"
            errors += self._validate_units(resp.get('frame', []), fmt, resp_label)
            # 应答帧支持递增值单元，需额外校验其起始值范围
            errors += self._validate_increment_units(resp.get('frame', []), resp_label)
        if errors:
            QMessageBox.warning(self, tr("单元字节长度错误"),
                                tr("请修正以下单元后再保存：\n\n") + "\n".join(errors))
            return  # 不关闭对话框，留给用户修改
        
        self.rule['name'] = self.name_edit.text()
        self.rule['format'] = fmt
        self.rule['match_frame'] = match_frame
        self.rule['responses'] = responses
        # 兼容旧字段：写回第一条应答，保证老版本读取时仍能工作
        first = responses[0] if responses else {'frame': [], 'delay_ms': 0}
        self.rule['response_frame'] = first.get('frame', [])
        self.rule['response_delay_ms'] = int(first.get('delay_ms', 0) or 0)
        
        super().accept()


class BatchFrameConfigDialog(RuleConfigDialog):
    """批量发送帧配置对话框：复用自动应答匹配帧单元配置逻辑。"""
    def __init__(self, parent, rule=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(tr("发送帧配置"))
        self.setMinimumSize(800, 420)
        self.rule = rule.copy() if rule else {'match_frame': [], 'format': 'HEX'}
        self.frame_units = self.rule.get('match_frame', [])
        self.frame_format = self.rule.get('format', 'HEX')
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(tr("发送格式:")))
        self.format_combo = QComboBox()
        self.format_combo.addItem("HEX")
        self.format_combo.addItem("文本")
        self.format_combo.setCurrentText(self.rule.get('format', 'HEX'))
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        frame_group = QGroupBox(tr("发送帧单元配置"))
        frame_layout = QVBoxLayout(frame_group)
        self.match_units_widget = QWidget()
        self.match_units_layout = QVBoxLayout(self.match_units_widget)
        self.match_units_layout.addStretch()
        frame_scroll_area = QScrollArea()
        frame_scroll_area.setWidget(self.match_units_widget)
        frame_scroll_area.setWidgetResizable(True)
        frame_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        frame_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        frame_scroll_area.setMaximumHeight(300)
        frame_layout.addWidget(frame_scroll_area)

        add_frame_btn = QPushButton(tr("添加帧单元"))
        add_frame_btn.clicked.connect(self.add_match_unit)
        add_frame_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        add_btn_layout = QHBoxLayout()
        add_btn_layout.addWidget(add_frame_btn)
        add_btn_layout.addStretch()
        frame_layout.addLayout(add_btn_layout)

        for unit in self.rule.get('match_frame', []):
            self.add_match_unit(unit)
        layout.addWidget(frame_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton(tr("确定"))
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QPushButton(tr("取消"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def accept(self):
        from PyQt5.QtWidgets import QWidget, QMessageBox
        fmt = self.format_combo.currentText()
        frame_units = []
        for i in range(self.match_units_layout.count()):
            widget = self.match_units_layout.itemAt(i).widget()
            if isinstance(widget, QWidget) and hasattr(widget, 'get_data'):
                frame_units.append(widget.get_data())

        errors = self._validate_units(frame_units, fmt, tr("发送帧单元配置"))
        # 追加校验：递增值起始值必须可解析且不超过 length 字节可表示的最大值
        errors += self._validate_increment_units(frame_units, tr("发送帧单元配置"))
        if errors:
            QMessageBox.warning(self, tr("单元字节长度错误"),
                                tr("请修正以下单元后再保存：\n\n") + "\n".join(errors))
            return

        self.frame_units = frame_units
        self.frame_format = fmt
        super(RuleConfigDialog, self).accept()

    def add_match_unit(self, unit=None):
        """批量发送场景专用：额外支持"递增值"单元类型。"""
        unit_data = unit or {'name': '', 'length': 1, 'type': 'fixed', 'value': ''}
        unit_widget = QWidget()
        unit_layout = QHBoxLayout(unit_widget)
        unit_layout.setContentsMargins(0, 0, 0, 0)

        name_edit = QLineEdit()
        name_edit.setPlaceholderText(tr("名称"))
        name_edit.setText(unit_data.get('name', ''))
        name_edit.setMaximumWidth(100)
        unit_layout.addWidget(name_edit)

        length_spin = QSpinBox()
        length_spin.setRange(1, MAX_FRAME_UNIT_LENGTH)
        length_spin.setValue(unit_data.get('length', 1))
        length_spin.setMaximumWidth(70)
        unit_layout.addWidget(length_spin)

        type_combo = QComboBox()
        type_combo.addItem(tr("固定值"), "fixed")
        type_combo.addItem(tr("通配符"), "wildcard")
        type_combo.addItem(tr("校验"), "checksum")
        type_combo.addItem(tr("递增值"), "increment")
        cur_type = unit_data.get('type', 'fixed')
        type_index = type_combo.findData(cur_type)
        if type_index >= 0:
            type_combo.setCurrentIndex(type_index)
        unit_layout.addWidget(type_combo)

        # 校验算法（仅 checksum）
        algo_combo = QComboBox()
        for label, key in UartAssistantWindow.CHECKSUM_LABELS:
            algo_combo.addItem(label, key)
        algo_combo.setMaximumWidth(150)
        saved_algo = unit_data.get('algorithm', 'xor8')
        if saved_algo == 'xor':
            saved_algo = 'xor8'
        elif saved_algo == 'sum':
            saved_algo = 'sum8'
        algo_index = algo_combo.findData(saved_algo)
        if algo_index >= 0:
            algo_combo.setCurrentIndex(algo_index)
        unit_layout.addWidget(algo_combo)

        # 校验范围
        start_spin = QSpinBox()
        start_spin.setRange(0, 255)
        start_spin.setValue(unit_data.get('crc_start', 0))
        start_spin.setMaximumWidth(55)
        start_spin.setPrefix(tr("起:"))
        start_spin.setToolTip("校验起始字节索引(从0开始)")
        unit_layout.addWidget(start_spin)

        end_spin = QSpinBox()
        end_spin.setRange(-1, 255)
        end_spin.setValue(unit_data.get('crc_end', -1))
        end_spin.setMaximumWidth(60)
        end_spin.setPrefix(tr("止:"))
        end_spin.setToolTip("校验结束字节索引(含)，-1 表示到校验位前一字节")
        unit_layout.addWidget(end_spin)

        # 字节序：校验和递增值共用
        order_combo = QComboBox()
        order_combo.addItem(tr("高位在前"), "big")
        order_combo.addItem(tr("低位在前"), "little")
        order_combo.setMaximumWidth(95)
        order_combo.setToolTip("多字节校验/递增值的字节顺序：高位在前(大端)或低位在前(小端)")
        saved_order = unit_data.get('byte_order', 'big')
        order_index = order_combo.findData(saved_order)
        if order_index >= 0:
            order_combo.setCurrentIndex(order_index)
        unit_layout.addWidget(order_combo)

        # 步进值：仅递增值单元使用，默认 1
        step_spin = QSpinBox()
        step_spin.setRange(-1000000, 1000000)
        step_spin.setValue(int(unit_data.get('step', 1)))
        step_spin.setPrefix(tr("步进") + ":")
        step_spin.setMaximumWidth(110)
        step_spin.setToolTip("每一轮批量发送时递增值的步进量，默认1")
        unit_layout.addWidget(step_spin)

        # 数值模式：仅递增值使用
        #   normal —— 普通数值（默认），HEX 显示会经过 09→0A→...→0F→10
        #   bcd    —— BCD 十进制，HEX 显示跳过 0A~0F，形如 09→10→...→99→00
        num_mode_combo = QComboBox()
        num_mode_combo.addItem(tr("普通数值"), "normal")
        num_mode_combo.addItem(tr("BCD十进制"), "bcd")
        num_mode_combo.setMaximumWidth(110)
        num_mode_combo.setToolTip(tr("递增值的数值模式：普通数值按二进制加；BCD 按十进制加(HEX 显示跳过 A~F)"))
        saved_num_mode = unit_data.get('num_mode', 'normal')
        idx_nm = num_mode_combo.findData(saved_num_mode)
        if idx_nm >= 0:
            num_mode_combo.setCurrentIndex(idx_nm)
        unit_layout.addWidget(num_mode_combo)

        value_edit = QLineEdit()
        value_edit.setPlaceholderText(tr("值 (HEX 或 文本)"))
        value_edit.setText(unit_data.get('value', ''))
        unit_layout.addWidget(value_edit, 1)

        del_btn = QPushButton(tr("删除"))
        del_btn.clicked.connect(lambda: self.match_units_layout.removeWidget(unit_widget) or unit_widget.deleteLater())
        unit_layout.addWidget(del_btn)

        def update_controls():
            t = type_combo.currentData()
            if t == 'fixed':
                value_edit.setEnabled(True)
                value_edit.setPlaceholderText(tr("值 (HEX 或 文本)"))
                algo_combo.setVisible(False)
                start_spin.setVisible(False)
                end_spin.setVisible(False)
                order_combo.setVisible(False)
                step_spin.setVisible(False)
                num_mode_combo.setVisible(False)
                length_spin.setEnabled(True)
                length_spin.setMaximum(MAX_FRAME_UNIT_LENGTH)
            elif t == 'wildcard':
                value_edit.setEnabled(False)
                value_edit.setPlaceholderText(tr("任意值（按长度跳过）"))
                algo_combo.setVisible(False)
                start_spin.setVisible(False)
                end_spin.setVisible(False)
                order_combo.setVisible(False)
                step_spin.setVisible(False)
                num_mode_combo.setVisible(False)
                length_spin.setEnabled(True)
                length_spin.setMaximum(MAX_FRAME_UNIT_LENGTH)
            elif t == 'checksum':
                value_edit.setEnabled(False)
                value_edit.setPlaceholderText(tr("校验自动比对"))
                algo_combo.setVisible(True)
                start_spin.setVisible(True)
                end_spin.setVisible(True)
                order_combo.setVisible(True)
                step_spin.setVisible(False)
                num_mode_combo.setVisible(False)
                length_spin.setEnabled(False)
            elif t == 'increment':
                value_edit.setEnabled(True)
                value_edit.setPlaceholderText(tr("起始值（十进制或0x前缀）"))
                algo_combo.setVisible(False)
                start_spin.setVisible(False)
                end_spin.setVisible(False)
                order_combo.setVisible(True)
                step_spin.setVisible(True)
                num_mode_combo.setVisible(True)
                length_spin.setEnabled(True)
                length_spin.setMaximum(MAX_INCREMENT_UNIT_LENGTH)

        type_combo.currentIndexChanged.connect(lambda _: update_controls())
        update_controls()

        def get_unit_data():
            t = type_combo.currentData()
            data = {'name': name_edit.text(), 'length': length_spin.value(),
                    'type': t, 'value': value_edit.text()}
            if t == 'checksum':
                data['algorithm'] = algo_combo.currentData()
                data['crc_start'] = start_spin.value()
                data['crc_end'] = end_spin.value()
                data['byte_order'] = order_combo.currentData()
            elif t == 'increment':
                data['byte_order'] = order_combo.currentData()
                data['step'] = step_spin.value()
                data['num_mode'] = num_mode_combo.currentData()
            return data

        unit_widget.get_data = get_unit_data
        self.match_units_layout.insertWidget(self.match_units_layout.count() - 1, unit_widget)


class HelpDialog(QDialog):
    """使用说明对话框：左侧模块列表，右侧显示对应说明。"""

    HELP_SECTIONS = [
        ("串口与接收", "receive"),
        ("单次发送", "single"),
        ("批量发送", "batch"),
        ("发送帧配置（含递增值/BCD）", "frame"),
        ("自动应答（多条应答帧）", "reply"),
        ("快捷指令", "quick"),
        ("语言切换与快捷键", "misc"),
    ]

    HELP_TEXTS = {
        "receive": """<h3>串口与接收</h3>
<ul>
<li><b>端口/波特率/数据位/停止位/校验位/流控制</b>：请按照对端设备一致的参数配置。</li>
<li>点击 <b>端口下拉框</b> 会自动重新扫描 COM 端口。</li>
<li>点击 <b>打开串口</b> 建立连接，红灯变绿灯并显示已连接。</li>
<li>接收显示：<b>文本 / HEX</b> 复选框互斥且至少保留一个勾选；勾选 <b>时间戳</b> 会在每条消息前显示时间。</li>
<li><b>自动换行</b>：勾选后按窗口宽度自适应换行；不勾选时长行水平滚动查看。</li>
<li>快捷键 <b>Ctrl+L</b> 清空接收区，<b>Ctrl+O</b> 打开/关闭串口。</li>
</ul>""",
        "single": """<h3>单次发送</h3>
<ul>
<li>在"单次发送"标签页输入内容后点击 <b>发送</b> 或按 <b>Ctrl+S</b>。</li>
<li>发送格式 <b>文本 / HEX</b> 互斥且至少保留一个勾选。HEX 模式下输入形如 <code>01 02 A0</code>，空格可选。</li>
<li>勾选 <b>显示发送</b> 才会把发送内容回显到接收区。</li>
<li>右下角会实时显示当前输入的字节长度。</li>
</ul>""",
        "batch": """<h3>批量发送</h3>
<ul>
<li>勾选 <b>启用批量发送</b>，配置 <b>发送间隔（ms）</b> 和 <b>次数</b>（或勾选 <b>无限循环</b>）。</li>
<li>指令列表：<b>添加指令 / 编辑 / 删除 / 导入 / 导出</b>；每行的 <b>选中</b> 可控制该条本轮是否启用。</li>
<li>右键点击某行可 <b>上移 / 下移</b>，调整发送顺序。</li>
<li>每条指令有两种构造方式：
  <ol>
    <li>直接填 <b>指令内容</b>（按 文本 / HEX 格式发送）。</li>
    <li>点击 <b>添加规则 / 编辑规则</b> 打开"发送帧配置"，用帧单元方式构造（推荐用于校验、递增值等场景）。</li>
  </ol>
</li>
<li>批量发送指令自动保存到本地，重启不丢失。</li>
</ul>""",
        "frame": """<h3>发送帧配置（帧单元）</h3>
<p>用于批量发送和快捷指令构造复杂帧。支持的单元类型：</p>
<ul>
<li><b>固定值</b>：按数据格式（文本 / HEX）填写具体字节，长度必须匹配。</li>
<li><b>通配符</b>：占位用；在发送场景下按长度填 <code>0x00</code>。</li>
<li><b>校验</b>：算法有 <code>sum8 / sum8_reverse / lrc / sum16 / sum16_inet / xor8 / 多种 CRC</code>；可设置校验范围（起始/结束字节索引，-1 表示到校验位前一字节）与字节序（大端/小端）。</li>
<li><b>递增值</b>（批量发送每完成一轮后累加；自动应答按该规则每命中一次累加）。字段：
  <ul>
    <li><b>起始值</b>：填十进制数（例如 <code>0</code>、<code>10</code>）或 <code>0x</code> 前缀十六进制（例如 <code>0x0A</code>）。</li>
    <li><b>步进</b>：默认 1，允许负数用于递减。</li>
    <li><b>字节长度</b>：占几个字节。</li>
    <li><b>字节序</b>：多字节时高位在前 / 低位在前。</li>
    <li><b>数值模式</b>：
      <ul>
        <li><b>普通数值</b>（默认）：按普通整数 +步进；HEX 显示可能是 <code>00→01→…→09→0A→0B→…→FF→00</code>。</li>
        <li><b>BCD十进制</b>：按十进制 +步进；HEX 显示 <b>跳过 A~F</b>，形如 <code>00→01→…→09→10→11→…→99→00</code>，常用于 BCD 编码的计数/包序号。</li>
      </ul>
    </li>
    <li>溢出后自动回 0 循环。</li>
  </ul>
</li>
</ul>
<p><b>提示：</b> 长度校验基于实际字节数——文本模式按 UTF-8 字节数，HEX 模式按十六进制字节数（<code>22</code> = 1 字节）。从批量发送/快捷指令进入"添加规则"时默认按 HEX 打开。</p>""",
        "reply": """<h3>自动应答（多条应答帧）</h3>
<ul>
<li>勾选 <b>启用自动应答</b>，然后 <b>添加规则</b>。</li>
<li><b>匹配帧</b>：可用 <b>固定值 / 通配符（可命名以便应答引用）/ 校验</b>组合。</li>
<li><b>应答帧配置</b>：
  <ul>
    <li>支持 <b>多条应答帧</b>，点击 <b>添加应答帧</b> 追加。</li>
    <li>每条应答独立配置 <b>应答延迟（ms）</b>：<b>累计间隔式</b> —— 第 N 条实际发送时刻 = 前 N 条延迟之和（从收到匹配帧开始计时）。</li>
    <li>单元类型：固定值、<b>引用匹配值</b>（回显匹配帧中命名的通配符字段）、<b>递增值</b>（该规则每命中一次自动累加，可用于应答包序号/计数器；支持起始值、步进、字节序与普通数值 / BCD十进制模式）、校验（自动计算）。</li>
    <li><b>递增值说明</b>：计数按规则独立维护，首次命中使用起始值；同一次命中的多条应答帧使用同一个值；规则被修改、删除或重新导入后计数会从起始值重新开始；程序重启不保留计数。</li>
  </ul>
</li>
<li>右键点击规则行可 <b>上移 / 下移</b> 调整匹配优先级；靠前的规则会优先命中。</li>
<li>规则支持导入 / 导出 JSON，自动保存到本地。</li>
</ul>""",
        "quick": """<h3>快捷指令</h3>
<ul>
<li>与批量发送互补，用于一键发送常用单条指令。</li>
<li>表格每行提供 <b>编辑</b> 和 <b>发送</b> 两个按钮，点击 <b>发送</b> 立即单次发送。</li>
<li>添加/编辑时可点击 <b>添加规则 / 编辑规则</b> 使用与批量发送相同的"发送帧配置"（递增值在快捷指令中不会累加，因为不是循环发送）。</li>
<li>右键 <b>上移 / 下移</b>；支持 <b>导入 / 导出</b> JSON；自动保存到本地。</li>
</ul>""",
        "misc": """<h3>语言切换与快捷键</h3>
<ul>
<li>点击右上角齿轮 <b>⚙</b> → 语言，可在 <b>中文 / English</b> 之间实时切换，选择会保存到配置。</li>
<li>快捷键：
  <ul>
    <li><b>Ctrl+O</b>：打开 / 关闭串口</li>
    <li><b>Ctrl+S</b>：发送数据（单次发送）</li>
    <li><b>Ctrl+L</b>：清空接收区</li>
    <li><b>Ctrl++</b> / <b>Ctrl+-</b>：放大 / 缩小字体</li>
  </ul>
</li>
<li>配置文件位置：<code>C:\\Users\\&lt;用户名&gt;\\.uart_tool\\</code>（含 config / rules / batch_commands / quick_commands 等 JSON）。</li>
</ul>""",
    }

    HELP_TEXTS_EN = {
        "receive": """<h3>Serial &amp; Receive</h3>
<ul>
<li>Configure Port / Baud / Data bits / Stop bits / Parity / Flow control to match your device.</li>
<li><b>Refresh</b> re-scans COM ports; <b>Open Port</b> connects.</li>
<li>Display mode: <b>Text / HEX</b> are mutually exclusive and at least one must remain checked; enable <b>Timestamp</b> for time prefix.</li>
<li><b>Word Wrap</b>: wrap to window width when checked; otherwise long lines scroll horizontally.</li>
<li>Shortcuts: <b>Ctrl+L</b> clear receive area, <b>Ctrl+O</b> open/close port.</li>
</ul>""",
        "single": """<h3>Single Send</h3>
<ul>
<li>Type in the "Single Send" tab and click <b>Send</b> or press <b>Ctrl+S</b>.</li>
<li><b>Text / HEX</b> are mutually exclusive; in HEX enter like <code>01 02 A0</code>.</li>
<li>Check <b>Echo Send</b> to also show what was sent in the receive area.</li>
<li>Byte length is shown live at the bottom right.</li>
</ul>""",
        "batch": """<h3>Batch Send</h3>
<ul>
<li>Enable <b>Batch Send</b>, set <b>Interval (ms)</b> and <b>Count</b> (or check <b>Infinite Loop</b>).</li>
<li>Command list: <b>Add / Edit / Delete / Import / Export</b>. Row <b>Selected</b> toggles per-round enable.</li>
<li>Right-click a row for <b>Move Up / Move Down</b>.</li>
<li>Two ways to compose each command:
  <ol>
    <li>Fill <b>Command Content</b> directly (sent as Text / HEX).</li>
    <li>Click <b>Add Rule / Edit Rule</b> to open "Send Frame Config" and build with frame units (recommended for checksums / increment).</li>
  </ol>
</li>
<li>Batch commands persist across app restarts.</li>
</ul>""",
        "frame": """<h3>Send Frame Config (Frame Units)</h3>
<p>Used to build complex frames for Batch Send and Quick Commands. Supported unit types:</p>
<ul>
<li><b>Fixed</b>: bytes per data format (Text / HEX). Length must match value bytes.</li>
<li><b>Wildcard</b>: placeholder; filled with <code>0x00</code> * length when sending.</li>
<li><b>Checksum</b>: sum8 / sum8_reverse / lrc / sum16 / sum16_inet / xor8 / CRCs, with range (start/end index, -1 = up to previous byte) and byte order.</li>
<li><b>Increment</b> (Batch Send only): auto-increases per round. Fields:
  <ul>
    <li><b>Start Value</b>: decimal (e.g. <code>0</code>, <code>10</code>) or <code>0x</code> prefix hex (e.g. <code>0x0A</code>).</li>
    <li><b>Step</b>: default 1, negative allowed to decrement.</li>
    <li><b>Length</b>: byte count.</li>
    <li><b>Byte order</b>: big / little endian for multi-byte.</li>
    <li><b>Number Mode</b>:
      <ul>
        <li><b>Normal</b> (default): plain integer + step; HEX may go <code>00→01→…→09→0A→0B→…→FF→00</code>.</li>
        <li><b>BCD Decimal</b>: decimal + step, HEX skips A~F, e.g. <code>00→01→…→09→10→11→…→99→00</code>. Handy for BCD counters / packet sequences.</li>
      </ul>
    </li>
    <li>Wraps to 0 on overflow.</li>
  </ul>
</li>
</ul>
<p><b>Tip:</b> Length check uses actual bytes — Text uses UTF-8 bytes, HEX uses hex bytes (<code>22</code> = 1 byte). "Add Rule" from Batch/Quick opens in HEX by default.</p>""",
        "reply": """<h3>Auto Reply (Multiple Responses)</h3>
<ul>
<li>Enable <b>Auto Reply</b>, then <b>Add Rule</b>.</li>
<li><b>Match Frame</b>: use combinations of <b>Fixed / Wildcard (nameable for reference) / Checksum</b>.</li>
<li><b>Response Frame Configuration</b>:
  <ul>
    <li>Supports <b>multiple responses</b>. Click <b>Add Response Frame</b> to append more.</li>
    <li>Each response has its own <b>Response Delay (ms)</b>: <b>cumulative</b> — the Nth response is sent at <em>sum(delays[0..N])</em> after match arrival.</li>
    <li>Units: Fixed, <b>Reference Match Value</b> (echo named wildcard from match), Checksum (auto-computed).</li>
  </ul>
</li>
<li>Right-click a rule row for <b>Move Up / Move Down</b>; earlier rules win on match.</li>
<li>Rules can be imported / exported as JSON and persist to disk.</li>
</ul>""",
        "quick": """<h3>Quick Commands</h3>
<ul>
<li>Complements Batch Send — one-click single send of frequently used commands.</li>
<li>Each row has <b>Edit</b> and <b>Send</b> buttons.</li>
<li>Add / edit supports <b>Add Rule / Edit Rule</b> using the same Send Frame Config (increment does not roll here since it's not a loop).</li>
<li>Right-click <b>Move Up / Move Down</b>; <b>Import / Export</b> JSON; persists automatically.</li>
</ul>""",
        "misc": """<h3>Language &amp; Shortcuts</h3>
<ul>
<li>Click the top-right gear <b>⚙</b> → <b>Language</b> to switch between <b>中文 / English</b> at runtime; the choice is saved.</li>
<li>Shortcuts:
  <ul>
    <li><b>Ctrl+O</b>: Open / Close Port</li>
    <li><b>Ctrl+S</b>: Send (Single Send)</li>
    <li><b>Ctrl+L</b>: Clear receive area</li>
    <li><b>Ctrl++</b> / <b>Ctrl+-</b>: Font size up / down</li>
  </ul>
</li>
<li>Config directory: <code>C:\\Users\\&lt;user&gt;\\.uart_tool\\</code> (config / rules / batch_commands / quick_commands JSON).</li>
</ul>""",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("使用说明"))
        self.resize(820, 560)
        from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QListWidget, QTextBrowser, QDialogButtonBox
        main_layout = QHBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(220)
        for title_key, _key in self.HELP_SECTIONS:
            self.list_widget.addItem(tr(title_key))
        main_layout.addWidget(self.list_widget)

        right_layout = QVBoxLayout()
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        right_layout.addWidget(self.browser, 1)

        btn_box = QDialogButtonBox(QDialogButtonBox.Close)
        btn_box.rejected.connect(self.reject)
        btn_box.accepted.connect(self.accept)
        right_layout.addWidget(btn_box)
        main_layout.addLayout(right_layout, 1)

        self.list_widget.currentRowChanged.connect(self._on_section_changed)
        self.list_widget.setCurrentRow(0)

    def _on_section_changed(self, row):
        if row < 0 or row >= len(self.HELP_SECTIONS):
            return
        key = self.HELP_SECTIONS[row][1]
        text_map = self.HELP_TEXTS_EN if CURRENT_LANG == 'en' else self.HELP_TEXTS
        self.browser.setHtml(text_map.get(key, ''))


def main():
    # 重定向 print 到控制台（不通过logging）
    class PrintLogger:
        def write(self, message):
            if message.strip():
                # 使用原始stdout避免递归，添加None检查
                if sys.__stdout__ is not None:
                    try:
                        sys.__stdout__.write(message)
                    except:
                        pass
        def flush(self):
            # 添加None检查
            if sys.__stdout__ is not None:
                try:
                    sys.__stdout__.flush()
                except:
                    pass
    
    sys.stdout = PrintLogger()
    
    print("[DEBUG] 程序启动")
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = UartAssistantWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
