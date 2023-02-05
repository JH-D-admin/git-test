import secrets
from Crypto.PublicKey import RSA
import Crypto.Signature.PKCS1_v1_5 as sign_PKCS1_v1_5
from Crypto.Cipher import PKCS1_v1_5, DES
from Crypto import Random
from Crypto.Hash import SHA1 as HASH
from Crypto.Util.Padding import pad, unpad


class RSAOperation:
    def __init__(self):
        """初始化参数"""
        self.key = RSA.generate(2048)

    def create_rsa_keypair(self) -> (bytes, bytes):
        """
        生成一对RSA算法的公钥与私钥

        :return: (私钥, 公钥)
        """
        private_key = self.key.export_key()
        public_key = self.key.publickey().export_key()
        return private_key, public_key

    @staticmethod
    def encrypt_with_rsa(plain_text: bytes, public_key: bytes) -> bytes:
        """
        公钥加密

        :param plain_text: 需加密的字节
        :param public_key: RSA公钥字节
        :return: 加密的字节
        """
        cipher_pub_obj = PKCS1_v1_5.new(RSA.importKey(public_key))
        secret_bytes = cipher_pub_obj.encrypt(plain_text)
        return secret_bytes

    @staticmethod
    def decrypt_with_rsa(secret_bytes: bytes, private_key: bytes) -> bytes:
        """
        私钥解密

        :param secret_bytes: RSA加密的字节
        :param private_key: 对应的RSA私钥字节
        :return: 解密的字节
        """
        cipher_pri_obj = PKCS1_v1_5.new(RSA.importKey(private_key))
        plain_bytes = cipher_pri_obj.decrypt(secret_bytes, Random.new().read)
        return plain_bytes

    def sign_with_private_key(self, private_key: bytes, mode: str, filepath=None, sign_bytes=None) -> bytes:
        """
        私钥签名

        :param private_key: RSA私钥字节
        :param filepath: 需签名的文件路径
        :param sign_bytes: 需签名的字节
        :param mode: 签名的模式
        :return: 数字签名值（bytes）
        """
        signer_pri_obj = sign_PKCS1_v1_5.new(RSA.importKey(private_key))
        sign_hash = b''
        if mode == 'bytes':
            sign_hash = HASH.new()
            sign_hash.update(sign_bytes)
        elif mode == 'file':
            sign_hash = self.toHash_fileBytes(filepath=filepath)
        signature = signer_pri_obj.sign(sign_hash)
        return signature

    @staticmethod
    def verify_with_public_key(signature: bytes, checksum_hash: HASH, public_key: bytes):
        """
        公钥验签

        :param signature: 数字签名值
        :param checksum_hash: 对文件内容完成数字摘要的Hash对象
        :param public_key: 数字签名的对应 RSA 公钥
        :return: 布尔值（True or False）
        """
        verifier = sign_PKCS1_v1_5.new(RSA.importKey(public_key))
        return verifier.verify(checksum_hash, signature)

    @staticmethod
    def toHash_fileBytes(filepath=None, sec=1024 * 1024) -> HASH:
        """
        使用SHA256为字节流生成数字摘要

        :param filepath: 文件的路径
        :param sec: 分段读取的字节长度
        :return: 数字摘要 Hash 对象
        """
        checksum_hash = HASH.new()
        with open(filepath, "rb") as f:
            while True:
                read_bytes = f.read(sec)  # 每次读取指定字节长度
                if not read_bytes:
                    break
                checksum_hash.update(read_bytes)
        return checksum_hash


class DESOperation:
    def __init__(self):
        self.des_mode = DES.MODE_CBC
        self.Des_IV = b"\x02\x00\x00\x05\x03\x01\x02\x03"

    @staticmethod
    def create_des_key() -> bytes:
        """
        生成安全性高的DES密钥

        :return: DES密钥
        """
        return secrets.token_bytes(8)

    def encrypt_with_des(self, text: bytes, Des_Key: bytes) -> bytes:
        """
        DES加密

        :param text: 需加密的字节
        :param Des_Key: DES密钥
        :return: 加密后的字节
        """
        cipher = DES.new(Des_Key, self.des_mode, self.Des_IV)
        return cipher.encrypt(pad(text, 8))  # 返回加密后的密文

    def decrypt_with_des(self, text: bytes, Des_Key: bytes) -> bytes:
        """
        DES解密

        :param text: 需解密的字节
        :param Des_Key: DES密钥
        :return: 解密后的字节
        """
        cipher = DES.new(Des_Key, self.des_mode, self.Des_IV)
        plaint = cipher.decrypt(text)
        return unpad(plaint, 8)


#     with open('Amy Deasismont - Heartbeats.mp3', 'rb') as f1:
#         print(f.read() == f1.read())
# text = b'1' * 9
# pad_t = pad(text, 8)
# print(len(pad_t))
# en = a.encrypt_with_des(text, b'12345678')
# print(en, len(en))
# de = a.decrypt_with_des(en, b'12345678')
# print(de)
# print()
# with open("b.mp3", 'wb') as f1:
#     with open('a.mp3', 'rb') as f:
#         while True:
#             b = f.read(1024 * 1024)
#             c = a.decrypt_with_des(b, b'\x16i\xe8\x11\xe5\xe8\xaf0')
#             f1.write(c)

# [text_bytes[i:i + sec] for i in range(0, len(text_bytes), sec)]

