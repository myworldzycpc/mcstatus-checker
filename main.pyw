# ------------------------- 检查 Python 版本 (Check Python version) -------------------------
import sys
if sys.version_info < (3, 10):
    from tkinter import messagebox
    messagebox.showerror('Python版本过低 (Python version too low)', 'Python版本过低，请升级到3.10或以上版本后重试。\nPython version too low, please upgrade to 3.10 or above to retry.')
    sys.exit()

# ------------------------- 检查依赖包 (Check dependencies) -------------------------
try:
    import PyQt5
    import mcstatus
except ImportError:
    import os
    from tkinter import messagebox
    import subprocess
    import sys

    # 改进依赖安装流程 (Improved dependency installation process)
    response = messagebox.askyesno(
        '缺少依赖 (Missing dependencies)',
        '缺少依赖包，请在命令行下运行 pip install PyQt5 mcstatus 后重试。\nMissing dependencies, please run "pip install PyQt5 mcstatus" in the command line and retry.\n\n'
        '点击"是"安装依赖包，点击"否"退出程序。\nClick "Yes" to install dependencies, click "No" to exit the program.'
    )

    if response:
        try:
            os.system('pip install PyQt5 mcstatus && echo 依赖安装成功 && timeout /t 5')

            # 检查安装是否成功 (Check installation success)
            import PyQt5
            import mcstatus
            messagebox.showinfo('提示 (Information)', '依赖安装成功。\nDependencies installed successfully.')
        except ImportError:
            messagebox.showerror('缺少依赖 (Missing dependencies)', '安装失败，请在命令行下运行 pip install PyQt5 mcstatus 手动安装。\nInstallation failed, please run "pip install PyQt5 mcstatus" manually in the command line.')
            sys.exit()
    else:
        sys.exit()

# ------------------------- 导入依赖包 (Import dependencies) -------------------------
import base64
import os
import sys
import json
import glob
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QSize, QLocale
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap
from mcstatus import JavaServer
from mcstatus.status_response import JavaStatusResponse
import logging

# 常量定义 (Constants)
DEFAULT_SETTINGS = {
    "auto_check": True,
    "icon_list_size": "32x32",
    "icon_detail_size": "64x64",
    "list_row_size": "multi",
    "language": "system"  # 新增：默认使用系统语言
}

COLOR_ONLINE = QColor(220, 255, 220)  # 浅绿色
COLOR_OFFLINE = QColor(255, 220, 220)  # 浅红色
COLOR_CHECKING = QColor(255, 255, 200)  # 浅黄色
COLOR_UNCHECKED = QColor(220, 220, 220)  # 灰色

# 配置日志系统 (Configure logging system)


def setup_logging():
    log_formatter = logging.Formatter(
        '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    )

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 文件日志处理器 (File log handler)
    file_handler = logging.FileHandler('mcstatus.log', mode='a')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    # 控制台日志处理器 (Console log handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)


setup_logging()
logger = logging.getLogger(__name__)


class I18nManager:
    """国际化管理类 (Internationalization manager class)"""

    def __init__(self):
        self.languages = {}  # 语言字典: 语言代码 -> 语言名称
        self.current_lang = None
        self.lang_data = {}
        self.default_lang = "en_us"  # 默认语言

        # 加载内置语言
        self.load_builtin_languages()

        # 加载外部语言包
        self.load_external_language_packs()

    def load_builtin_languages(self):
        """加载内置语言"""
        # 内置中文简体
        self.languages["zh_cn"] = "简体中文"
        self.lang_data["zh_cn"] = {
            "app_title": "Minecraft 服务器状态检查器",
            "menu_file": "文件",
            "menu_file_log": "日志",
            "menu_file_run_dir": "运行目录",
            "menu_file_lang_dir": "语言目录",
            "menu_file_exit": "退出",
            "menu_options": "选项",
            "menu_options_auto_check": "自动获取状态",
            "menu_options_icon": "图标",
            "menu_options_icon_list": "列表",
            "menu_options_icon_detail": "详细信息",
            "menu_options_icon_none": "不显示",
            "menu_options_list_row": "列表显示行数",
            "menu_options_list_row_single": "单行",
            "menu_options_list_row_single_no_motd": "单行（无MOTD）",
            "menu_options_list_row_multi": "多行",
            "menu_language": "语言",
            "menu_language_system": "系统默认",
            "menu_help": "帮助",
            "menu_help_about": "关于",
            "button_add_server": "添加服务器",
            "button_remove_server": "删除服务器",
            "button_refresh": "刷新状态",
            "button_refresh_all": "全部刷新",
            "dialog_add_server": "添加服务器",
            "dialog_add_server_address": "输入服务器地址:",
            "dialog_add_server_name": "输入显示名称(可选):",
            "dialog_edit_server": "编辑服务器",
            "dialog_edit_server_name": "显示名称:",
            "dialog_edit_server_address": "服务器地址:",
            "confirm_delete_server": "确认删除",
            "confirm_delete_server_msg": '确定要删除服务器 "{0}" 吗?',
            "server_status_online": "在线",
            "server_status_unknown": "未查询",
            "server_status_checking": "查询中...",
            "server_status_error": "错误",
            "server_details_title": "服务器详细信息",
            "server_details_name": "{0}",
            "server_details_address": "服务器地址",
            "server_details_not_checked": "未查询服务器状态",
            "server_details_status": "状态",
            "server_details_latency": "延迟",
            "server_details_version": "版本",
            "server_details_protocol": "协议",
            "server_details_players": "在线玩家",
            "server_details_motd": "MOTD",
            "server_details_players_list": "在线玩家列表",
            "server_details_players_none": "无",
            "server_details_raw_data": "原始数据",
            "about_title": "关于",
            "about_text": """
            <h2>Minecraft 服务器状态检查器</h2>
            <p>版本: 1.0.0</p>
            <p>作者: myworldzycpc</p>
            <p>许可证: MIT</p>
            <p>GitHub: <a href="https://github.com/myworldzycpc/mcstatus-checker">https://github.com/myworldzycpc/mcstatus-checker</a></p>
            <p>这是一个用于检查Minecraft Java版服务器状态的小工具。</p>
            """,
            "error_log_open": "无法打开日志文件: {0}",
            "error_log_not_found": "日志文件不存在。",
            "error_run_dir_open": "无法打开目录: {0}",
            "error_lang_dir_open": "无法打开目录: {0}",
            "error_run_dir_not_found": "运行目录不存在。",
            "error_lang_dir_not_found": "语言目录不存在。",
            "server_already_exists": "服务器 {0} 已存在，是否仍要添加？"
        }

        # 内置英文
        self.languages["en_us"] = "English (US)"
        self.lang_data["en_us"] = {
            "app_title": "Minecraft Server Status Checker",
            "menu_file": "File",
            "menu_file_log": "Log",
            "menu_file_run_dir": "Run Directory",
            "menu_file_lang_dir": "Language Directory",
            "menu_file_exit": "Exit",
            "menu_options": "Options",
            "menu_options_auto_check": "Auto Refresh Status",
            "menu_options_icon": "Icons",
            "menu_options_icon_list": "List",
            "menu_options_icon_detail": "Details",
            "menu_options_icon_none": "None",
            "menu_options_list_row": "List Display Style",
            "menu_options_list_row_single": "Single Line",
            "menu_options_list_row_single_no_motd": "Single Line (No MOTD)",
            "menu_options_list_row_multi": "Multi Line",
            "menu_language": "Language",
            "menu_language_system": "System Default",
            "menu_help": "Help",
            "menu_help_about": "About",
            "button_add_server": "Add Server",
            "button_remove_server": "Remove Server",
            "button_refresh": "Refresh Status",
            "button_refresh_all": "Refresh All",
            "dialog_add_server": "Add Server",
            "dialog_add_server_address": "Enter server address:",
            "dialog_add_server_name": "Enter display name (optional):",
            "dialog_edit_server": "Edit Server",
            "dialog_edit_server_name": "Display Name:",
            "dialog_edit_server_address": "Server Address:",
            "confirm_delete_server": "Confirm Deletion",
            "confirm_delete_server_msg": "Are you sure you want to delete server '{0}'?",
            "server_status_online": "Online",
            "server_status_unknown": "Not Checked",
            "server_status_checking": "Checking...",
            "server_status_error": "Error",
            "server_details_title": "Server Details",
            "server_details_name": "{0}",
            "server_details_address": "Server Address",
            "server_details_not_checked": "Server status not checked",
            "server_details_status": "Status",
            "server_details_latency": "Latency",
            "server_details_version": "Version",
            "server_details_protocol": "Protocol",
            "server_details_players": "Players",
            "server_details_motd": "MOTD",
            "server_details_players_list": "Player List",
            "server_details_players_none": "None",
            "server_details_raw_data": "Raw Data",
            "about_title": "About",
            "about_text": """
            <h2>Minecraft Server Status Checker</h2>
            <p>Version: 1.0.0</p>
            <p>Author: myworldzycpc</p>
            <p>License: MIT</p>
            <p>GitHub: <a href="https://github.com/myworldzycpc/mcstatus-checker">https://github.com/myworldzycpc/mcstatus-checker</a></p>
            <p>This is a tool for checking the status of Minecraft Java Edition servers.</p>
            """,
            "error_log_open": "Failed to open log file: {0}",
            "error_log_not_found": "Log file does not exist.",
            "error_run_dir_open": "Failed to open directory: {0}",
            "error_lang_dir_open": "Failed to open directory: {0}",
            "error_run_dir_not_found": "Run directory does not exist.",
            "error_lang_dir_not_found": "Language directory does not exist.",
            "server_already_exists": "Server {0} already exists. Add anyway?"
        }

    def load_external_language_packs(self):
        """加载外部语言包"""
        lang_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lang")

        # 检查语言目录是否存在
        if not os.path.exists(lang_dir):
            try:
                os.makedirs(lang_dir)
                logger.info(f"Created language directory: {lang_dir}")
            except Exception as e:
                logger.error(f"Failed to create language directory: {e}")
                return

        # 加载所有JSON语言文件
        lang_files = glob.glob(os.path.join(lang_dir, "*.json"))
        for lang_file in lang_files:
            try:
                lang_code = os.path.basename(lang_file).replace(".json", "")
                with open(lang_file, "r", encoding="utf-8") as f:
                    lang_data = json.load(f)
                    # 检查语言名称是否存在
                    if "language_name" in lang_data:
                        self.languages[lang_code] = lang_data["language_name"]
                        # 合并翻译数据，不包括语言名称
                        self.lang_data[lang_code] = {k: v for k, v in lang_data.items() if k != "language_name"}
                        logger.info(f"Loaded language pack: {lang_code} ({lang_data['language_name']})")
                    else:
                        logger.warning(f"Language pack {lang_code} is missing 'language_name' key")
            except Exception as e:
                logger.error(f"Failed to load language pack {lang_file}: {e}")

    def get_language_name(self, lang_code):
        """获取语言名称"""
        return self.languages.get(lang_code, lang_code)

    def get_available_languages(self):
        """获取可用语言列表"""
        return sorted(self.languages.items(), key=lambda x: x[1])

    def set_language(self, lang_code):
        """设置当前语言"""
        # 特殊处理：系统默认
        if lang_code == "system":
            system_lang = QLocale.system().name().lower()
            # 尝试查找匹配的语言
            for code in self.languages:
                if code in system_lang:
                    lang_code = code
                    break
            else:
                # 如果没有找到匹配的，使用默认语言
                lang_code = self.default_lang

        if lang_code in self.lang_data:
            self.current_lang = lang_code
            logger.info(f"Language set to: {lang_code} ({self.get_language_name(lang_code)})")
            return True
        else:
            logger.warning(f"Language {lang_code} not found, using default")
            self.current_lang = self.default_lang
            return False

    def translate(self, key, *args):
        """翻译文本"""
        if not self.current_lang:
            self.set_language(self.default_lang)

        # 尝试从当前语言获取翻译
        translation = self.lang_data[self.current_lang].get(key)

        # 如果没有找到，尝试从默认语言获取
        if not translation and self.current_lang != self.default_lang:
            translation = self.lang_data[self.default_lang].get(key)

        # 如果还是没有找到，返回键名
        if not translation:
            logger.warning(f"Translation key not found: {key}")
            translation = key

        # 如果有参数，进行格式化
        if args:
            try:
                translation = translation.format(*args)
            except Exception as e:
                logger.error(f"Failed to format translation: {translation}, args: {args}, error: {e}")

        return translation


class ServerStatusThread(QThread):
    """用于后台获取服务器状态的线程类 (Thread class for fetching server status in background)"""
    status_fetched = pyqtSignal(str, object, float)  # 信号：地址, 状态对象, 延迟 (Signal: address, status object, delay)

    def __init__(self, address):
        super().__init__()
        self.address = address

    def run(self):
        try:
            logger.info(f"开始查询服务器: {self.address}")
            server = JavaServer.lookup(self.address)
            latency = server.ping()  # 先获取延迟 (Get latency first)
            status = server.status()  # 再获取完整状态 (Get full status second)
            logger.info(f"服务器 {self.address} 查询成功, 延迟: {latency}ms")
            self.status_fetched.emit(self.address, status, latency)
        except Exception as e:
            logger.info(f"服务器 {self.address} 查询失败: {str(e)}")
            self.status_fetched.emit(self.address, str(e), -1)


class SettingsManager:
    """设置管理类 (Settings manager class)"""

    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = self.load_settings()

    def load_settings(self):
        """加载设置 (Load settings)"""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                settings = json.load(f)
                # 确保所有设置项都存在 (Ensure all settings exist)
                for key, default in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = default
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning(f"设置文件 {self.filename} 未找到或损坏，使用默认设置")
            return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """保存设置 (Save settings)"""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.info("设置已保存")
        except Exception as e:
            logger.error(f"保存设置失败: {str(e)}")

    def __getitem__(self, key):
        return self.settings[key]

    def __setitem__(self, key, value):
        self.settings[key] = value
        self.save_settings()


class ServerManager:
    """服务器管理类 (Server manager class)"""

    def __init__(self, filename="servers.json"):
        self.filename = filename
        self.servers = self.load_servers()
        self.addresses = set()  # 地址集合
        self.server_status = {}  # 地址 -> 状态数据 (Address -> status data)
        self.server_icons = {}   # 地址 -> 图标QPixmap (Address -> icon QPixmap)

    def load_servers(self):
        """从文件加载服务器列表 (Load server list from file)"""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                servers = json.load(f)
                logger.info(f"已加载 {len(servers)} 个服务器")
                return servers
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning(f"服务器文件 {self.filename} 未找到或损坏")
            return []

    def save_servers(self):
        """保存服务器列表到文件 (Save server list to file)"""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.servers, f, ensure_ascii=False, indent=2)
            logger.info("服务器列表已保存")
        except Exception as e:
            logger.error(f"保存服务器列表失败: {str(e)}")

    def add_server(self, name, address):
        """添加新服务器 (Add new server)"""
        # 检查服务器是否已存在 (Check if server already exists)
        if any(s["address"] == address for s in self.servers):
            if QMessageBox.question(window, i18n.translate("confirm_delete_server"),
                                    i18n.translate("server_already_exists", address),
                                    QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                logger.warning(f"服务器 {address} 已存在，未添加")
                return False

        self.servers.append({"name": name or address, "address": address})
        logger.info(f"已添加服务器: {name} ({address})")
        self.save_servers()
        return True

    def remove_server(self, index):
        """删除服务器 (Remove server)"""
        if 0 <= index < len(self.servers):
            server = self.servers.pop(index)
            logger.info(f"已删除服务器: {server['name']} ({server['address']})")
            self.save_servers()
            return True
        return False

    def update_server(self, index, name, address):
        """更新服务器信息 (Update server information)"""
        if 0 <= index < len(self.servers):
            self.servers[index] = {"name": name or address, "address": address}
            window.server_list.item(index).setData(Qt.UserRole, self.servers[index])

            logger.info(f"已更新服务器: {name} ({address})")
            self.save_servers()
            return True
        return False

    def get_server_addresses(self):
        """获取所有服务器地址 (Get all server addresses)"""
        return [s["address"] for s in self.servers]


class MinecraftStatusChecker(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化国际化管理器
        global i18n
        i18n = I18nManager()

        self.setGeometry(300, 300, 900, 600)

        # 初始化管理器 (Initialize managers)
        self.settings = SettingsManager()
        self.server_manager = ServerManager()

        self.threads = []  # 活动线程列表 (Active thread list)

        # 设置当前语言
        i18n.set_language(self.settings["language"])

        # 设置应用程序标题
        self.setWindowTitle(i18n.translate("app_title"))

        # 创建UI (Initialize UI)
        self.init_ui()

        # 如果启用自动检查，刷新所有服务器状态
        if self.settings["auto_check"]:
            self.refresh_all()

    # ------------------------- UI 初始化 -------------------------
    def init_ui(self):
        """初始化用户界面"""
        self.create_menu_bar()
        self.create_main_layout()
        self.position_floating_icon()

    def create_menu_bar(self):
        """创建菜单栏"""
        bar = self.menuBar()

        # 文件菜单
        file_menu = bar.addMenu(i18n.translate("menu_file"))
        self.add_menu_action(file_menu, i18n.translate("menu_file_log"), self.show_log)
        self.add_menu_action(file_menu, i18n.translate("menu_file_run_dir"), self.show_run_dir)
        self.add_menu_action(file_menu, i18n.translate("menu_file_lang_dir"), self.show_lang_dir)
        file_menu.addSeparator()
        self.add_menu_action(file_menu, i18n.translate("menu_file_exit"), self.close, "Ctrl+Q")

        # 选项菜单
        option_menu = bar.addMenu(i18n.translate("menu_options"))
        self.auto_check_action = self.add_menu_action(
            option_menu, i18n.translate("menu_options_auto_check"), self.update_auto_check,
            checkable=True, checked=self.settings["auto_check"]
        )

        # 图标子菜单
        icon_menu = option_menu.addMenu(i18n.translate("menu_options_icon"))
        self.create_icon_size_menu(icon_menu, i18n.translate("menu_options_icon_list"), "icon_list_size",
                                   ["none", "16x16", "32x32", "64x64"])
        self.create_icon_size_menu(icon_menu, i18n.translate("menu_options_icon_detail"), "icon_detail_size",
                                   ["none", "32x32", "64x64", "128x128"])

        # 列表显示行数菜单
        list_row_menu = option_menu.addMenu(i18n.translate("menu_options_list_row"))
        self.create_option_menu(
            list_row_menu, "list_row_size",
            [
                (i18n.translate("menu_options_list_row_single"), "single"),
                (i18n.translate("menu_options_list_row_single_no_motd"), "single_no_motd"),
                (i18n.translate("menu_options_list_row_multi"), "multi")
            ]
        )

        # 语言菜单
        language_menu = option_menu.addMenu(i18n.translate("menu_language"))
        group = QActionGroup(self)
        group.setExclusive(True)

        # 添加系统默认选项
        action = self.add_menu_action(
            language_menu, i18n.translate("menu_language_system"),
            lambda chk: self.change_language("system"),
            checkable=True,
            checked=(self.settings["language"] == "system"))
        group.addAction(action)

        # 添加所有可用语言
        for lang_code, lang_name in i18n.get_available_languages():
            if lang_code != "system":
                action = self.add_menu_action(
                    language_menu, lang_name,
                    lambda chk, lc=lang_code: self.change_language(lc),
                    checkable=True,
                    checked=(self.settings["language"] == lang_code))
                group.addAction(action)

        # 帮助菜单
        help_menu = bar.addMenu(i18n.translate("menu_help"))
        self.add_menu_action(help_menu, i18n.translate("menu_help_about"), self.show_about)

    def create_main_layout(self):
        """创建主布局"""
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # 使用分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # 左侧区域 - 服务器列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 服务器列表控件
        self.server_list = QListWidget()
        self.server_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.server_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.server_list.setMinimumWidth(300)
        self.server_list.itemDoubleClicked.connect(self.edit_server)
        self.server_list.itemSelectionChanged.connect(self.show_details)
        self.server_list.model().rowsMoved.connect(self.list_row_moved)
        self.server_list.model().rowsRemoved.connect(self.list_row_moved)
        self.update_icon_list_size()

        # 按钮区域
        self.button_layout = self.create_button_layout()

        left_layout.addWidget(self.server_list)
        left_layout.addLayout(self.button_layout)

        # 右侧区域 - 详细信息
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 详细信息标签
        self.detail_label = QLabel(i18n.translate("server_details_title"))
        self.detail_label.setFont(QFont("Arial", 12, QFont.Bold))

        # 详细信息文本框
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("background-color: #f0f0f0;")

        right_layout.addWidget(self.detail_label)
        right_layout.addWidget(self.detail_text)

        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 500])

        # 创建浮动图标标签
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(128, 128)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            background-color: #e0e0e0; 
            border: 1px solid #c0c0c0;
        """)
        self.icon_label.hide()

        # 加载服务器列表
        self.reload_server_list()
        if self.server_manager.servers:
            self.server_list.setCurrentRow(0)

    def create_button_layout(self):
        """创建按钮布局"""
        button_layout = QHBoxLayout()

        buttons = [
            (i18n.translate("button_add_server"), self.add_server),
            (i18n.translate("button_remove_server"), self.remove_server),
            (i18n.translate("button_refresh"), self.refresh),
            (i18n.translate("button_refresh_all"), self.refresh_all)
        ]

        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            button_layout.addWidget(button)

        return button_layout

    # ------------------------- 菜单辅助方法 -------------------------
    def add_menu_action(self, menu, text, callback, shortcut=None,
                        checkable=False, checked=False):
        """添加菜单项"""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
        action.triggered.connect(callback)
        menu.addAction(action)
        return action

    def create_icon_size_menu(self, parent_menu, name, setting_key, options):
        """创建图标大小菜单"""
        menu = parent_menu.addMenu(name)
        group = QActionGroup(self)
        group.setExclusive(True)

        for option in options:
            text = i18n.translate("menu_options_icon_none") if option == "none" else option
            action = self.add_menu_action(
                menu, text,
                lambda chk, opt=option: self.update_setting(setting_key, opt),
                checkable=True,
                checked=(self.settings[setting_key] == option))
            group.addAction(action)

    def create_option_menu(self, parent_menu, setting_key, options):
        """创建选项菜单"""
        group = QActionGroup(self)
        group.setExclusive(True)

        for text, value in options:
            action = self.add_menu_action(
                parent_menu, text,
                lambda chk, val=value: self.update_setting(setting_key, val),
                checkable=True,
                checked=(self.settings[setting_key] == value))
            group.addAction(action)

    # ------------------------- 服务器列表管理 -------------------------
    def reload_server_list(self):
        """重新加载服务器列表显示"""
        self.server_list.clear()
        for server in self.server_manager.servers:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, server)  # 存储完整数据
            self.update_server_item(item, server)
            self.server_list.addItem(item)
        self.show_details()

    def list_row_moved(self):
        if self.server_list.count() != len(self.server_manager.servers):
            self.reload_server_list()
        self.save_server_order()

    def save_server_order(self):
        """保存服务器顺序"""
        # 更新服务器顺序
        servers = []
        for i in range(self.server_list.count()):
            item = self.server_list.item(i)
            servers.append(item.data(Qt.UserRole))

        self.server_manager.servers = servers
        self.server_manager.save_servers()

    def update_server_item(self, item, server):
        """更新单个服务器项的显示"""
        address = server["address"]
        name = server.get("name", address)
        status_data = self.server_manager.server_status.get(address)

        # 根据状态设置文本和背景色
        if status_data is None:  # 未查询状态
            if self.settings["list_row_size"] == "single" or self.settings["list_row_size"] == "single_no_motd":
                status_text = i18n.translate("server_status_unknown")
            elif self.settings["list_row_size"] == "multi":
                status_text = i18n.translate("server_status_unknown") + "\n"
            else:
                logger.error(f"未知列表显示行数设置: {self.settings['list_row_size']}")
            color = COLOR_UNCHECKED
        elif isinstance(status_data, JavaStatusResponse):  # 在线状态
            online_text = f"{i18n.translate('server_details_players')}: {status_data.players.online}/{status_data.players.max}"
            latency_text = f"{i18n.translate('server_details_latency')}: {status_data.latency:.1f}"

            if self.settings["list_row_size"] == "single":
                motd = status_data.motd.to_plain().replace('\n', '↵ ')
                status_text = f"{online_text}, {latency_text} | {motd}"
            elif self.settings["list_row_size"] == "single_no_motd":
                status_text = f"{online_text}, {latency_text}"
            elif self.settings["list_row_size"] == "multi":
                motd = status_data.motd.to_plain().replace('\n', '\n  ')
                status_text = f"{online_text}, {latency_text}\n  {motd}"
            else:
                logger.error(f"未知列表显示行数设置: {self.settings['list_row_size']}")
                status_text = f"{online_text}, {latency_text}"

            color = COLOR_ONLINE
        else:  # 错误状态
            error_msg = str(status_data)
            if self.settings["list_row_size"] == "single" or self.settings["list_row_size"] == "single_no_motd":
                status_text = f'{i18n.translate("server_status_error")}: {error_msg}'
            elif self.settings["list_row_size"] == "multi":
                status_text = f'{i18n.translate("server_status_error")}:\n {error_msg}'
            else:
                logger.error(f"未知列表显示行数设置: {self.settings['list_row_size']}")
            color = COLOR_OFFLINE

        # 设置项目文本和背景
        if self.settings["list_row_size"] == "single" or self.settings["list_row_size"] == "single_no_motd":
            item.setText(f"{name} - {status_text}")
        else:
            item.setText(f"{name} - {status_text}")

        item.setBackground(color)

        # 设置服务器图标（如果存在）
        if (self.settings["icon_list_size"] != "none" and
                address in self.server_manager.server_icons):
            item.setIcon(QIcon(self.server_manager.server_icons[address]))
        else:
            item.setIcon(QIcon())  # 清除图标

    def update_server_list(self, address=None):
        """更新服务器列表显示"""
        if self.server_list.count() != len(self.server_manager.servers):
            self.reload_server_list()
            return

        for i in range(self.server_list.count()):
            server = self.server_manager.servers[i]
            if address is None or server["address"] == address:
                self.update_server_item(self.server_list.item(i), server)

        self.show_details()

    # ------------------------- 服务器操作 -------------------------
    def add_server(self):
        """添加新服务器"""
        address, ok = QInputDialog.getText(
            self, i18n.translate("dialog_add_server"),
            i18n.translate("dialog_add_server_address")
        )

        if not ok or not address:
            return

        name, ok = QInputDialog.getText(
            self, i18n.translate("dialog_add_server_name"),
            i18n.translate("dialog_add_server_name"),
            text=address
        )

        if not ok:
            return

        # 添加到服务器列表
        if self.server_manager.add_server(name, address):
            self.reload_server_list()
            if self.settings["auto_check"]:
                self.refresh_status(address)

    def edit_server(self, item):
        """编辑服务器信息"""
        index = self.server_list.row(item)
        server = self.server_manager.servers[index]

        # 创建编辑对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(i18n.translate("dialog_edit_server"))
        dialog_layout = QVBoxLayout(dialog)

        # 创建表单布局
        form_layout = QFormLayout()

        # 名称输入框
        name_edit = QLineEdit(server["name"])
        form_layout.addRow(i18n.translate("dialog_edit_server_name"), name_edit)

        # 地址输入框
        address_edit = QLineEdit(server["address"])
        form_layout.addRow(i18n.translate("dialog_edit_server_address"), address_edit)

        dialog_layout.addLayout(form_layout)

        def input_confirm():
            new_name = name_edit.text().strip()
            new_address = address_edit.text().strip()
            if new_name and new_address:
                dialog.accept()

        # 按钮布局
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(input_confirm)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)

        # 显示对话框并获取结果
        if dialog.exec_() == QDialog.Accepted:
            new_name = name_edit.text().strip()
            old_address = server["address"]
            new_address = address_edit.text().strip()

            if new_name and new_address:
                # 更新服务器信息
                if self.server_manager.update_server(index, new_name, new_address):
                    self.update_server_list()
                    if self.settings["auto_check"] and old_address != new_address:
                        self.refresh_status(new_address)

    def remove_server(self):
        """删除选中的服务器"""
        selected = self.server_list.currentRow()
        if selected < 0:
            return

        server = self.server_manager.servers[selected]

        reply = QMessageBox.question(
            self, i18n.translate("confirm_delete_server"),
            i18n.translate("confirm_delete_server_msg", server['name']),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.server_manager.remove_server(selected):
                self.reload_server_list()

    # ------------------------- 状态刷新 -------------------------
    def refresh_status(self, address):
        """刷新单个服务器的状态"""
        # 创建并启动线程
        thread = ServerStatusThread(address)
        self.threads.append(thread)
        thread.status_fetched.connect(self.handle_status_result)
        thread.start()

        # 更新UI显示正在查询
        for i in range(self.server_list.count()):
            item = self.server_list.item(i)
            server = item.data(Qt.UserRole)
            if server["address"] == address:
                if self.settings["list_row_size"] == "single" or self.settings["list_row_size"] == "single_no_motd":
                    item.setText(f"{server['name']} - {i18n.translate('server_status_checking')}")
                else:
                    item.setText(f"{server['name']} - {i18n.translate('server_status_checking')}\n")
                item.setBackground(COLOR_CHECKING)

    def refresh(self):
        """刷新选中的服务器状态"""
        selected_item = self.server_list.currentItem()
        if not selected_item:
            return

        server = selected_item.data(Qt.UserRole)
        self.refresh_status(server["address"])

    def refresh_all(self):
        """刷新所有服务器状态"""
        for server in self.server_manager.servers:
            self.server_manager.addresses.add(server["address"])
        for server in self.server_manager.addresses:
            self.refresh_status(server)

    def handle_status_result(self, address, status, latency):
        """处理状态查询结果"""
        # 存储结果
        self.server_manager.server_status[address] = status

        # 处理服务器图标
        if isinstance(status, JavaStatusResponse) and status.icon:
            try:
                # 移除Base64前缀
                icon_data = status.icon
                if icon_data.startswith("data:image/png;base64,"):
                    icon_data = icon_data[len("data:image/png;base64,"):]

                # 解码Base64数据
                decoded_icon = base64.b64decode(icon_data)

                # 创建QPixmap
                pixmap = QPixmap()
                pixmap.loadFromData(decoded_icon)
                self.server_manager.server_icons[address] = pixmap
            except Exception as e:
                logger.error(f"处理服务器图标时出错: {e}")
                self.server_manager.server_icons.pop(address, None)
        else:
            # 如果没有图标或出错，确保删除缓存
            self.server_manager.server_icons.pop(address, None)

        # 更新列表显示
        self.update_server_list(address)

        # 关闭线程
        for thread in self.threads[:]:
            if thread.address == address:
                thread.quit()
                thread.wait(100)
                self.threads.remove(thread)

    # ------------------------- 详细信息显示 -------------------------
    def show_details(self):
        """显示选中服务器的详细信息"""
        self.update_icon_label()

        selected_item = self.server_list.currentItem()
        if not selected_item:
            self.detail_text.clear()
            return

        server = selected_item.data(Qt.UserRole)
        address = server["address"]
        status = self.server_manager.server_status.get(address)

        # 构建详细信息文本
        details = f"<h2>{i18n.translate('server_details_name', server['name'])}</h2>"
        details += f"<b>{i18n.translate('server_details_address')}:</b> {address}<br><br>"

        if status is None:
            details += f"<i>{i18n.translate('server_details_not_checked')}</i>"
        elif isinstance(status, str):
            details += f"<b>{i18n.translate('server_status_error')}:</b><br>{status}"
        else:
            # 服务器在线信息
            details += f"<b>{i18n.translate('server_details_status')}:</b> {i18n.translate('server_status_online')}<br>"
            details += f"<b>{i18n.translate('server_details_latency')}:</b> {status.latency:.1f}ms<br>"
            details += f"<b>{i18n.translate('server_details_version')}:</b> {status.version.name} ({i18n.translate('server_details_protocol')}: {status.version.protocol})<br>"
            details += f"<b>{i18n.translate('server_details_players')}:</b> {status.players.online}/{status.players.max}<br>"

            # MOTD信息
            motd = status.motd.to_html()
            details += f"<b>{i18n.translate('server_details_motd')}:</b>" + motd.replace('\n', '<br>') + "<br>"

            # 玩家列表
            if status.players.sample:
                details += f"<b>{i18n.translate('server_details_players_list')}:</b><br>"
                for player in status.players.sample:
                    details += f"  - {player.name}<br>"
            else:
                details += f"<b>{i18n.translate('server_details_players_list')}:</b> {i18n.translate('server_details_players_none')}<br>"

            # 原始数据
            details += f"<br><b>{i18n.translate('server_details_raw_data')}:</b><br>"
            details += f"<pre>{json.dumps(status.raw, indent=2)}</pre>"

        self.detail_text.setHtml(details)

    # ------------------------- 图标处理 -------------------------
    def resizeEvent(self, event):
        """窗口大小改变时重新定位浮动图标"""
        super().resizeEvent(event)
        self.position_floating_icon()

    def position_floating_icon(self):
        """定位浮动图标到窗口右上角"""
        if not self.icon_label.isVisible():
            return

        # 计算右上角位置 (右上角偏移20像素)
        x_pos = self.width() - self.icon_label.width() - 50
        y_pos = 60  # 距离顶部20像素

        # 设置位置
        self.icon_label.move(x_pos, y_pos)

    def update_icon_label(self):
        """更新浮动图标"""
        if self.settings["icon_detail_size"] == "none":
            self.icon_label.hide()
            return

        selected_item = self.server_list.currentItem()
        if not selected_item:
            self.icon_label.hide()
            return

        server = selected_item.data(Qt.UserRole)
        address = server["address"]
        pixmap = self.server_manager.server_icons.get(address)

        if not pixmap:
            self.icon_label.hide()
            return

        # 根据设置缩放图标
        size_str = self.settings["icon_detail_size"]
        if size_str == "none":
            self.icon_label.hide()
            return
        elif size_str == "32x32":
            pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.icon_label.setFixedSize(32, 32)
        elif size_str == "64x64":
            pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.icon_label.setFixedSize(64, 64)
        elif size_str == "128x128":
            pixmap = pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.icon_label.setFixedSize(128, 128)
        else:
            logger.warning(f"未知图标大小: {size_str}")
            self.icon_label.hide()
            return

        self.icon_label.setPixmap(pixmap)
        self.icon_label.setStyleSheet("border: 1px solid #c0c0c0")
        self.icon_label.show()
        self.position_floating_icon()

    def update_icon_list_size(self):
        """更新服务器列表图标大小"""
        size_str = self.settings["icon_list_size"]
        if size_str == "none":
            self.server_list.setIconSize(QSize(0, 0))
        elif size_str == "16x16":
            self.server_list.setIconSize(QSize(16, 16))
        elif size_str == "32x32":
            self.server_list.setIconSize(QSize(32, 32))
        elif size_str == "64x64":
            self.server_list.setIconSize(QSize(64, 64))
        else:
            logger.warning(f"未知图标大小: {size_str}")

    # ------------------------- 设置管理 -------------------------
    def update_setting(self, key, value):
        """更新设置项"""
        self.settings[key] = value

        # 根据设置项更新UI
        if key == "icon_list_size":
            self.update_icon_list_size()
            self.update_server_list()
        elif key == "icon_detail_size":
            self.update_icon_label()
        elif key == "list_row_size":
            self.update_server_list()

    def update_auto_check(self):
        """更新自动检查设置"""
        self.settings["auto_check"] = self.auto_check_action.isChecked()

    def change_language(self, lang_code):
        """更改应用程序语言"""
        if i18n.set_language(lang_code):
            self.settings["language"] = lang_code
            self.retranslate_ui()

    def retranslate_ui(self):
        """重新翻译UI"""
        # 更新窗口标题
        self.setWindowTitle(i18n.translate("app_title"))

        # 更新菜单
        self.menuBar().clear()
        self.create_menu_bar()

        # 更新按钮文本
        button_layout = self.button_layout
        button_texts = [
            i18n.translate("button_add_server"),
            i18n.translate("button_remove_server"),
            i18n.translate("button_refresh"),
            i18n.translate("button_refresh_all")
        ]

        for i in range(button_layout.count()):
            button = button_layout.itemAt(i).widget()
            button.setText(button_texts[i])

        # 更新详情标签
        self.detail_label.setText(i18n.translate("server_details_title"))

        # 重新加载服务器列表以更新状态文本
        self.update_server_list()

    # ------------------------- 工具方法 -------------------------
    def show_log(self):
        """显示日志"""
        log_file = "mcstatus.log"

        if os.path.exists(log_file):
            try:
                os.startfile(log_file)
            except Exception as e:
                QMessageBox.warning(self, i18n.translate("menu_file_log"),
                                    i18n.translate("error_log_open", str(e)))
        else:
            QMessageBox.warning(self, i18n.translate("menu_file_log"),
                                i18n.translate("error_log_not_found"))

    def show_run_dir(self):
        """显示运行目录"""
        run_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(run_dir):
            try:
                os.startfile(run_dir)
            except Exception as e:
                QMessageBox.warning(self, i18n.translate("menu_file_run_dir"),
                                    i18n.translate("error_run_dir_open", str(e)))
        else:
            QMessageBox.warning(self, i18n.translate("menu_file_run_dir"),
                                i18n.translate("error_run_dir_not_found"))

    def show_lang_dir(self):
        """显示语言目录"""
        lang_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lang")
        if os.path.exists(lang_dir):
            try:
                os.startfile(lang_dir)
            except Exception as e:
                QMessageBox.warning(self, i18n.translate("menu_file_lang_dir"),
                                    i18n.translate("error_lang_dir_open", str(e)))
        else:
            QMessageBox.warning(self, i18n.translate("menu_file_lang_dir"),
                                i18n.translate("error_lang_dir_not_found"))

    def show_about(self):
        """显示关于信息"""
        QMessageBox.about(self, i18n.translate("about_title"), i18n.translate("about_text"))


# ------------------------- 主程序入口 -------------------------
if __name__ == "__main__":
    logger.info("启动程序")
    app = QApplication(sys.argv)

    # 设置全局字体
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)

    # 设置工具提示样式
    app.setStyleSheet(
        "QToolTip { background-color: #ffffe0; color: black; border: 1px solid black; }")

    window = MinecraftStatusChecker()
    window.show()

    exit_code = app.exec_()
    logger.info(f"退出程序，退出码: {exit_code}")
    sys.exit(exit_code)
