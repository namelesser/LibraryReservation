import re
import time
import base64
import sys

import requests
from bs4 import BeautifulSoup
import threading


class User:
    def __init__(self, username, password, roomId, seatIdList):
        self.username = username
        self.password = password
        self.name = "未登录"
        self.roomId = roomId
        self.seatIdList = seatIdList


class LibraryReservation:

    def __init__(self, user):
        self.user = user
        self.host = 'http://172.16.47.84/'
        self.session = requests.session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        }
        self.session.headers = headers
        get_host = self.session.get(self.host, headers=headers)
        get_host.encoding = 'utf-8'
        bs_host = BeautifulSoup(get_host.text, 'lxml')
        # 获取提交表单value
        select_VIEWSTATE = bs_host.select_one('#__VIEWSTATE')
        select_EVENTVALIDATION = bs_host.select_one('#__EVENTVALIDATION')
        select_VIEWSTATEGENERATOR = bs_host.select_one("#__VIEWSTATEGENERATOR")
        self.VIEWSTATEGENERATOR = select_VIEWSTATEGENERATOR['value']
        self.VIEWSTATE = select_VIEWSTATE['value']
        self.EVENTVALIDATION = select_EVENTVALIDATION['value']

    # 获取验证码图片
    def getCode(self, seatId):
        url = "http://172.16.47.84/VerifyCode.aspx?seatid=" + seatId
        get_rsp = self.session.get(url)
        return get_rsp.content

    def diffCode(self, img):  # 识别验证码 并返回  验证码识别调用的是百度免费的,如需更精确可自行更换验证码接口
        img_base64 = base64.b64encode(img)
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
        params = {"image": img_base64, "language_type": ""}
        access_token = '24.fe9b8289d047fe71a6f35572c4cf0b13.2592000.1635336606.282335-22546420'
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        code = response.json()['words_result'][0]['words']
        return code

    def logLibrary(self):  # 登录
        url_log = 'http://172.16.47.84/'
        data_log = {
            '__VIEWSTATE': self.VIEWSTATE,
            '__EVENTVALIDATION': self.EVENTVALIDATION,
            '__VIEWSTATEGENERATOR': self.VIEWSTATEGENERATOR,
            'TextBox1': self.user.username,
            'TextBox2': self.user.password,
            'Button1': '%E7%99%BB++++++%E5%BD%95'
        }

        # 读取登录信息
        post_log = self.session.post(url_log, data=data_log)
        if '帐号或密码错误' in post_log.text:
            return '帐号或密码错误'
        elif '齐大图书馆座位预约系统预约导航' in post_log.text:
            self.getName()
            return '登录成功'
        else:
            return '未知错误' + post_log.text

    def getddlDay(self):  # 获取教室编号ddlDay=[今日||明日] 返回{房间编号:房间号}
        url = 'http://172.16.47.84/DayNavigation.aspx'
        get = self.session.get(url)
        get.encoding = 'utf-8'
        bs_get = BeautifulSoup(get.text, 'lxml')
        select_rooms = bs_get.select('[name=ddlRoom] option')
        rooms_id = {}
        for select in select_rooms:
            rooms_id[select['value'][:-3]] = select.text
        return rooms_id

    def submitCode(self, code_str, roomId, seatId):  # 提交验证码
        url = "http://172.16.47.84/Verify.aspx?seatid=" + roomId + seatId
        data = {
            "__VIEWSTATE": "/wEPDwUKMTcwNzM5ODc3NGRkxk3OrVjxT6behMtQpWcazajx8PyvSuwHitNzRtt/hW8=",
            "__VIEWSTATEGENERATOR": "460BFA5D",
            "__EVENTVALIDATION": "/wEdAANkcH5/1fjT1VTtjqvpdy4W7hv76BH8vu7iM4tkb8en1c34O/GfAV4V4n0wgFZHr3dW6dTyTKTMqYOytm8RFUOrs5GAAAhg2KMXDmC1pQgTog==",
            "TextBox3": code_str,
            "Button1": "提      交"
        }

        headers = {
            'Host': '172.16.47.84',
            'Connection': 'Keep-Alive',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Upgrade-Insecure-Requests': '1',
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://172.16.47.84/Verify.aspx?seatid=" + roomId + seatId,
        }
        post_rsp = self.session.post(url, data=data, headers=headers)
        if '该座位不可用，每天18:20开放明日预约！' in post_rsp.text:
            return '该座位不可用，每天18:20开放明日预约！'
        elif '该座位已经有人预约了，请试试其它座位！' in post_rsp.text:
            return '该座位已经有人预约了，请试试其它座位！'
        elif '错误' in post_rsp.text:
            return '验证码错误'
        else:
            return '预约成功'

    def getddlRoom(self, ddlRoom, ddlDay):  # 获取教室座位 ddlDay=[今日|明日]
        ddlRoom = ddlRoom + "001"
        url_post = 'http://172.16.47.84/DayNavigation.aspx'
        headers = {
            'Referer': 'http://172.16.47.84/DayNavigation.aspx',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data1 = {
            'ddlRoom': ddlRoom,
        }
        post = self.session.post(url=url_post, data=data1, headers=headers)
        post.encoding = 'utf-8'

        bs_post = BeautifulSoup(post.text, 'lxml')
        select = bs_post.select_one('.text input[name=txtSeats]')
        return select['value']

    def getName(self):  # 获取号主姓名
        url = 'http://172.16.47.84/Top.aspx'
        get = self.session.get(url)
        get.encoding = 'utf-8'
        bs_get = BeautifulSoup(get.text, 'lxml')
        select_name = bs_get.select_one('#Label1')
        self.user.name = select_name.text

    def StartSeatSelection(self, roomid):  # 获取座位信息
        seatId = {}
        url = 'http://172.16.47.84/AppSTod.aspx?roomid=' + roomid + '&hei=722&wd=1536'
        get = self.session.get(url)
        get.encoding = 'utf-8'
        bs_get = BeautifulSoup(get.text, 'lxml')
        select_tds = bs_get.select('#DataList1 tr td')
        for td in select_tds:
            bs_td = BeautifulSoup(str(td), 'lxml')
            select_a = bs_td.select_one('a')
            select_img = bs_td.select_one('img')
            if select_a is not None:
                seatId[select_a['href'][-3:]] = select_img['src'][11:14]
        return seatId

    def appointment(self, roomId, seatId):  # 预约今天
        url = 'http://172.16.47.84/SkipToday.aspx?seatid=' + roomId + seatId
        get = self.session.get(url)
        get.encoding = 'utf-8'
        if '该座位已经有人预约了，请试试其它座位！' in get.text:
            return '该座位已经有人预约了，请试试其它座位！'
        elif '您已经预约了今日座位，不可重复预约！' in get.text:
            return "您已经预约了今日座位，不可重复预约！"
        elif '账户被锁定，无法预约！' in get.text:
            return '账户被锁定，无法预约！'
        elif '今日预约成功' in get.text:
            return '今日预约成功'
        return "未知错误,请检查房间号,座位号是否正确"

    def appointmentTomorrow(self, roomId, seatId):  # 预约明日
        # 发起预约请求
        url = "http://172.16.47.84/Verify.aspx?seatid=" + roomId + seatId
        headers = {
            'Host': '172.16.47.84',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': 'http://172.16.47.84/AppSTom.aspx?roomid=' + roomId + '&hei=983&wd=1102',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6',
            'Connection': 'keep-alive'
        }
        get_rsp = self.session.get(url, headers=headers)
        if '该座位不可用，每天18:20开放明日预约！' in get_rsp.text:
            return '该座位不可用，每天18:20开放明日预约！'
        if '该座位已经有人预约了，请试试其它座位！' in get_rsp.text:
            return '该座位已经有人预约了，请试试其它座位！'
        if '您已经预约了明日座位，不可重复预约！' in get_rsp.text:
            return '您已经预约了明日座位，不可重复预约！'
        if '账户被锁定，无法预约！' in get_rsp.text:
            return '账户被锁定，无法预约！'
        # 否则就是返回验证码
        # 获取验证码
        img_content = self.getCode(roomId + seatId)
        # 识别验证码
        code_str = self.diffCode(img_content)
        # 提交验证码
        return self.submitCode(code_str, roomId, seatId)

    def computerSeatDivision(self, ddlDay, ddlRoom):  # 电脑选座 ddlDay=[今日]||[明日]   ddlRoom= 房间号
        url = 'http://172.16.47.84/DayNavigation.aspx'
        data = {
            '__VIEWSTATE': self.VIEWSTATE,
            '__EVENTVALIDATION': self.EVENTVALIDATION,
            'TextBox1': '722',
            'TextBox2': '1536',
            'ddlDay': ddlDay,
            'ddlRoom': ddlRoom,
            'Button1': '电脑分座'
        }
        # 提交验证码
        post_rsp = self.session.post(url, data=data)
        if '该座位不可用，每天18:20开放明日预约！' in post_rsp.text:
            return '该座位不可用，每天18:20开放明日预约！'
        if '该座位已经有人预约了，请试试其它座位！' in post_rsp.text:
            return '该座位已经有人预约了，请试试其它座位！'


def loadAccount():
    userList = []
    with open("account.txt", "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            list = line.split(' ')
            username = list[0]
            password = list[1]
            roomId = list[2]
            seatIdList = list[3:]
            user = User(username, password, roomId, seatIdList)
            userList.append(user)
    return userList


class MyThread(threading.Thread):
    def __init__(self, user, appointment):
        self.appointment = appointment
        threading.Thread.__init__(self)
        self.user = user

    def run(self):
        lr = LibraryReservation(self.user)
        log = lr.logLibrary()
        if log != '登录成功':
            print(self.user.username + ": 账户或者密码错误")
            return log
        rooms = lr.getddlDay()
        try:
            room_name = rooms[self.user.roomId]
        except KeyError:
            print("房间号填写错误,请参照文档.")
            return

        while True:
            seat_number = self.user.seatIdList.__len__()
            for i in range(0, seat_number ):
                if i >= len(self.user.seatIdList):
                    continue
                try:
                    if self.appointment.__eq__("1"):
                        rt = lr.appointment(self.user.roomId, self.user.seatIdList[i])
                    else:
                        rt = lr.appointmentTomorrow(self.user.roomId, self.user.seatIdList[i])
                except KeyError:
                    print(self.user.username + " 预约座位号 " + self.user.seatIdList[i] + " 失败! 原因:" + self.user.seatIdList[
                        i] + "可能座位号错误,如果座位号没有填错,请上 github 反馈.")
                    self.user.seatIdList.remove(self.user.seatIdList[i])
                    continue
                if '成功' in rt:
                    print(rt)
                    print(self.user.username + " 预约座位号 " + self.user.seatIdList[i] + " 成功! ")
                    return
                elif '您已经预约了' in rt:
                    print(self.user.username + " 预约座位号 " + self.user.seatIdList[i] + "失败 原因:" + rt)
                    return
                elif '该座位已经有人预约了' in rt:
                    print(self.user.username + " 预约座位号 " + self.user.seatIdList[i] + "失败 原因:" + rt)
                    self.user.seatIdList.remove(self.user.seatIdList[i])
                elif '账户被锁定' in rt:
                    print(self.user.username + "预约座位号 " + self.user.seatIdList[i] + "失败 原因:" + rt)
                    return
                else:
                    print(self.user.username + " 预约座位号 " + self.user.seatIdList[i] + "失败 原因:" + rt)
            if len(self.user.seatIdList) == 0:
                print(self.user.username + " 所有座位已被预约,请重新选座")
                return


# 返回 现在时间-目标时间
def computeTimeDifference():
    # 格式化成2016-03-20 11:45:39形式
    nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 取出时分秒
    HMS = nowTime.split(' ')[1].split(':')

    # 构造出 当天 19 点 19 分 45 秒
    # 替换时
    aimTime = nowTime.replace(HMS[0], '18')
    # 替换分
    aimTime = aimTime.replace(HMS[1], '19')
    # 替换秒
    aimTime = aimTime.replace(HMS[2], '55')
    # 返回 现在时间-目标时间
    print("现在时间:" + nowTime)
    print("开抢时间:" + aimTime)
    return time.mktime(time.strptime(nowTime, "%Y-%m-%d %H:%M:%S")) - time.mktime(
        time.strptime(aimTime, "%Y-%m-%d %H:%M:%S"))


def checkTime():
    # 时间差=现在时间 - 目标时间
    timeDifference = computeTimeDifference()
    if timeDifference < 0:
        print("距离 18:19:55 还剩" + str(-1 * timeDifference / 60) + "分钟,正在等待中...")
        time.sleep(-1 * timeDifference)
    print("开始抢座!")


def main():
    print("----------------欢迎使用图书馆预约系统---------------------")
    print('-----使用说明:')
    print('----- 抢当天,立即抢当天')
    print('----- 抢第二天,如果当前时间没有到18:20,程序进入等待,到 18:20 开始抢座, 如果当前时间已过 18:20 则立即抢座')
    print('----- 输入格式:账号 密码 教室 座位号 座位号 座位号')
    print('----- 输入 1.抢当天(立即抢)  2.抢第二天(18:20:55 开始抢)')
    appointmentTime = input()
    if not appointmentTime.__eq__("1") and not appointmentTime.__eq__("2"):
        print("输入格式错误,程序结束.")
        sys.exit()
    if appointmentTime.__eq__("2"):
        checkTime()

    userList = loadAccount()
    for i in range(0, userList.__len__()):
        myThread = MyThread(userList[i], appointmentTime)
        myThread.start()


if __name__ == '__main__':
    main()
