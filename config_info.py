PRIVATE_KEY = b'''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA1uVdHJIdvRnvM12k53m1g4p2PtKplu7ZJqHbSCqd5SH/EGl4
5sZhDpNPuMTVPH/88FFgaMHNkJzsbuMScWChXgI7quPqXvnLGhjJcuwQakKYvym7
lqIXuA6k1AqrOiqGhAS6PXgNh60JcrZrxO3WHKq9HkD8XF2W2ZD1cQVRznvU66rY
OvneKdedGVpqCLPhcm9TwDhXuW6jicPXx5W6bP0OyeV3G/DX4xUeJoiN8PRh0g5n
qH/qLOehy7a/xw+fcebxuGOXaR0MizZgySUybO2pYL5u+a5giSfBUKfdsR6MUPml
+HXTOJbqPdXER+E2A55cWiqqDuQRcJNYarIu2wIDAQABAoIBABJvPpuS1UZBkUmA
wQKyaCXOnPIqtC2kc7BitiLstPrQ/cZ0pdB2OCE99drN19UGzbX35SNXbMD5FTc1
94EOXwlne6LfRl27Y/brJWzcX1QePmg3tkXnxc0eRHmEKMgmmb99gFSBlfeLmoHi
sEAGfxWad/q+bGeoB6bGTqfRYwEpagWkCVcoZsZF89H+O5daa52vkedN0f3XwdgD
QHdQ7AKhgUp3yalkmALMrOf7je7kMMutW3wws0lFhux2pGbAopY4TsPmu8XSZeh5
0iT0ZIgneAeRNHv1ai0jW6OnK7Xn6t5kU2RIamMAopY++bmE5Hpzi8spktgZZ1FY
zYYfcbECgYEA4O3FzUUYpOG9s59Y8FkJtymR+5HZsvd9ofCm/k0wd94+wZiNkrr4
FlK+JSu9OhR7Yj22QUPK6XJ6eOPBzyboh+3dy5PEkM/o4M3BySEjSgh2He/g0LCu
oX9UErYL7iDIw6m7ct2sfVbF+GKwTXtzTYtCY7+6JZ3zoQiRRf9IkWcCgYEA9JTL
3NMC7EvNUTVtUnQal+3UtiBbfPmY3S4lTBxBl0YXSADA5A1EGUrpnCYIKq1K1vfJ
Y50SSH5IW7lZK2TRg/EwWwuwzKbynLgYN+fS2PoBU5E7Dfnc83hRJGdMpGGh+YtS
J2t75RJmxmAJ3vYFRJKWJ3j0S+autmfSCbnHym0CgYBy7wyz5yrAldkpf7MinVyp
i0RdGBn1qSE5Lo8mQqsRlS7cHee5onBCd+VReRgoJW8mtAH9N3bn8udB/p96Cpen
XZSIAenfVV3aAUmUTKqLmedBROHLwXx6aWW8aemOtJHh6UkvWLZbFYvzb/pGnV49
sXsrHT0xG5TyJD6XVeru4QKBgC4znX8NbVPtzc81ZH1a6Vsh1jjBTAcDr1i4ytrh
y5Ij72numoF58A9HE3InzQsiySxqimSC211OXaTWEn4cAWgHO7c3MiK2tsXcENce
t7m9IFsE6D7voEltxQY3bUbwGoTlSJOhvjm7jCaVJcg0eTJG7o5uTte3r/FNE2Q6
7/7RAoGBAM2PA+weP9U+uwuJ6s2IPLTrbIXPTQ49mVChLaJnqau2Tokhf8vYKaJJ
z/76KGz15ItnZ9+D1QvPm52VZx+g7v4Iz9TUMWIBvT+7K4Hsf1zUSKp/aA0AdOQO
juglLBx3/ASmCCI64WuXJj+lpuwW+ow/X/+t6gqDq4s7r2p+l6nD
-----END RSA PRIVATE KEY-----'''

PUBLIC_KEY = b'''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1uVdHJIdvRnvM12k53m1
g4p2PtKplu7ZJqHbSCqd5SH/EGl45sZhDpNPuMTVPH/88FFgaMHNkJzsbuMScWCh
XgI7quPqXvnLGhjJcuwQakKYvym7lqIXuA6k1AqrOiqGhAS6PXgNh60JcrZrxO3W
HKq9HkD8XF2W2ZD1cQVRznvU66rYOvneKdedGVpqCLPhcm9TwDhXuW6jicPXx5W6
bP0OyeV3G/DX4xUeJoiN8PRh0g5nqH/qLOehy7a/xw+fcebxuGOXaR0MizZgySUy
bO2pYL5u+a5giSfBUKfdsR6MUPml+HXTOJbqPdXER+E2A55cWiqqDuQRcJNYarIu
2wIDAQAB
-----END PUBLIC KEY-----'''

Welcome_Info = "欢迎使用安全文件传输工具！\n" \
               "==========================================\n" \
               "注：本工具适用于局域网的文件加密传输，并自动进行收发两端的数字签名校验，无需用户另行操作，具有较高的可操作性。\n" \
               "“发送”功能需输入发送方或接收方的内网IP地址与对应的端口（即：使用本工具“发送”功能开放的端口，下同），且须提前指定正确的文件路径；\n" \
               "“接收”功能需输入发送方或接收方的内网IP地址与对应的端口。\n" \
               "双方可事先约定均使用某一方的内网IP地址与对应的端口，以确保文件传输的连接成功。\n" \
               "==========================================\n"
WaitForReceiverConnection_Info = "已绑定本机端口，开始等待接收方的连接……"
WaitForSenderConnection_Info = "已绑定本机端口，开始等待发送方的连接……"
ReceiveTimeout_Info = '等待时间已超过设置的等待时间（%s秒），已退出接收状态。'
SendTimeout_Info = '等待时间已超过设置的等待时间（%s秒），已退出接收状态。'
SenderReject_Info = '发送方拒绝本方的接收请求，已退出接收状态。'
ReceiverReject_Info = '接收方拒绝本方的发送请求，已退出发送状态。'
DefaultSavePath_Info = '未选择接收文件的保存路径，默认选择：本机桌面。'
QuitSend_Info = '已退出发送状态。'
QuitReceive_Info = '已退出接收状态。'
StartToSend_Info = '对方同意接收，开始发送文件……'
Receiving_Info = '正在接收文件……'
FileVerification_Info = '文件校验结果：一致，下载成功！'

WarningTitle = '警告'
TooManyThreads_Warning = '当前本工具程序正在运行的任务数量已超过4个，运行过多可能影响程序的正常使用，请结合本机性能及运行环境进行操作。'
FilePath_Warning = "文件路径不存在，请选择正确的文件路径。"
IPNotPrivate_Warning = "IP地址错误：不属于局域网内部IP地址。"
IPFormal_Warning = 'IP地址错误：不属于正确格式的IP地址。'
Port_Warning = "端口号错误。"

SetReceiveServer_Error = '无法设置为接收服务端，请检查端口占用等相关信息后重新尝试。'
SetSendServer_Error = '无法设置为发送服务端，请检查端口占用等相关信息后重新尝试。'
Connection_Error = '连接出现问题，请检查相关信息后，再进行尝试。'
Disconnection_Error = '连接中断，对方可能已断开连接。'
SenderAuthentication_Error = '接收的数据存在错误，连接到的对方可能不是使用本程序的发送方，连接已断开。'
ReceiverAuthentication_Error = '接收的数据存在错误，连接到的对方可能不是使用本程序的接收方，连接已断开。'
DataTransmission_Error = '数据传输存在问题，请重新尝试发送！'
Timeout_Error = "对方在一段时间内没有响应，连接失败。"
PortClosed_Error = "对方主机未开放对应的端口，连接失败。"
IP_Address_Error = "IP地址错误，连接失败。"
FileVerification_Error = '文件校验结果：不一致，下载的文件存在问题。'
