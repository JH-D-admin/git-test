import socket
import threading
import time
from tkinter.constants import NORMAL, DISABLED, END
from tkinter import messagebox
from queue import Queue
import sender
import receiver
import config_info


class FileTransfer:
    def __init__(self, GText_Log):
        """
        初始化方法

        :param GText_Log: 主界面的运行日志控件对象
        """
        self.msg_queue = Queue()
        self.check_msg_queue_thread(GText_Log)

    def check_msg_queue_thread(self, GText_Log):
        """
        开启：消息队列 msg_queue 监听线程，显示欢迎信息
        :param GText_Log: 主界面的运行日志控件对象
        :return:
        """
        self.set_Daemon_thread(self.check_msg_queue, args=(GText_Log,))
        """显示欢迎信息"""
        # 获取本机内网IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except OSError:
            ip = "127.0.0.1" + "（当前本机未接入网络，处于单机模式）"
        finally:
            s.close()
        computer_ip_info = '本机的内网IP地址：%s' % ip
        info = config_info.Welcome_Info + computer_ip_info
        self.msg_queue.put(info)

    def check_msg_queue(self, GText_Log):
        """
        一直运行检测 消息队列 msg_queue 内容，并立即在运行日志中，打印其中信息

        :param GText_Log: 主界面的运行日志控件对象
        """
        while True:
            time.sleep(0.005)

            while not self.msg_queue.empty():
                GText_Log.config(state=NORMAL)
                # 获取东八区时间
                from datetime import datetime, timedelta, timezone
                time_8 = timezone(timedelta(hours=8))
                now = datetime.now(time_8)
                time_info = now.strftime("%Y-%m-%d %H:%M:%S")
                # time_info = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                GText_Log.insert(END, f"{time_info}\n" + self.msg_queue.get() + "\n\n")
                GText_Log.config(state=DISABLED)
                GText_Log.see(END)

    def send(self, ip, port, absolute_path):
        """
        发送功能

        :param ip:  发送文件的IP
        :param port: 发送文件的端口
        :param absolute_path: 发送文件的绝对路径
        """
        if len(threading.enumerate()) > 6:
            messagebox.showwarning(config_info.WarningTitle, config_info.TooManyThreads_Warning)
        send_thread = sender.Sender(ip, port, absolute_path, check_local_ip(ip), self.msg_queue)
        self.set_Daemon_thread(send_thread.run)

    def receive(self, ip, port):
        """
        接收功能

        :param ip: 接收文件的IP
        :param port: 接收文件的端口
        """
        if len(threading.enumerate()) > 6:
            messagebox.showwarning(config_info.WarningTitle, config_info.TooManyThreads_Warning)
        receive_thread = receiver.Receiver(ip, port, check_local_ip(ip), self.msg_queue)
        self.set_Daemon_thread(receive_thread.run)

    @staticmethod
    def set_Daemon_thread(t, args=()):
        thread = threading.Thread(target=t, args=args)
        thread.setDaemon(True)
        thread.start()


def check_local_ip(ip):
    """
    判断输入的IP，是否属于本机内网IP地址

    :param ip: IP地址
    :return: 判断结果（bool）
    """
    addrs = socket.getaddrinfo(socket.gethostname(), None)
    net_ip_list = [addr[4][0] for addr in addrs if addr[4][0].startswith("192")]
    return ip in ["0.0.0.0", "127.0.0.1", ""] + net_ip_list
