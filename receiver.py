import base64
import json
import os
import socket
import struct
import time
from tkinter import filedialog, messagebox
import config_info
from Crypto.Hash import SHA1 as HASH
from cryptoToolBox import RSAOperation as rsaOp
from cryptoToolBox import DESOperation as desOp


class Receiver:
    def __init__(self, ip, port, local_ip_flag, msg_queue, time_out=45):
        """
        初始化参数

        :param ip: 接收文件的IP
        :param port: 接收文件的端口
        :param msg_queue: 消息队列
        :param time_out: 空连接超时的退出时间
        """
        self.ip = ip
        self.port = port
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
                self.receive_server()
            except OSError:
                # try:
                self.receive_client()
                # except:
                #     self.msg_queue.put(config_info.Connection_Error)
        else:
            self.receive_client()

    def receive_client(self):
        """
        接收方客户端的接收操作流程
        """
        # 1、向对方（发送方）发送连接请求
        socket_client = socket.socket()
        try:
            socket_client.connect((self.ip, int(self.port)))
        except TimeoutError:
            self.msg_queue.put(config_info.Timeout_Error)
            socket_client.close()
            return False
        except ConnectionRefusedError:
            self.msg_queue.put(config_info.PortClosed_Error)
            socket_client.close()
            return False
        try:
            socket_client.settimeout(self.time_out)
            self.main_receive_steps(conn=socket_client, address=self.ip + ': ' + self.port)
        except socket.timeout:
            self.msg_queue.put(config_info.SendTimeout_Info % f'{15}')
            return
        except ConnectionResetError:
            self.msg_queue.put(config_info.Disconnection_Error)
            return
        finally:
            # 7、关闭套接字对象
            socket_client.close()

    def receive_server(self):
        """
        接收方服务端的接收操作流程
        """
        # 1、向对方（发送方）发送连接请求
        socket_server = socket.socket()
        socket_server.bind((self.ip, int(self.port)))
        socket_server.listen()
        socket_server.settimeout(self.time_out)
        self.msg_queue.put(config_info.WaitForSenderConnection_Info)

        try:
            conn, address = socket_server.accept()
        except socket.timeout:
            self.msg_queue.put(config_info.ReceiveTimeout_Info % f'{self.time_out}')
            socket_server.close()
            return
        try:
            # 主要流程
            self.main_receive_steps(conn=conn, address=address[0] + ': ' + str(address[1]))
        except socket.timeout:
            self.msg_queue.put(config_info.ReceiveTimeout_Info % f'{15}')
            return
        except ConnectionResetError:
            self.msg_queue.put(config_info.Disconnection_Error)
            return
        finally:
            # 7、关闭套接字对象
            conn.close()
            socket_server.close()

    def verify_signature(self, dic, checksum_hash):
        """
        验签操作

        :param dic: 含有数字签名、公钥的字典数据
        :param checksum_hash: 对文件内容完成数字摘要的Hash对象
        :return: 验证结果的布尔值
        """
        # 对公钥验签
        pub_key_sign = base64.b64decode(dic['pub_key_sign'].encode('utf-8'))

        pub_key_hash = HASH.new()
        pub_key_hash.update(base64.b64decode(dic['pub_key'].encode('utf-8')))
        if not self.rsaOp.verify_with_public_key(pub_key_sign, pub_key_hash, config_info.PUBLIC_KEY):
            self.msg_queue.put(config_info.FileVerification_Error)
            return False
        # 验签
        if self.rsaOp.verify_with_public_key(
                base64.b64decode(dic['file_sign'].encode('utf-8')),
                checksum_hash,
                base64.b64decode(dic['pub_key'].encode('utf-8'))):
            self.msg_queue.put(config_info.FileVerification_Info)
            return True
        else:
            self.msg_queue.put(config_info.FileVerification_Error)
            return False

    def receive_dict(self, sk):
        """
        接收构造的自定义数据包

        :param sk: 实例化的套接字对象
        :return: 字典类型源数据
        """
        struct_dic = sk.recv(4)  # 接收4字节：struct的int为4字节
        dic_len = struct.unpack('i', struct_dic)[0]
        str_dic = sk.recv(dic_len).decode('utf-8')  # 接收指定长度,获取完整的字典，并解码
        dic = dict(json.loads(str_dic))  # 反序列化得到真正的字典
        return dic

    def main_receive_steps(self, conn, address):
        """
        主要的接收操作流程

        :param conn: 连接成功的套接字对象
        :param address: 发送方的”IP:端口号“
        """
        # 2、接收对方（发送方）发来的数据包，验证身份
        try:
            dic_0 = self.receive_dict(conn)
        except struct.error:
            self.msg_queue.put(config_info.SenderAuthentication_Error)
            return
        except TypeError:
            self.msg_queue.put(config_info.SenderAuthentication_Error)
            return
        if dic_0.get('send_refuse_flag'):
            self.msg_queue.put(config_info.SenderReject_Info)
            return
        elif dic_0.get('ask_flag'):
            try:
                ask_flag = base64.b64decode(dic_0['ask_flag'].encode('utf-8'))
                answer_token = self.rsaOp.decrypt_with_rsa(ask_flag, config_info.PRIVATE_KEY)
                time_str = ''
                for _ in answer_token[90: 110: 2]:
                    time_str += str(_)
                if not (len(answer_token) > 0 and time_str.isdigit()):
                    self.msg_queue.put(config_info.SenderAuthentication_Error)
                    return
                now_time = time.time()
                if now_time - 5 < int(time_str) <= now_time:
                    conn.send(answer_token)
                else:
                    self.msg_queue.put(config_info.SenderAuthentication_Error)
                    return
            except:
                self.msg_queue.put(config_info.SenderAuthentication_Error)
                return
        else:
            self.msg_queue.put(config_info.SenderAuthentication_Error)
            return

        # 3、接收请求后，发送本方的响应数据
        dic_1 = self.receive_dict(conn)
        filename = dic_1['filename']
        file_size = '{:.4f}'.format(dic_1['file_size'] / 1024 / 1024)
        save_ask_bool = messagebox.askyesno(
            title='提示', message=f"是否接收来自{address}的文件：{filename}（大小：{file_size}MB）")
        if not save_ask_bool:
            # 如果拒绝接收文件，退出
            conn.send(b'refuse')
            self.msg_queue.put(config_info.QuitReceive_Info)
            return
        # 如果同意接收文件
        conn.settimeout(15)
        # 提前选择好：文件保存路径
        save_dir = filedialog.askdirectory()
        if not save_dir:
            self.msg_queue.put(config_info.DefaultSavePath_Info)
            save_dir = os.path.join(os.path.expanduser('~'), "Desktop")
        self.msg_queue.put('已确定接收文件的保存路径：' + os.path.join(save_dir, filename))

        pri_key, pub_key = self.rsaOp.create_rsa_keypair()
        conn.sendall(base64.b64encode(b'accept' + pub_key))
        time.sleep(0.1)
        conn.sendall(base64.b64encode(
            self.rsaOp.sign_with_private_key(sign_bytes=pub_key, private_key=config_info.PRIVATE_KEY, mode='bytes')))

        # 4、接收对方（发送方）的数字签名、DES密钥、RSA公钥
        dic_2 = self.receive_dict(conn)
        try:
            des_key = self.rsaOp.decrypt_with_rsa(base64.b64decode(dic_2['des_key'].encode('utf-8')), pri_key)
        except:
            self.msg_queue.put(config_info.DataTransmission_Error)
            return

        # 5、接收文件字节流数据
        with open(save_dir + '/' + filename, 'wb') as f:
            write_bytes_len = 0
            receive_bytes_len = dic_2['file_des_size']
            receive_content = bytes()
            start_time = time.time()
            count = 0

            self.msg_queue.put(config_info.Receiving_Info)
            checksum_hash = HASH.new()

            while write_bytes_len < dic_1['file_size']:
                count += 1
                content_decrypted = b''
                content = conn.recv(self.BUFFER_size)
                print('接收到的数据长度：', content.__len__())
                receive_bytes_len -= content.__len__()
                # 问题（级别：严重，已解决）：TCP分包问题
                # 原因分析：可能是传输大量数据时，计算机接收的缓冲区容易数据堆满溢出，造成后面接收的数据丢失而重传，得到多个小数据包。
                # 解决依据：TCP协议保证，传输的数据顺序不会改变，中间不会被插入其他数据。
                receive_content += content
                if receive_content.__len__() % self.BUFFER_size == 0 or receive_bytes_len == 0:
                    # 数据包重组
                    for i in [receive_content[i:i + self.BUFFER_size]
                              for i in range(0, len(receive_content), self.BUFFER_size)]:
                        content_decrypted += self.desOp.decrypt_with_des(i, des_key)
                    receive_content = b''

                write_bytes_len += content_decrypted.__len__()
                # 写入接收的文件数据
                f.write(content_decrypted)
                checksum_hash.update(content_decrypted)
                # 显示进度
                if count % self.process_count == 0:
                    self.msg_queue.put(f"{filename}\n"
                                       f"接收进度：{write_bytes_len / dic_1['file_size'] * 100}%")

            # 6、验证数字签名
            self.verify_signature(dic_2, checksum_hash)

        # 显示传输用时
        receive_time = time.time() - start_time
        self.msg_queue.put('接收完毕：本次用时 {:.4f} 秒。'.format(receive_time))
