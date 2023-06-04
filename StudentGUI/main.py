import datetime
import sys

import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QDialogButtonBox, QInputDialog, QWidget, QMessageBox
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt

class AccountDialog(QDialog):
    def __init__(self, parent, username='', password=''):
        super().__init__(parent)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()

        self.username_input.setText(username)
        self.password_input.setText(password)

        form_layout = QFormLayout()
        form_layout.addRow('用户名:', self.username_input)
        form_layout.addRow('密码:', self.password_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)


class AccountManagementWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('账户管理')

        self.resize(800, 600)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['用户名', '密码'])

        self.add_button = QPushButton('添加账户')
        self.add_button.clicked.connect(self.add_account)

        self.delete_button = QPushButton('删除账户')
        self.delete_button.clicked.connect(self.delete_account)

        self.edit_button = QPushButton('修改账户')
        self.edit_button.clicked.connect(self.edit_account)

        self.search_button = QPushButton('查找账户')
        self.search_button.clicked.connect(self.search_account)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table_widget)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.edit_button)
        self.layout.addWidget(self.search_button)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)
        self.load_accounts()

    def load_accounts(self):
        with open("user_info.txt", "r") as file:
            for line in file:
                if ":" in line:
                    username, password = line.strip().split(":")
                    exists = False
                    rows = self.table_widget.rowCount()
                    for row in range(rows):
                        username_item = self.table_widget.item(row, 0)
                        if username_item.text() == username:
                            exists = True
                            break
                    if not exists:
                        row_count = self.table_widget.rowCount()
                        self.table_widget.insertRow(row_count)
                        username_item = QTableWidgetItem(username)
                        password_item = QTableWidgetItem(password)
                        if username == "admin":
                            username_item.setForeground(Qt.red)  # 设置管理员账户文字颜色为红色
                            username_item.setFont(QFont("Arial", 10, QFont.Bold))  # 设置管理员账户字体加粗
                            password_item.setFont(QFont("Arial", 10, QFont.Bold))  # 设置管理员账户密码字体加粗
                        self.table_widget.setItem(row_count, 0, username_item)
                        self.table_widget.setItem(row_count, 1, password_item)

    def save_accounts(self):
        with open("user_info.txt", "w") as file:
            rows = self.table_widget.rowCount()
            for row in range(rows):
                username_item = self.table_widget.item(row, 0)
                password_item = self.table_widget.item(row, 1)
                username = username_item.text()
                password = password_item.text()
                file.write(f"{username}:{password}\n")

    def add_account(self):
        dialog = AccountDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            username = dialog.username_input.text()
            password = dialog.password_input.text()

            # 先加载已有账户信息
            self.load_accounts()

            # 检查是否存在相同的账户名
            exists = False
            rows = self.table_widget.rowCount()
            for row in range(rows):
                username_item = self.table_widget.item(row, 0)
                if username_item.text() == username:
                    exists = True
                    break

            if not exists:
                # 将新账户添加到列表中
                row_count = self.table_widget.rowCount()
                self.table_widget.insertRow(row_count)
                self.table_widget.setItem(row_count, 0, QTableWidgetItem(username))
                self.table_widget.setItem(row_count, 1, QTableWidgetItem(password))

                # 保存所有账户信息
                self.save_accounts()
            else:
                QMessageBox.warning(self, '警告', '账户名已存在，请输入不同的账户名。')

    def delete_account(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            username_item = self.table_widget.item(selected_row, 0)
            if username_item.text() != "admin":  # 确保不能删除管理员账户
                self.table_widget.removeRow(selected_row)
                self.save_accounts()

    def edit_account(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            username_item = self.table_widget.item(selected_row, 0)
            if username_item.text() != "admin":  # 确保不能编辑管理员账户
                password_item = self.table_widget.item(selected_row, 1)

                dialog = AccountDialog(self, username_item.text(), password_item.text())
                result = dialog.exec_()
                if result == QDialog.Accepted:
                    new_username = dialog.username_input.text()
                    new_password = dialog.password_input.text()

                    username_item.setText(new_username)
                    password_item.setText(new_password)

                    self.save_accounts()

    def search_account(self):
        search_text, ok = QInputDialog.getText(self, '查找账户', '请输入要查找的用户名:')
        if ok and search_text:
            rows = self.table_widget.rowCount()
            for row in range(rows):
                username_item = self.table_widget.item(row, 0)
                if username_item.text() == search_text:
                    self.table_widget.setCurrentCell(row, 0)
                    break

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        # 创建管理员账户
        self.create_admin_account()

    def init_ui(self):
        self.setWindowTitle('用户登录')

        self.resize(800, 450)

        self.username_label = QLabel('用户名')
        self.username_label.setFixedWidth(50)
        self.username_input = QLineEdit()
        self.username_input.setMaximumWidth(200)

        self.password_label = QLabel('密码')
        self.password_label.setFixedWidth(50)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMaximumWidth(200)

        self.login_button = QPushButton('登录')
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton('注册')
        self.register_button.clicked.connect(self.register)

        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.close)

        self.message_label = QLabel('消息：')
        self.message_label.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor('#ffffcc'))
        self.message_label.setPalette(palette)
        self.message_label.setAlignment(Qt.AlignTop)

        username_layout = QHBoxLayout()
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_input)

        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.cancel_button)

        login_layout = QVBoxLayout()
        login_layout.addLayout(username_layout)
        login_layout.addLayout(password_layout)
        login_layout.addLayout(button_layout)

        message_layout = QVBoxLayout()
        message_layout.addWidget(self.message_label)

        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(login_layout)
        vbox_layout.addLayout(message_layout)
        vbox_layout.setStretch(0, 1)
        vbox_layout.setStretch(1, 3)

        self.setLayout(vbox_layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin123":
            self.open_account_management()
            self.message_label.setText('消息：登录成功!\n用户类型：管理员账号\n登录时间：' + str(
                datetime.datetime.now()) + '\n登陆地点：' + self.get_login_location() + '\n创建时间：N/A')
            return

        with open("user_info.txt", "r") as file:
            for line in file:
                file_username, file_password = line.strip().split(":")
                if file_username == username:
                    if file_password == password:
                        self.message_label.setText('消息：登录成功!\n用户类型：普通账号\n登录时间：' + str(
                            datetime.datetime.now()) + '\n登陆地点：' + self.get_login_location() + '\n创建时间：N/A')
                    else:
                        self.message_label.setText('消息：密码错误!')
                    break
            else:
                self.message_label.setText('消息：账户不存在!')

    def get_login_location(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            location = data.get("loc")
            return location
        except:
            return "无法获取登录地点"

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin":
            self.message_label.setText('消息：不能使用管理员账户名进行注册!')
            return

        with open("user_info.txt", "r") as file:
            for line in file:
                if ":" not in line:
                    continue
                file_username, _ = line.strip().split(":")
                if file_username == username:
                    self.message_label.setText('消息：该用户名已被注册!')
                    break
            else:
                with open("user_info.txt", "a") as file:
                    file.write(f"{username}:{password}\n")
                self.message_label.setText('消息：注册成功! 用户信息已保存.')

    def create_admin_account(self):
        admin_username = "admin"
        admin_password = "admin123"

        with open("user_info.txt", "r") as file:
            for line in file:
                file_username, _ = line.strip().split(":")
                if file_username == admin_username:
                    break
            else:
                with open("user_info.txt", "a") as file:
                    file.write(f"{admin_username}:{admin_password}\n")

    def open_account_management(self):
        self.account_management_window = AccountManagementWindow()
        self.account_management_window.show()

app = QApplication(sys.argv)
login_window = LoginWindow()
login_window.show()

sys.exit(app.exec_())
