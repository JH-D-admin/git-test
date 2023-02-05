import os
import threading
from tkinter import filedialog, LabelFrame, Label, Entry, StringVar, Button, DISABLED, Tk
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
import transmissionInterface as fTP
import ipaddress
import config_info


class App:
    def __init__(self, root):
        """
        初始化窗口界面
        :param root: 根窗口 Tk对象
        """
        # setting title
        root.title("安全文件传输工具")
        # setting window size
        width = 720
        height = 460
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        # 设置多个容器控件
        group1 = LabelFrame(root, padx=5, pady=5)
        group2 = LabelFrame(root, padx=5, pady=5)
        group3 = LabelFrame(root, padx=5, pady=5, text="运行日志")
        group4 = LabelFrame(root, padx=5, pady=5)
        # 定义字体
        ft = Font(family='微软雅黑', size=10)
        ft_input = Font(family='微软雅黑', size=12)
        # 包装限制输入内容的函数
        limit_ip_cmd = group1.register(self.limit_ip_input)
        limit_port_cmd = group1.register(self.limit_port_input)
        # IP 标签
        GLabel_IP = Label(group1, text="IP：", padx=15, font=ft)
        # 端口 标签
        GLabel_Port = Label(group1, text="端口：", padx=15, font=ft)
        # 文件路径 标签
        GLabel_File = Label(group2, text="文件路径：", font=ft)
        # IP 文本框
        self.GLineEdit_IP = Entry(group1, width=15, font=ft_input, validate="key")
        self.GLineEdit_IP['validatecommand'] = (limit_ip_cmd, '%P')
        self.GLineEdit_IP['textvariable'] = StringVar(value='127.0.0.1')
        # 端口 文本框
        self.GLineEdit_PORT = Entry(group1, width=10, font=ft_input, validate="key")
        self.GLineEdit_PORT['validatecommand'] = (limit_port_cmd, '%P')
        self.GLineEdit_PORT['textvariable'] = StringVar(value='1234')
        # 传输文件路径 文本框
        self.entryVar = StringVar()
        self.GLineEdit_File = Entry(group2, width=45, textvariable=self.entryVar, font=ft_input)
        # 运行日志 文本框
        self.GText_Log = ScrolledText(group3, width=65, height=15, state=DISABLED)
        self.GText_Log['font'] = ft
        # 选择 按钮
        self.GButton_chooser = Button(group2, text="选择", width=6, font=ft)
        self.GButton_chooser['command'] = self.GButton_chooser_command
        # 发送 按钮
        self.GButton_send = Button(group4, text="发送", height=4, font=ft)
        self.GButton_send['command'] = self.GButton_send_command
        # 接收 按钮
        self.GButton_receive = Button(group4, text="接收", height=4, font=ft)
        self.GButton_receive['command'] = self.GButton_receive_command
        # group1容器部分 控件排列
        GLabel_IP.grid(row=0, column=0)
        self.GLineEdit_IP.grid(row=0, column=1)
        GLabel_Port.grid(row=0, column=2)
        self.GLineEdit_PORT.grid(row=0, column=4)
        group1.grid(row=0, column=0, sticky="we", padx=10, pady=10)
        # group2容器部分 控件排列
        GLabel_File.grid(row=0, column=0, columnspan=1)
        self.GLineEdit_File.grid(row=0, column=1, columnspan=3)
        self.GButton_chooser.grid(row=0, column=5, columnspan=1, padx=10)
        group2.grid(row=1, column=0, sticky="we", padx=10)
        # group3容器部分 控件排列
        self.GText_Log.grid(row=0, column=1, sticky="we")
        group3.grid(row=2, column=0, sticky="we", padx=10)
        # group4容器 控件排列
        self.GButton_send.grid(row=0, column=5, sticky="we", pady=5)
        self.GButton_receive.grid(row=1, column=5, sticky="we", pady=5)
        group4.grid(row=2, column=1, rowspan=3, sticky="we")
        # 创建 ftp类 实例，初始化
        self.ftp = fTP.FileTransfer(self.GText_Log)
        root.mainloop()

    @staticmethod
    def limit_ip_input(content: str) -> bool:
        """
        限制 IP地址文本框 的输入内容

        :param content: 文本框内容
        :return: 布尔值
        """
        if len(content) > 15 or content.count('.') > 3:
            return False
        for ch in content:
            if not (ch.isdigit() or ch == "." or ch == ""):
                return False
        return True

    @staticmethod
    def limit_port_input(content: str) -> bool:
        """
        限制 端口文本框 的输入内容

        :param content: 文本框内容
        :return: 布尔值
        """
        if content.isdigit() or content == "":
            if len(content) < 6:
                return True
        return False

    def check_ip_port(self):
        """
        检查：IP地址、端口的格式是否合法

        :return: 符合格式，则返回 IP地址、端口；否则，返回错误原因
        """
        ip = self.GLineEdit_IP.get()
        port = self.GLineEdit_PORT.get()
        # 检查IPv4地址格式
        if len(ip) > 6:  # 允许IP为空：表示本机接受其他任何IP的连接
            try:
                if not ipaddress.ip_address(ip).is_private:
                    return config_info.IPNotPrivate_Warning, ""
            except ValueError:
                return config_info.IPFormal_Warning, ""
        else:
            return config_info.IPFormal_Warning, ""
        # 检查端口格式
        if self.GLineEdit_PORT.get().isdigit():
            if not 1024 <= int(port) <= 65535:
                return "", config_info.Port_Warning
        else:
            return "", config_info.Port_Warning
        return ip, port

    def GButton_chooser_command(self):
        """选择 按钮事件"""
        filename = filedialog.askopenfilename()
        if filename:
            self.entryVar.set(filename)
            self.ftp.msg_queue.put(f"已选择文件：{filename}")

    def GButton_send_command(self):
        """发送 按钮事件：创建发送文件线程"""
        # 检查IP、端口格式
        ip, port = self.check_ip_port()
        info = ip + port
        if port.isdigit():
            if os.path.isfile(self.entryVar.get()):
                thread = threading.Thread(target=self.ftp.send(ip, port, self.entryVar.get()))
                thread.daemon = True
                thread.start()
                return
            else:
                info = config_info.FilePath_Warning
        self.ftp.msg_queue.put(info)

    def GButton_receive_command(self):
        """接收 按钮事件：创建接收文件线程"""
        # 检查IP、端口格式
        ip, port = self.check_ip_port()
        info = ip + port
        if port.isdigit():
            thread = threading.Thread(target=self.ftp.receive(ip, port))
            thread.daemon = True
            thread.start()
            return
        self.ftp.msg_queue.put(info)


def main():
    tk = Tk()
    App(tk)
    tk.mainloop()


if __name__ == "__main__":
    main()
