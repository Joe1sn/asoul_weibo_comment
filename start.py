# -*- coding: utf-8 -*-
# @Time    : 2021/9/28 10:57
# @Author  : Joe1sn
# @Project : a_soul
# @FileName: start.py
# @Software: PyCharm
# @Version : python3.8
from asoul_spider import get_comment
import os

os.system('toilet -f standard "Asoul Spider" | lolcat')

if __name__ == '__main__':
    keyword_list = ["asoul", "嘉然", "向晚", "珈乐", "乃琳", "贝拉"]
    i = 0
    ch = input("是否上次爬取失败? Y/N\n")
    if ch == 'Y':
        i = int(input("Keyword ID> "))
    ch = input("继续上次爬取? Y/N\n")
    while i < len(keyword_list):
        if ch == 'Y':
            get_comment(keyword_list[i],1)
            ch = 'N'
        else:
            get_comment(keyword_list[i],0)
        i+=1
