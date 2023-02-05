"""
已改进：
1、真正解决：TCP数据大量传输时，存在的数据分段与des解密的矛盾问题。
2、解决：在未接入网络时，程序获取本机内网IP所出现的问题。
"""
import time
import datetime


def getYesterday():
    today = datetime.datetime.today()
    oneday = datetime.timedelta(hours=8)
    yesterday = today - oneday
    return yesterday


print("昨天的日期：", getYesterday())

print(time.strftime('%Y-%m-%d', time.gmtime()))


