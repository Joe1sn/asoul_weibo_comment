# -*- coding: utf-8 -*-
# @Time    : 2021/9/21 19:41
# @Author  : yuqiannan
# @Project : pythonProject
# @FileName: EditWeiboTime.py
# @Software: PyCharm
# @Version : python3.8
import time
from datetime import datetime
from datetime import timedelta

std_time_format = "%Y-%m-%d %H:%M:%S"
short_std_time_format = "%Y-%m-%d"
today_fotmat = "%Y-%m-%d今天 %H:%M"
yesterday_format = "%Y-%m-%d昨天 %H:%M"
gmt_format = '%a %b %d %H:%M:%S +0800 %Y'


def get_format_datetime(datestr):
    now = datetime.now()
    ymd = now.strftime("%Y-%m-%d")
    y = now.strftime("%Y")
    newstr = datestr
    newdate = now
    if "+0800" in newstr:
        newdate = datetime.strptime(newstr, gmt_format)  # strptime()根据指定的格式把一个时间字符串解析为时间元组
        return newdate
    if "今天" in newstr:
        mdate = time.mktime(time.strptime(ymd + newstr, today_fotmat))  # mktime()用 秒数来表示时间 的浮点数
        newdate = datetime.fromtimestamp(mdate)  # fromtimestamp() 将mdate转换成字符串日期
    elif "分钟前" in newstr:
        newdate = now - timedelta(minutes=int(newstr[:-3]))
        newdate = str(newdate).split('.')[0]
        newdate = datetime.strptime(newdate, std_time_format)
    elif "秒前" in newstr:
        newdate = now - timedelta(minutes=int(newstr[:-2]))
        newdate = str(newdate).split('.')[0]
        newdate = datetime.strptime(newdate, std_time_format)
    elif "-" in newstr:
        if len(newstr) < 6:  # 今年的评论
            mdate = time.mktime(time.strptime(y + "-" + newstr, short_std_time_format))
            newdate = datetime.fromtimestamp(mdate)
        else:
            mdate = time.mktime(time.strptime(newstr, short_std_time_format))
            newdate = datetime.fromtimestamp(mdate)
    elif "昨天" in newstr:
        mdate = time.mktime(time.strptime(ymd + newstr, yesterday_format))
        newdate = datetime.fromtimestamp(mdate) - timedelta(days=1)
    elif "小时前" in newstr:
        newdate = now - timedelta(hours=int(newstr[:-3]))
        newdate = str(newdate).split('.')[0]
        newdate = datetime.strptime(newdate, std_time_format)
    elif "刚刚" in newstr:
        newdate = datetime.now().strptime(std_time_format)
    else:
        newdate = datetime.strptime(newstr, std_time_format)
    return newdate
