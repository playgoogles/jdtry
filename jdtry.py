# 京东试用 学习用的
# 配置文件的写入和读取、图画、cookie的存储pickle、cookie的更新、导入cookie
# -*- coding: utf-8 -*-
import requests
import time
import matplotlib.pyplot as plt
import random
import json
import re
import pickle
from bs4 import BeautifulSoup
import configparser
from tqdm import trange
import os
import socket
import datetime


class jdobj:
    def __init__(self):
        self.name = ""
        self.time = 0
        self.amount = ""
        self.activeid = ""
        self.price = ""
def getmidstring(html, start_str, end):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()
def write_ini(inikey, inivaluse, str):
    config = configparser.ConfigParser()
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    config.read(parent_dir  + "/info_date.ini", encoding = 'utf-8')
    convaluse = config.set(inikey, inivaluse, str)
    config.write(open(parent_dir + "/info_date.ini", "w"))
    return convaluse
def read_ini(inikey, inivaluse, filepath):
    config = configparser.ConfigParser()
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    config.read(parent_dir  + "/" + filepath,encoding = 'utf-8')
    convaluse = config.get(inikey, inivaluse)
    return convaluse
class jdtry:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
        }
        self.sess = requests.Session()
        self.cookies = {

        }
    def check_login(self):
        now_time = datetime.datetime.now()
        print ('当前时间' + str(now_time) + "正在检测登录状态！")
        if os.path.exists('cookie') == False:
            return False
        else:
            parent_dir = os.path.dirname(os.path.abspath(__file__))
            with open(parent_dir + '/cookie', 'rb') as f:
                cookie = requests.utils.cookiejar_from_dict(pickle.load(f))
            url = "https://try.jd.com/activity/getActivityList"
            res = requests.get(url)
            html_str = res.text
            besoup = BeautifulSoup(html_str, features='lxml')
            div_str = str(besoup.find_all('div', attrs={'class': "con"}))
            items = BeautifulSoup(div_str, "html.parser")
            a = items.find_all('li')  # 类型：resultset
            b = getmidstring(str(a[1]), 'activity_id="', '"')
            url = 'https://try.jd.com/migrate/getActivityById?id=' + b
            head = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                'ContentType': 'text/html; charset=utf-8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Host': 'try.jd.com',
                'Referer': 'https://try.jd.com/public'
            }
            res = requests.get(url, headers=head, cookies=cookie)
            c = json.loads(res.text)
            d = c['data']['login']
            return d
    def login(self):
        urls = (
            'https://passport.jd.com/new/login.aspx',
            'https://qr.m.jd.com/show',
            'https://qr.m.jd.com/check',
            'https://passport.jd.com/uc/qrCodeTicketValidation'
        )

        input('请打开京东扫码，按回车键继续：')
        response = self.sess.get(
            urls[0],
            headers=self.headers
        )
        self.cookies.update(response.cookies)# 初始化JDcookie,这一步cookie用于检查二维码是否扫码
        # 获取二维码
        response1 = self.sess.get(
            urls[1],
            headers=self.headers,
            cookies=self.cookies,
            params={
                'appid': 133,
                'size': 147,
                't': int(time.time() * 1000),
            }
        )
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        with open(parent_dir +'/eth.png', 'wb') as f:
            f.write(response1.content)
        img = plt.imread(parent_dir + '/eth.png')
        plt.imshow(img)
        plt.show()
        # 显示二维码
        # 更新协议头
        self.headers['Host'] = 'qr.m.jd.com'
        self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'
        retry_times = 100  # 尝试100次
        while retry_times:
            retry_times -= 1
            response = self.sess.get(
                urls[2],
                headers=self.headers,
                cookies=self.cookies,
                params={
                    'callback': 'jQuery%d' % random.randint(1000000, 9999999),
                    'appid': 133,
                    'token': response1.cookies['wlfstk_smdl'],
                    '_': int(time.time() * 1000)
                }
            )
            if response.status_code != requests.codes.OK:
                continue
            rs = json.loads(re.search(r'{.*?}', response.text, re.S).group())
            # code == 200 说明扫码成功
            if rs['code'] == 200:
                print(f"{rs['code']} : {rs['ticket']}")
                qr_ticket = rs['ticket']
                break
            elif rs['code'] == 201:
                # 还没有确认登录
                print(f"{rs['code']} : {rs['msg']}")
                time.sleep(3)

        # 扫码后登录完成
        self.headers['Host'] = 'passport.jd.com'
        self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'
        response = requests.get(
            urls[3],
            headers=self.headers,
            cookies=self.cookies,
            params={'t': qr_ticket},
        )
        res = json.loads(response.text)
        if not response.headers.get('p3p'):
            if 'url' in res:
                print(f"需要手动安全验证: {res['url']}")
                return False
            else:
                print(res)
                print('登录失败!!')
                return False
        # 登录成功
        self.headers['P3P'] = response.headers.get('P3P')
        self.cookies.update(response.cookies)
        # 保存cookie
        with open(parent_dir + '/cookie', 'wb') as f:
            pickle.dump(self.cookies, f)
        print("登录成功")
        return True

    def get_price(self, product_list):
        now_time = datetime.datetime.now()
        print ('当前时间' + str(now_time) + '正在查询价格')
        for i in range(len(product_list)):
            sku_id = product_list[i].skuid
            url = "https://p.3.cn/prices/mgets?skuIds=" + sku_id + "&origin=2"
            head = self.headers
            head['cache-control'] = 'max-age=0'
            head['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            self.headers = head
            for n in range(5):
                try:
                    res = requests.get(url, headers=head)
                    break
                except requests.exceptions.RequestException as e:
                    print(e)
            jsStr = res.content
            jsonArr = json.loads(jsStr)
            product_list[i].price = getmidstring(str(jsonArr[0]), "'p': '", "'")
        return product_list
    def try_post(self, plan):
        with open('cookie', 'rb') as f:
            cookie = requests.utils.cookiejar_from_dict(pickle.load(f))
        head = self.headers
        head['Host'] = 'try.jd.com'
        head['Referer'] = 'https://try.jd.com/938237.html'
        #先看看有没有申请过
        url = "https://try.jd.com/migrate/getActivityById?id=" + plan.activeid
        res = requests.get(url, headers=self.headers, cookies=cookie)
        jsonArr = json.loads(res.text)
        print (jsonArr)
        temp = getmidstring(str(jsonArr), "'shopInfo': ",'}')
        temp2 = getmidstring(str(jsonArr), "'data': ",'}')
        temp3 = getmidstring(str(jsonArr), "'submit': ",',')
        if temp == None:
            plan.isposted = True
        elif temp2 == None:
            plan.isposted = True
        elif temp3 == None:
            plan.isposted = True
        else:
            plan.isposted = jsonArr['data']['submit']
        if plan.isposted == True:
            return
        else:
            plan.shopid = jsonArr['data']['shopInfo']['shopId']
            head = self.headers
            head['Host'] = 'try.jd.com'
            head['Referer'] = 'https://try.jd.com/938237.html'
            url = 'https://try.jd.com/migrate/follow?_s=pc&venderId=' + str(plan.shopid)
            requests.get(url, headers=head, cookies=cookie)
            url = 'https://try.jd.com/migrate/apply?activityId=' + plan.activeid + '&source=0'
            response = requests.get(url, headers=head, cookies=cookie)
            s = response.text
            time.sleep(5)
            print( s)
            if s.find("您的申请次数已超过上限") != -1:#不等于-1，即寻找到此文本,向微信报错
                requests.get('https://sc.ftqq.com/方糖密钥.send?text=京东今日申请达到上限')
                return "申请次数已满"
            url = 'https://try.jd.com/migrate/unfollow?_s=pc&venderId=' + str(plan.shopid)  # https://try.jd.com/migrate/unfollow?_s=pc&venderId=10138593取关
            requests.get(url, headers=head, cookies=cookie)
        return
    def get_product_list(self):#获取试用商品列表,返回的uls是一个数组，每个成员内包含商品名称和编号skd_id
        cids_list = read_ini('appbase','cids_list','info.ini')
        cids_list = cids_list.split(',')
        uls = []
        for cids in cids_list:
            for page in range(15):
                url = "https://try.jd.com/activity/getActivityList?page=" + str(
                    page + 1) + '&cids=' + str(cids)  # &cids=1320通过cdds来确定分区
                res = requests.get(url)
                html_str = res.text
                besoup = BeautifulSoup(html_str, features='lxml')
                div_str = str(besoup.find_all('div', attrs={'class': "con"}))
                items = BeautifulSoup(div_str, "html.parser")
                a = items.find_all('li')  # 类型：resultset
                uls.append(a)
        product = []
        p = len(uls)
        print('当前时间'+str(datetime.datetime.now())+'正在查询商品')
        for o in range(p):
            for n in uls[o]:
                temp = jdobj()
                t1 = getmidstring(str(n), 'sys_time="', '"')  # 目前时间
                t2 = getmidstring(str(n), 'end_time="', '"')
                t3 = (int(t2) - int(t1)) / 3600000  # 剩余时间
                temp.name = getmidstring(str(n), '<div class="p-name">', '</div>')
                temp.time = t3
                temp.skuid = getmidstring(str(n), 'sku_id="', '"')
                temp.activeid = getmidstring(str(n), 'activity_id="', '"')
                temp.amount = getmidstring(str(n), '>提供<b>', '</b>份')
                product.append(temp)
        return product
    def rank(self, product_list):
        #第一步筛选价格
        #第二部筛选关键词
        #时间就不过滤了
        key_word_list = read_ini('appbase', 'key_word_list', 'info.ini')
        key_word_list = key_word_list.split(',')
        print (key_word_list)
        ex_price = read_ini('appbase', 'ex_price','info.ini')
        plan = []
        for temp in product_list:
            if float(temp.price) > float(ex_price):
                plan.append(temp)
        for temp in plan:
            for key_word in key_word_list:
                if temp.name.find(key_word) != -1:  # 有过滤词
                    plan.remove(temp)
                    break
        return plan



def get_try():
    now_time = datetime.datetime.now()
    print ('当前时间' + str(now_time) + "开始执行京东试用脚本！")
    jd = jdtry()
    if jd.check_login() == False:
        requests.get('https://sc.ftqq.com/方糖密钥.send?text=京东cookie已失效')
        print ('cookie失效，请打开手机扫码')
        islogin = jd.login()
        if islogin == True:
            print ('登录成功')
            product = jd.get_product_list()
            product = jd.get_price(product)
            product = jd.rank(product)
            requests.get(
                'https://sc.ftqq.com/方糖密钥.send?text=预计最大申请数量：' + str(
                    len(product)))
            for plan in product:
                res = jd.try_post(plan)  # 一条一条申请
                if res == "申请次数已满":
                    return
            # 跑完全部任务都没跑满
            requests.get('https://sc.ftqq.com/方糖密钥.send?text=今日京东未跑满')
            return


        else:
            print ('登录失败')

    else:
        print ('登录有效')
        product = jd.get_product_list()
        product = jd.get_price(product)
        product = jd.rank(product)
        requests.get('https://sc.ftqq.com/方糖密钥.send?text=预计最大申请数量：'+str(len(product)))
        for plan in product:
            res = jd.try_post(plan)#一条一条申请
            if res == "申请次数已满":
                return
        #跑完全部任务都没跑满
        requests.get('https://sc.ftqq.com/方糖密钥.send?text=今日京东未跑满')
        return
# 737,9987,670,1620,1316,1325,12218,5025,12259
def run ():
    last_date = read_ini("appbase", "last_date", 'info_date.ini')
    now_time = datetime.datetime.now()
    now_date = now_time.strftime('%x')
    print (last_date,now_date)
    if now_date != last_date:

        get_try()
        write_ini("appbase", "last_date", str(now_date))
        print (str(now_time) + "今日申请完毕，待机1小时。")
        time.sleep(3600)
    else:
        print (str(now_time) + "今日已经申请过，待机中。")
        time.sleep(3600)


        return
    return
def main():
    while True:
        run()
    return
if __name__ == '__main__':
    main()
