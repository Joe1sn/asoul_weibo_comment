# -*- coding: utf-8 -*-
# @Time    : 2021/9/28 10:57
# @Author  : Joe1sn
# @Project : a_soul
# @FileName: start.py
# @Software: PyCharm
# @Version : python3.8
from asoul_spider import get_comment

if __name__ == '__main__':
    keyword_list = ["asoul", "嘉然", "向晚", "珈乐", "乃琳"]
    for i in keyword_list:
        get_comment(i)
