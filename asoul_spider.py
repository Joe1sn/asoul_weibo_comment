# -*- coding: utf-8 -*-
# @Time    : 2021/9/28 10:57
# @Author  : Joe1sn
# @Project : a_soul
# @FileName: asoul_spider.py
# @Software: PyCharm
# @Version : python3.8

import requests
from urllib.parse import urlencode
from pyquery import PyQuery as pq
from time_issue import get_format_datetime
from weibo_comment import main_function
import MySQLdb
import time

# 待爬取的关键词
global keyword

SNAP = 4

weibo_base_url = 'https://m.weibo.cn/api/container/getIndex?'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    "Cookie": "XSRF-TOKEN=5ff75c; WEIBOCN_FROM=1110006030; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D20000174%26lfid%3D102803%26uicode%3D20000174; loginScene=102003; SUB=_2A25MQaLXDeRhGeNI6FMT-CjKwjuIHXVvzc6frDV6PUJbkdCOLXKlkW1NSJY6R3BaZjkPMItsSnQWIqzk7OimbuaG; _T_WM=46080388295"
}

global count
global commentsCount
count = 0
index = 0
weibo_bid = {}
retweeted_username = {}
data = {}


# 按页数抓取数据
def get_weibo_page(page):
    # 请求参数
    params = {
        'containerid': '231522type=1&q=#{keyword}#'.format(keyword=keyword),
        'page_type': 'searchall',
        'page': page
    }
    url = weibo_base_url + urlencode(params)
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.json()
        else:
            print("出现错误！！！状态码：", r.status_code)
            exit()
    except requests.ConnectionError as e:
        print('出现错误！', e.args)


# 获取长文本 lid为长文本对应的id
def get_long_text(lid):
    params = {
        'id': lid
    }
    url = 'https://m.weibo.cn/statuses/extend?' + urlencode(params)
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:  # 数据返回成功
            jsondata = r.json()
            tmp = jsondata.get('data')
            return pq(tmp.get("longTextContent")).text()  # 解析返回结构，获取长文本对应内容
    except requests.ConnectionError as e:
        print('出现错误！', e.args)


# 获取json数据中的目的信息
def get_detailed_Data(item):
    global index
    if item.get('isLongText') is False:  # 不是长文本
        Text = pq(item.get("text")).text()  # 仅提取内容中的文本
    else:  # 长文本涉及文本的展开
        Text = get_long_text(item.get('id'))  # 调用函数获取长文本

    # # 保存微博id,为后续爬取微博评论做准备
    # weibo_bid[index] = item.get('bid')

    # # 保存微博发布者用户名,为后续爬取微博评论时的便于保存回复关系
    # retweeted_username[index] = item.get('user').get('screen_name')

    weiboTime = item.get('created_at')  # 获取微博创建时间
    weiboTime = str(get_format_datetime(weiboTime))  # 格式化处理微博时间
    data = {
        'id': item.get('user').get('id'),
        'username': item.get('user').get('screen_name'),
        'created': weiboTime,
        'text': Text,
        'retweeted_username': "",  # 默认无转发关系
        'bid':item.get('bid'),
    }
    try:
        if item.get('retweeted_status'):  # 判断有无转发/回复关系
            data['retweeted_username'] = item.get('retweeted_status').get('user').get('screen_name')
    except:
        save_error(item)
    index += 1

    return data


# 解析json数据，获取目的信息
def parse_weibo_page(json):
    global data
    items = json.get('data').get('cards')
    for item in items:
        if item.get('mblog'):  # 可直接获取mblog
            item = item.get('mblog')
            data = get_detailed_Data(item)
        elif item.get('card_group'):  # mblog可能隐藏在card_group之下
            item = item.get('card_group')
            for k in item:
                k_item = k.get('mblog')
                if k_item:
                    data = get_detailed_Data(k_item)
        yield data


# 处理sql语句
def add(uid, username, update_time, source_user, comment,bid):
    cmd = 'insert into {table_name} values ("{uid}","{username}","{update_time}","{source_user}","{comment}","{bid}");'\
        .format(table_name=keyword, uid=uid, username=username, update_time=update_time, \
                source_user=source_user, comment=comment.replace("'", "''").replace("\"", "\\\""),bid=bid,)
    return cmd

#处理报错
def save_error(msg):
    with open("error.log", "w") as file:
        file.writelines(msg)

def get_comment(word,mode):
    server = 1
    if server:
        db = MySQLdb.connect(
            "localhost",
            "admin",
            "MjfoyX3gUF0j5",
            "WeiboComment",
            charset='utf8mb4'
        )
    else:
        db = MySQLdb.connect(
            "localhost",
            "root",
            "J8Ltt50tVC297Y612I7T",
            "weibocomment",
            charset='utf8mb4'
        )

    control = db.cursor()

    global keyword
    keyword = word
    page = 0
    # 爬取相关话题微博
    while 1:  # 瀑布流下拉式，加载
        if mode:
            page = 4
        else:
            page += 1

        print("正在获取第%d页数据..." % page)
        json = get_weibo_page(page)
        print("第%d页数据获取完成！" % page)
        if json.get('ok') == 0:
            print("第%d页无数据！" % page)
            print("爬取完成！共获取%d页数据" % (page - 1))
            break
        results = parse_weibo_page(json)
        for result in results:  # 需要存入的字段
            if result.get('id'):  # 判断数据是否为空，若不为空，则传入数据库
                uid = str(result.get('id'))
                username = result.get('username')
                update_time = result.get('created')
                source_user = result.get('retweeted_username')
                comment = result.get('text')
                bid = result.get('bid')
                sql = add(uid=uid, username=username, update_time=update_time, source_user=source_user,
                          comment=comment,bid=bid)
                global count
                count += 1
                control.execute(sql)
                db.commit()
        time.sleep(SNAP)  # 爬取时间间隔
        mode = 0


    # 爬取相关话题微博的评论
    sql = "select bid,source_user from `{table_name}`;".format(table_name=keyword)
    control.execute(sql)
    bid_username = tuple(set(control.fetchall()))

    for i in range(0, len(bid_username)):
        commemts = main_function(bid_username[i][0], bid_username[i][1])
        # 保存爬取的相关话题微博的评论
        for L in commemts:
            sql = add(uid=str(L[0]), username=L[1], update_time=L[2], source_user=str(L[3]), comment=L[4],\
                      bid=bid_username[i][0])
            try:
                control.execute(sql)
                db.commit()
            except:
                print(sql)
                save_error()
            count += 1
    db.close()
