# -*- coding: utf-8 -*-
# @Time    : 2021/9/28 10:57
# @Author  : Joe1sn
# @Project : a_soul
# @FileName: weibo_comment.py
# @Software: PyCharm
# @Version : python3.8

import time
import re
import requests
from time_issue import get_format_datetime

comments_list = []

SNAP = 3  # 间隔时间 s
LONGSNAP = 60


# 发送请求、获取数据
def get_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Cookie": "XSRF-TOKEN=5ff75c; WEIBOCN_FROM=1110006030; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D20000174%26lfid%3D102803%26uicode%3D20000174; loginScene=102003; SUB=_2A25MQaLXDeRhGeNI6FMT-CjKwjuIHXVvzc6frDV6PUJbkdCOLXKlkW1NSJY6R3BaZjkPMItsSnQWIqzk7OimbuaG; _T_WM=46080388295"
    }
    try:
        r = requests.get(url, headers=headers)
        print(url)
        if r.status_code == 200:
            return r.json()
        else:
            print("服务器拒绝连接，状态码：", r.status_code)
            return "WAIT"
    except:
        return "ERROR!!!"


# 处理评论内容中的a、span标签
def edit_comments(comments):
    comments = comments.replace('<span class="url-icon"><img alt=', "").replace('</span>', "")

    replace_elements_span = re.findall(r'].*>', comments)
    replace_elements_a_1 = re.findall(r'<a.*?#', comments)
    replace_elements_a_2 = re.findall(r'<a.*?>', comments)

    for i in range(0, len(replace_elements_span)):
        comments = comments.replace(replace_elements_span[i], "]")

    for j in range(0, len(replace_elements_a_1)):
        comments = comments.replace(replace_elements_a_1[j], "")

    for k in range(0, len(replace_elements_a_2)):
        comments = comments.replace(replace_elements_a_2[k], "").replace("</a>", "")

    return comments


# 解析json数据、获取目的信息
def get_comments(json_data, lists, username):
    id = ""
    user_name = ""
    time = ""
    comments = ""
    reply = ""
    bid = ""
    datas = json_data.get('data').get('data')

    for data in datas:
        for key, value in data.items():
            if key == "user":  # 获取发表评论用户的信息
                user_name = data.get("user").get("screen_name")
                id = data.get("user").get("id")
            elif key == "text":  # 获取用户评论
                comments = data.get("text")
                reply = username  # 评论默认回复给源微博
                if "回复<a" in comments:  # 若评论中有"回复<a"，则该评论不是回复源微博
                    # 利用正则表达式确定该评论回复给谁
                    reply = re.findall(r'>(.*?)</a>', comments)
                    # 提取出评论信息
                    reply_info = re.findall(r'回复<a.*</a>', comments)
                    comments = comments.replace(reply_info[0], "").replace(":", "")
                if "<span" or '</a>' in comments:  # 清洗评论信息，去除评论中的的span标签
                    comments = edit_comments(comments)
            elif key == "created_at":  # 获取评论发表时间
                time = data.get("created_at")
                time = str(get_format_datetime(time))

        lists.append([id, user_name, time, reply, comments])


# 获取微博评论主函数
def main_function(weibo_bid, retweeted_username):
    num = 1
    lists = []
    print("开始爬取%s的微博评论。。。" % retweeted_username)
    while 1:
        url = 'https://m.weibo.cn/api/comments/show?id=' + str(weibo_bid) + '&page=' + str(num)
        json_data = get_data(url)
        if json_data == "WAIT":
            time.sleep(LONGSNAP)
            continue
        time.sleep(SNAP)
        num += 1
        if json_data.get('ok') == 0:
            print(retweeted_username + "的微博评论抓取结束！共%d页！" % (num - 2))
            break
        else:
            get_comments(json_data, lists, retweeted_username)
    return lists
