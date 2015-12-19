# encoding=utf-8
from __future__ import division
import requests
import time
from bs4 import *
import re
import json
import numpy as np
import pickle
import requests.utils
import os
import traceback


class XSQST(object):

    def __init__(self):
        self.s = requests.session()
        return

    def login(self):
        if os.path.exists('cookies.txt'):
            with open('cookies.txt') as f:
                cookies = pickle.load(f)
                self.s.cookies = cookies

        else:
            try:
                b = open('b.txt', 'rb')
                lines = b.readlines()
                email = unicode(lines[0].strip(), 'gbk')
                password = lines[1].strip()
                nga = lines[2].strip()
                b.close()
            except:
                print 'open b.txt failed'
                time.sleep(10)
            req = self.s.get('https://account.178.com/')
            req2 = self.s.get('https://account.178.com/q_vcode.php?_act=gen_reg')
            o = open('a.jpg', 'wb')

            o.write(req2.content)
            o.close()
            # txtcode = pytesser.image_file_to_string('a.jpg')
            # print txtcode
            vcode = raw_input('input code:')
            self.Formdata = {
                '_': '',
                '_act': 'login',
                'email': email,
                'print': 'login',
                'password': password,
                'to': 'http://i.178.com',
                'vcode': vcode
            }
            print self.Formdata
            req3 = self.s.post('https://account.178.com/q_account.php', data=self.Formdata)
            with open('cookies.txt', 'w') as f:
                pickle.dump(self.s.cookies, f)

        pp = {
            'id': '1',
            'nga': 'nga'
        }

        print pp
        reqs = self.s.get('http://s1.xsqs.178.com/game.php', params=pp)
        print reqs.content
        soup = BeautifulSoup(reqs.content)
        soup_body_div_div_iframe = soup.div.div.iframe
        new_url = soup_body_div_div_iframe['src']
        reqs1 = self.s.get(new_url)
        soup = BeautifulSoup(reqs1.content)
        souphead = soup.head
        # print souphead
        print souphead
        scpritlist = souphead.find_all('script')
        LoadGameScriptSoup = scpritlist[2]
        LoadGameScriptUrl = 'http://game.178mxwk.90tank.com/' + LoadGameScriptSoup['src']
        # print 'LoadGameSriptUrl', LoadGameScriptUrl
        targets = scpritlist[-1].text
        # print targets
        patter = r"sid='(.*?)'"
        patternum = r"\d\d\d\d"
        self.newsid = re.findall(patter, targets)[-1]
        self.newnum = re.findall(patternum, targets)[-1]
        # print 'newsid', self.newsid
        # print 'newnum', self.newnum
        posturl = 'http://game.178mxwk.90tank.com/' + soup.body.form['action']
        value = soup.body.input['value']
        # print 'posturl', posturl
        reqLoad = self.s.get(LoadGameScriptUrl)
        # print reqLoad.content

    def _Post(self, t):
        p = {
            'sid': self.newsid,
            't': str(t),
            'userid': str(self.newnum)
        }
        rtnreq = self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p)
        return rtnreq

    def Info_Action(self):
        req = self._Post(5002)
        print req.content
        infolist = json.loads(req.content)
        self.bzd = infolist['data']['bzd']
        self.boxcount = infolist['data']['boxcount']

    def Food_Action(self):

        req7 = self._Post(7001)
        # print req7.content
        foodlist = json.loads(req7.content)
        foodnumlist = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for index, foodkv in enumerate(foodlist['data']):
            foodnumlist[index] = int(foodkv['count'])
        # print foodnumlist
        foodid = 0
        for index, num in enumerate(foodnumlist):
            if num > 0 and index != 5 and index != 11:
                foodid = index + 1
                break
        # print foodid
        p = {
            'foodid': str(foodid),
            'sid': self.newsid,
            't': '7002',
            'userid': str(self.newnum)
        }
        if self.bzd < 10000:
            self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p)

    def Box_Action(self):
        if self.boxcount > 0:
            self._Post(5007)
            self._Post(8004)

    def Arena_Action(self):
        req = self._Post(6001)
        datalist = json.loads(req.content)
        # print datalist
        areacount = int(datalist['data']['arenacount'])
        datalist = datalist['data']['list']

        idlist = []
        iswinlist = []
        for data in datalist:
            iswinlist.append(data['iswin'])
            idlist.append(data['id'])
            # print data['id'], data['iswin']

        for index, id in enumerate(idlist):
            if areacount < 10 and iswinlist[index] != 1:
                # print id
                p = {
                    'id': id,
                    'sid': self.newsid,
                    't': '6007',
                    'userid': str(self.newnum)
                }
                req1 = self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p)
                print req1.content
                temp = json.loads(req1.content)
                print temp['data']['iswin']
                if temp['data']['iswin'] == 'true':
                    iswinlist[index] = 1
                areacount = areacount + 1
                time.sleep(2)

        p1 = {
            'type': 1,
            'sid': self.newsid,
            't': '6006',
            'userid': str(self.newnum)}
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['type'] = 4
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['type'] = 9
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)

    def Factory_Action(self):
        req = self._Post(2016)
        temp = json.loads(req.content)
        datalist = temp['data']
        for data in datalist:
            if data['time'] == 0:
                p = {
                    'id': data['sid'],
                    'sid': self.newsid,
                    't': '2017',
                    'userid': str(self.newnum)
                }
                self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p)
        if len(datalist) < 1:
            p = {
                'id': 2492,
                'sid': self.newsid,
                't': '2018',
                'userid': str(self.newnum)}
            self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p)

    def setvalue(self, np, x, y, value, length):
        if value > 30000:
            if np[x + 1][y] < 10000:
                np[x + 1][y] += value / 4
            if np[x - 1][y] < 10000:
                np[x - 1][y] += value / 4
            if np[x][y + 1] < 10000:
                np[x][y + 1] += value / 4
            if np[x][y - 1] < 10000:
                np[x][y - 1] += value / 4
            return
        np[x][y] += value
        if length > 0:
            np[x + 1][y] += value / 4
            np[x - 1][y] += value / 4
            np[x][y + 1] += value / 4
            np[x][y - 1] += value / 4
        if length > 1:
            np[x + 2][y] += value / 8
            np[x - 2][y] += value / 8
            np[x][y + 2] += value / 8
            np[x][y - 2] += value / 8
            np[x + 1][y + 1] += value / 8
            np[x - 1][y - 1] += value / 8
            np[x - 1][y + 1] += value / 8
            np[x + 1][y - 1] += value / 8
        if length > 2:
            np[x + 3][y] += value / 12
            np[x - 3][y] += value / 12
            np[x][y + 3] += value / 12
            np[x][y - 3] += value / 12
            np[x + 2][y + 1] += value / 12
            np[x - 2][y + 1] += value / 12
            np[x + 2][y - 1] += value / 12
            np[x - 2][y - 1] += value / 12
            np[x + 1][y + 2] += value / 12
            np[x + 1][y - 2] += value / 12
            np[x - 1][y + 2] += value / 12
            np[x - 1][y - 2] += value / 12
        if length > 3:
            np[x + 4][y] += value / 16
            np[x - 4][y] += value / 16
            np[x][y + 4] += value / 16
            np[x][y - 4] += value / 16

            np[x + 3][y + 1] += value / 16
            np[x - 3][y + 1] += value / 16
            np[x + 3][y - 1] += value / 16
            np[x - 3][y - 1] += value / 16

            np[x + 2][y + 2] += value / 16
            np[x - 2][y + 2] += value / 16
            np[x + 2][y - 2] += value / 16
            np[x - 2][y - 2] += value / 16

            np[x + 1][y + 3] += value / 16
            np[x - 1][y + 3] += value / 16
            np[x + 1][y - 3] += value / 16
            np[x - 1][y - 3] += value / 16

    def deepvalue(self, i, j, deep):
        if j < deep:
            return j / 10
        if j < deep * 2:
            return (deep * 2 - j) / 10
        return 0

    def Mvalue(self):
        valuelist = []
        valuelist1 = [4000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        valuelist2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        value = np.zeros([2000, 500])
        valuelist = valuelist1
        # ruby 24
        ruby = 0
        # purple 25
        purplegem = 0
        # green 26
        greengem = 0
        # diamond 19 20
        diamond = 0

        kuang = 0

        # yello 27
        yellowgem = 0
        if self.szg < 10:
            ruby = 180
            purplegem = 150
            greengem = 150
            diamond = 200
            yellowgem = 150
            kuang = 0
        else:
            ruby = 0
            purplegem = 0
            greengem = 0
            yellowgem = 0
            diamond = 0
            kuang = 200

        deep = 260
        for i in range(0, 2000):
            for j in range(0, 500):
                if self.mine[i][j] == -1:
                    self.setvalue(value,  i,  j,  -100000,  0)
                if self.mine[i][j] == 0:
                    self.setvalue(value, i, j, 40000, 1)
                    self.setvalue(value, i, j, -400000, 0)
                if 0 < self.mine[i][j] < 4:
                    self.setvalue(value, i, j, self.deepvalue(i, j, deep), 0)
                if self.mine[i][j] == 4:
                    self.setvalue(value, i, j, -100000, 0)
                if self.mine[i][j] == 5:
                    self.setvalue(value, i, j, -100000, 0)
                if self.mine[i][j] == 28:
                    self.setvalue(value, i, j, 800, 5)
                if 5 < self.mine[i][j] < 19:
                    self.setvalue(value, i, j, kuang, 5)
                if self.szg < 10:
                    if self.mine[i][j] == 19:
                        self.setvalue(value, i, j, diamond / 2, 5)
                    if self.mine[i][j] == 20:
                        self.setvalue(value, i, j, diamond, 5)
                    if self.mine[i][j] == 24:
                        self.setvalue(value, i, j, ruby, 5)
                    if self.mine[i][j] == 25:
                        self.setvalue(value, i, j, purplegem, 5)
                    if self.mine[i][j] == 26:
                        self.setvalue(value, i, j, greengem, 5)
                    if self.mine[i][j] == 27:
                        self.setvalue(value, i, j, yellowgem, 5)

        # print 'update value'
        bx = -1
        by = -1
        bw = 0
        for i in range(0, 2000):
            for j in range(0, 500):
                if bw < value[i][j]:
                    bw = value[i][j]
                    bx = i
                    by = j

        print bx, by
        print 'mine', self.mine[bx][by]
        return bx, by

        # if self.mine[i][j] ==

    def Mine_(self):
        p1 = {
            'time': time.time(),
            'sid': self.newsid,
            't': '2005',
            'userid': str(self.newnum),
            'cmd': 'getNodeList'}
        req = self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        # print req.content
        temp = json.loads(req.content)
        px = temp['data']['px']
        py = temp['data']['py']
        datalist = temp['data']['list']
        self.mine = np.zeros([2000, 500])

        for i in range(0, 2000):
            for j in range(0, 500):
                self.mine[i][j] = -1

        for data in datalist:
            x = data['x'] + 1000
            y = data['y']
            type = data['type']
            self.mine[x][y] = type
        print self.mine[930][233]
        time.sleep(10)

    def Mine_Action(self):
        self.Mine_()
        p2 = {
            'time': time.time(),
            'sid': self.newsid,
            't': '2006',
            'userid': str(self.newnum),
            'cmd': 'getGatherList'}
        p = {
            'x': 0,
            'y': 0,
            'time': time.time(),
            'sid': self.newsid,
            't': '2004',
            'userid': str(self.newnum),
            'cmd': 'exploit',
        }
        pc = {
            'x': 0,
            'y': 0,
            'time': time.time(),
            'sid': self.newsid,
            't': '2007',
            'userid': str(self.newnum),
            'cmd': 'charge',
        }
        reqszg = self._Post(2003)
        # print 'reqszq', reqszg.content
        temp = json.loads(reqszg.content)
        self.szg = temp['data']['szg']
        while self.szg > 5:
            req2 = self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p2)
            print req2.content
            temp1 = json.loads(req2.content)
            print 'len', len(temp1['data'])
            if len(temp1['data']) > 0:
                #    print temp1['data']
                cx = temp1['data'][0]['x']
                print cx
                cy = temp1['data'][0]['y']
                print cy
                ctime = temp1['data'][0]['time']
                cntime = temp1['data'][0]['needtime']
                print ctime, cntime
                if ctime >= cntime:
                    pc['x'] = cx
                    pc['y'] = cy
                    reqcharge = self.s.post(
                        'http://game.178mxwk.90tank.com/service/main.ashx', data=pc)
                    self.mine[cx][cy] = 0
                    print 'charge ', cx, cy
                else:
                    if cntime - ctime < 60:
                        time.sleep(cntime - ctime)
                    else:
                        return
            else:
                print 'start find max value position'
                bx, by = self.Mvalue()
                print 'find', bx, by
                if self.mine[bx][by] > 0:
                    p['x'] = bx - 1000
                    p['y'] = by
                    reqexplot = self.s.post(
                        'http://game.178mxwk.90tank.com/service/main.ashx', data=p)
                    print 'explot', bx - 1000, by
                    print 'waiting 15'
                    time.sleep(15)
                    # print reqexplot.content
                    try:
                        temp1 = json.loads(reqexplot.content)
                        print 'addnewnodelist---start'
                        newnodelist = temp1['data']['nodeList']
                        for data in newnodelist:
                            x = data['x'] + 1000
                            y = data['y']
                            type = data['type']
                            self.mine[x][y] = type
                        print 'addnewnodelist---end'
                    except:
                        print 'addnewnodelist--failed'
                        self.Mine_()
                        print 'newnode', temp1
            print 'updata -szg'
            reqszg = self._Post(2003)
            # print reqszg.content
            temp = json.loads(reqszg.content)
            self.szg = temp['data']['szg']
            print 'szg is ', self.szg

        return

    def Quora(self, name):
        p = {
            'figure': '99000001',
            'username': name,
            'sid': self.newsid,
            'sex': '1',
            't': '1',
        }
        req = self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p)
        print req.content
        self.newnum = json.loads(req.content)['data']['userid']
        p1 = {
            'value1': '0',
            'value2': 'step1_autoGame',
            'sid': self.newsid,
            't': '1102',
            'userid': str(self.newnum)
        }
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step1_manyHeroes'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step1_end'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step2_start'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step2_animation'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step2_expGold'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step2_progressBar'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step2_event'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step2_eventClick'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step2_over'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p2 = {
            'type': '1',
            'isxz': '0',
            'sid': self.newsid,
            't': '5005',
            'userid': str(self.newnum)
        }
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p2)
        p1['value2'] = 'step2-1_setFight'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step2-1_atkSum'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)
        p1['value2'] = 'step2-1_over'
        self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p1)

    def loginreborn(self, email, password, nga):
        if os.path.exists(r'./data/' + str(email) + '.txt'):
            with open(r'./data/' + str(email) + '.txt') as f:
                cookies = pickle.load(f)
                self.s.cookies = cookies

        else:

            req = self.s.get('https://account.178.com/')
            req2 = self.s.get('https://account.178.com/q_vcode.php?_act=gen_reg')
            o = open('a.jpg', 'wb')

            o.write(req2.content)
            o.close()
            # txtcode = pytesser.image_file_to_string('a.jpg')
            # print txtcode
            vcode = raw_input('input code:')
            self.Formdata = {
                '_': '',
                '_act': 'login',
                'email': email,
                'print': 'login',
                'password': password,
                'to': 'http://i.178.com',
                'vcode': vcode
            }
            print self.Formdata
            req3 = self.s.post('https://account.178.com/q_account.php', data=self.Formdata)
            with open(r'./data/' + str(email) + '.txt', 'w') as f:
                pickle.dump(self.s.cookies, f)

        pp = {
            'id': nga,
            'nga': 'nga'
        }
        # print pp
        reqs = self.s.get('http://s1.xsqs.178.com/game.php', params=pp)
        # print reqs.content
        soup = BeautifulSoup(reqs.content)
        soup_body_div_div_iframe = soup.div.div.iframe
        new_url = soup_body_div_div_iframe['src']
        reqs1 = self.s.get(new_url)
        soup = BeautifulSoup(reqs1.content)
        souphead = soup.head
        # print souphead
        # print souphead
        scpritlist = souphead.find_all('script')
        LoadGameScriptSoup = scpritlist[2]
        LoadGameScriptUrl = 'http://game.178mxwk.90tank.com/' + LoadGameScriptSoup['src']
        # print 'LoadGameSriptUrl', LoadGameScriptUrl
        targets = scpritlist[-1].text
        # print targets
        patter = r"sid='(.*?)'"
        patternum = r"\d+"
        self.newsid = re.findall(patter, targets)[-1]
        try:
            self.newnum = re.findall(patternum, targets)[-1]
            print self.newnum
        except:
            print r"can't get newnum"
        # print 'newsid', self.newsid
        # print 'newnum', self.newnum
        posturl = 'http://game.178mxwk.90tank.com/' + soup.body.form['action']
        value = soup.body.input['value']
        # print 'posturl', posturl
        reqLoad = self.s.get(LoadGameScriptUrl)
        # print reqLoad.content

    def friend(self, name):
        p2 = {
            'name': name,
            'sid': self.newsid,
            't': '4009',
            'userid': str(self.newnum)
        }
        req = self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p2)
        print req.content

    def gift(self, id, gift):
        p2 = {
            'id': id,
            'sid': self.newsid,
            't': '4004',
            'userid': str(self.newnum),
            'gifttype': gift,
        }
        req1 = self.s.post('http://game.178mxwk.90tank.com/service/main.ashx', data=p2)
        return req1

    def getname(self):
        req = self._Post(1001)
        name = json.loads(req.content)['data']['username']
        return name

    def getfriendlist(self):
        print self._Post(4008)
        print self._Post(1002)
        req = self._Post(4003)
        list = json.loads(req.content)['data']['list']
        print list
        for l in list:
            id = l['id']
            if id != '4524':
                req1 = self.gift(id, 3)
                print req1.content

    def Util(self):

        self.login()
        while True:
            try:
                self.Info_Action()
                self.Food_Action()
                self.Box_Action()
                self.Arena_Action()
                self.Mine_Action()
                time.sleep(120)
            except Exception, e:
                # self.login()
                print traceback.format_exc()
                time.sleep(120)
                print time.time()

if __name__ == "__main__":
    xsqs = XSQST()
    xsqs.Util()
# xsqs.login()
# #
# for i in range(1,61):
#     nickname = '5jo7t9a'+str(i)
#     print i
#     try:
#         xsqs.loginreborn(nickname,'z36925','1')
#     except:
#         print i
#     try:
#         print xsqs.getname()
#         xsqs.Quora(nickname.upper())
#     except:
#         print i
#     xsqs.Info_Action()
#     xsqs.friend(u'AkashA')
#     xsqs.friend(u'ҹ�갲����')
# xsqs.friend(u'��ʻ�')
# xsqs.friend(u'Leodinas')
# xsqs.friend(u'����������')
# xsqs.friend(u'������������')
#     try:
#         xsqs.getfriendlist()
#     except:
#         print i
#     print i
#     time.sleep(15)
