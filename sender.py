import base64
import json
import os
import secrets
import socket
import struct
import time
from Crypto.Hash import SHA1 as HASH
from tkinter import messagebox
import config_info
from cryptoToolBox import RSAOperation as rsaOp
from cryptoToolBox import DESOperation as desOp


class Sender:
    def __init__(self, ip, port, absolute_path, local_ip_flag, msg_queue, time_out=45):
        """
        初始化参数

        :param ip: 发送的IP地址
        :param port: 发送的端口
        :param absolute_path: 发送的文件绝对路径
        :param time_out: 设置超时退出的等待时间
        """
        self.ip = ip
        self.port = port
        self.absolute_path = absolute_path
        self.local_ip_flag = local_ip_flag
        self.msg_queue = msg_queue
        self.time_out = time_out
        self.rsaOp = rsaOp()
        self.desOp = desOp()
        self.BUFFER_size = 1024 * 1024  # 设置读取的缓冲区大小
        # self.BUFFER_size = 4096  # 设置读取的缓冲区大小
        self.process_count = 5000  # 设置des加密每隔 process_count 次，显示一次传输进度

    def run(self):
        """
        自动判断选择，启动服务端或客户端
        """
        if self.local_ip_flag:
            try:
                self.send_server()
            except OSError:
                try:
                    self.send_client()
                except:
                    self.msg_queue.put(config_info.Connection_Error)
        else:
            self.send_client()

    def send_server(self):
        """
        发送方服务端的操作流程
        """
        # 1、开始连接
        socket_server = socket.socket()
        socket_server.bind((self.ip, int(self.port)))
        socket_server.listen()
        socket_server.settimeout(self.time_out)
        self.msg_queue.put(config_info.WaitForReceiverConnection_Info)
        try:
            conn, address = socket_server.accept()
        except socket.timeout:
            self.msg_queue.put(config_info.SendTimeout_Info % f'{self.time_out}')
            socket_server.close()
            return
        try:
            # 主要流程
            self.main_send_steps(conn=conn, address=address[0] + ': ' + str(address[1]))
        except socket.timeout:
            self.msg_queue.put(config_info.SendTimeout_Info % f'{15}')
            return
        except OSError:
            self.msg_queue.put(config_info.Disconnection_Error)
            return
        except ConnectionResetError:
            self.msg_queue.put(config_info.Disconnection_Error)
        finally:
            # 8、关闭连接对象、套接字对象
            conn.close()
            socket_server.close()

    def send_client(self):
        """
        发送方客户端的操作流程
        """
        # 1、开始连接
        socket_client = socket.socket()
        try:
            socket_client.connect((self.ip, int(self.port)))
        except TimeoutError:
            self.msg_queue.put(config_info.Timeout_Error)
            socket_client.close()
            return
        except OSError:
            self.msg_queue.put(config_info.IP_Address_Error)
            socket_client.close()
            return

        try:
            # 主要流程
            self.main_send_steps(conn=socket_client, address=self.ip + ': ' + self.port)
        except socket.timeout:
            self.msg_queue.put(config_info.SendTimeout_Info % f'{15}')
            return
        except OSError:
            self.msg_queue.put(config_info.Disconnection_Error)
            return
        except ConnectionResetError:
            self.msg_queue.put(config_info.Disconnection_Error)
        finally:
            # 8、关闭套接字对象
            socket_client.close()

    def send_dict(self, socket_conn, dic):
        """
        发送构造的自定义数据包。

        :param socket_conn: 实例化的套接字连接对象
        :param dic: 构造的数据信息字典
        """
        # 将字典转换为json
        send_dic = json.dumps(dic).encode('utf-8')
        # 发送字典长度
        dic_len = struct.pack('i', len(send_dic))
        socket_conn.send(dic_len)
        time.sleep(0.1)
        # 发送字典
        socket_conn.send(send_dic)

    def main_send_steps(self, conn, address):
        """
        主要的发送操作流程

        :param conn: 连接成功的套接字对象
        :param address: 接收方的“IP:端口号”
        """
        # 2、确认对方（接收方）的IP地址——身份信息
        save_ask_bool = messagebox.askyesno(
            title='提示', message=f"是否向{address}发送文件：{self.absolute_path}")
        if not save_ask_bool:
            self.msg_queue.put(config_info.QuitSend_Info)
            self.send_dict(conn, {'send_refuse_flag': True})
            return
        # 使用密钥进行身份核实
        time_bytes = b''
        for _ in int(time.time()).__str__():
            time_bytes += bytes([int(_)]) + secrets.token_bytes(1)
        token_bytes = secrets.token_bytes(90) + time_bytes + secrets.token_bytes(90)
        ask_flag = self.rsaOp.encrypt_with_rsa(token_bytes, config_info.PUBLIC_KEY)
        dic_0 = {'ask_flag': base64.b64encode(ask_flag).decode('utf-8')}
        self.send_dict(conn, dic_0)
        response = conn.recv(1024)
        if response != token_bytes:
            self.msg_queue.put(config_info.ReceiverAuthentication_Error)
            return
        # 3、询问对方（接收方），是否接收该文件
        file_size = os.path.getsize(self.absolute_path)
        dic_1 = {'filename': os.path.basename(self.absolute_path),
                 'file_size': file_size
                 }

        self.send_dict(conn, dic_1)
        response = base64.b64decode(conn.recv(610))

        if response[:6] != b'accept':
            # 如果拒绝，则退出
            self.msg_queue.put(config_info.ReceiverReject_Info)
            return
        conn.settimeout(15)
        # 如果同意，开始准备工作
        # 4、获取对方（接收方）的RSA公钥
        receive_pub_key = response[6:]
        # 检查接收的对方（接收方）RSA公钥是否完整、未被篡改
        receive_pub_key_sign = base64.b64decode(conn.recv(1700))
        receive_pub_key_hash = HASH.new()
        receive_pub_key_hash.update(receive_pub_key)
        if not receive_pub_key.endswith(b'END PUBLIC KEY-----')\
                and self.rsaOp.verify_with_public_key(receive_pub_key_sign, receive_pub_key_hash, config_info.PUBLIC_KEY):
            self.msg_queue.put(config_info.DataTransmission_Error)
            return

        # 5、创建：DES密钥，本方的RSA公钥、私钥，文件的数字签名
        des_key = self.desOp.create_des_key()
        pri_key, pub_key = self.rsaOp.create_rsa_keypair()
        pub_key_sign = self.rsaOp.sign_with_private_key(
            sign_bytes=pub_key, private_key=config_info.PRIVATE_KEY, mode='bytes')
        file_sign = self.rsaOp.sign_with_private_key(
            filepath=self.absolute_path, private_key=pri_key, mode='file')
        key_bytes = self.rsaOp.encrypt_with_rsa(des_key, receive_pub_key)

        # 6、将加密后的密钥和数字签名，发送给接收方
        # 预测传输字节长度
        pad_num = 8 - file_size % 8
        if file_size > 0 and pad_num == 0:
            pad_num = 8
        file_des_size = (file_size // (self.BUFFER_size - 8)) * self.BUFFER_size \
                        + file_size % (self.BUFFER_size - 8) + pad_num

        dic_2 = {'file_sign': base64.b64encode(file_sign).decode('utf-8'),
                 'pub_key': base64.b64encode(pub_key).decode('utf-8'),
                 'pub_key_sign': base64.b64encode(pub_key_sign).decode('utf-8'),
                 'des_key': base64.b64encode(key_bytes).decode('utf-8'),
                 'file_des_size': file_des_size
                 }
        self.send_dict(conn, dic_2)
        time.sleep(0.1)

        # 7、将DES加密的文件字节流，发送给接收方
        with open(self.absolute_path, 'rb') as f:  # 打开文件
            read_size = 0
            count = 0
            start_time = time.time()
            self.msg_queue.put(config_info.StartToSend_Info)

            while True:
                content = f.read(self.BUFFER_size - 8)  # 每次读取指定大小的字节

                read_size += len(content)
                count += 1
                if content:  # 判断内容不为空
                    # 每次读取指定大小的字节
                    ciphertext = self.desOp.encrypt_with_des(content, des_key)
                    conn.send(ciphertext)
                else:
                    break
                if count % self.process_count == 0:
                    self.msg_queue.put(f"{dic_1['filename']}\n"
                                       f"发送进度：{read_size / file_size * 100}%")
        # 显示传输用时
        send_time = time.time() - start_time
        self.msg_queue.put("发送完毕：本次用时 {:.4f} 秒。".format(send_time))
