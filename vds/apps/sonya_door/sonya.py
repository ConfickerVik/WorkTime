from vds.MySQLdb import MySQLDBConnect
from django.conf import settings
import struct
from datetime import datetime, timedelta
import os
import glob
from subprocess import Popen, PIPE
from collections import OrderedDict
from operator import itemgetter
import datetime as datetime2


class BSM:

    def parseBSM(self, year, month):
        log = OrderedDict()
        os.chdir(settings.STATICFILES_DIRS[0])
        for file in glob.glob(f"{year}.{month}.*.bsm"):
            with open(file, 'rb') as f:
                while True:
                    data = f.read(27)
                    if not data: break

                    s = struct.unpack('<icccHHHHHHHHi', data)

                    if s[0] == 6481:
                        point = 'in'
                    elif s[0] == 6480:
                        point = 'out'
                    if str(s[-1]) in log.keys():
                        date = datetime(s[4], s[5], s[7])
                        time = timedelta(hours=s[8], minutes=s[9], seconds=s[10])
                        log[str(s[-1])]['visit'].append({'point': point, 'date': date, 'time': time})
                    else:
                        log[str(s[-1])] = {}
                        log[str(s[-1])]['visit'] = []
                        date = datetime(s[4], s[5], s[7])
                        time = timedelta(hours=s[8], minutes=s[9], seconds=s[10])
                        log[str(s[-1])]['visit'].append({'point': point, 'date': date, 'time': time})
        return log


class Serialize:

    def getUsersId(self):
        users = {}
        res = Popen(
            '''/bin/echo 'select lastname,name,id from sotrudniki' | /usr/bin/mdb-sql %s ''' % settings.MS_ACCESS_DIR,
            shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
        for l in res.decode('utf-8').split('\n'):
            if l.startswith('+'): continue
            l = [s.strip() for s in l.split('|') if s.strip()]
            if len(l) != 3 or 'lastname' in l: continue
            users[str(l[2])] = (l[0], l[1])
        return users

    def rename(self, logs, access):
        for key_log in logs.keys():
            for key_access in access.keys():
                if int(key_log) == int(key_access):
                    logs[key_log]['FIO'] = ' '.join([access[key_access][0], access[key_access][1]])
                    logs[key_log]['id'] = key_access
        return logs

    def statistic(self, history):
        total = {}
        systime = datetime.now()
        datenow = datetime2.date(systime.year, systime.month, systime.day) 
        timenow = timedelta(hours=systime.hour, minutes=systime.minute, seconds=systime.second)
        for key in history.keys():
            try:
                if key == '0':
                    pass
                else:
                    otrab = timedelta(0)
                    visit = history[key]['visit']
                    date = visit[0]['date']
                    timein = timedelta(0)
                    timeout = timedelta(0)
                    deltasmoke = timedelta(0)
                    smoketime = timedelta(0)
                    countsmoke = 0
                    total[key] = {}
                    total[key]['days'] = []
                    firstaction = visit[0]['time']
                    lastaction = timedelta(hours=23, minutes=59, seconds=59)
                    for elem in range(len(visit)):
                        if len(visit) <= 1:
                            pass
                        if date == visit[elem]['date']:
                            if elem == 0 and visit[elem]['point'] == 'out':
                                timeout = visit[elem]['time']
                                timein = timedelta(0)
                                deltatime = timeout - timein
                                firstaction = timein
                                otrab += deltatime
                            if elem == 0 and visit[elem]['point'] == 'in':
                                timein = visit[elem]['time']
                                firstaction = visit[elem]['time']
                            if elem > 0 and visit[elem]['point'] == 'out':
                                timeout = visit[elem]['time']
                                deltatime = timeout - timein
                                otrab += deltatime
                            if elem > 0 and visit[elem]['point'] == 'in':
                                timein = visit[elem]['time']
                                deltasmoke = timein - timeout
                                if deltasmoke <= timedelta(minutes=5):
                                    otrab += deltasmoke
                                    smoketime += deltasmoke
                                    countsmoke += 1
                            if elem == len(visit) - 1:
                                if visit[elem]['point'] == 'out':
                                    lastaction = visit[elem]['time']
                                    total[key]['days'].append({'date':visit[elem]['date'].date(), 'smoketime': smoketime, 'countsmoke':countsmoke,
                                    'rabotal': otrab, 'firstaction':firstaction, 'lastaction':timeout})
                                if visit[elem]['point'] == 'in':
                                    if datenow == visit[elem]['date'].date() and timenow > visit[elem]['time']:
                                        total[key]['days'].append({'date':visit[elem]['date'].date(), 'smoketime': smoketime, 'countsmoke':countsmoke,
                                        'rabotal': otrab, 'firstaction':firstaction, 'lastaction':lastaction})
                                        total[key]['color'] = '#93c195'
                                    else:
                                        lastaction = timedelta(hours=23, minutes=59, seconds=59)
                                        timein = visit[elem]['time']
                                        timeout = timedelta(hours=23, minutes=59, seconds=59)
                                        deltatime = timeout - timein
                                        otrab += deltatime
                                        total[key]['days'].append({'date':visit[elem]['date'].date(), 'smoketime': smoketime, 'countsmoke':countsmoke,
                                        'rabotal': otrab, 'firstaction':firstaction, 'lastaction':timeout})
                        elif date != visit[elem]['date']:
                            date = visit[elem]['date']
                            if visit[elem - 1]['point'] == 'out':
                                lastaction = visit[elem]['time']
                                total[key]['days'].append({'date':visit[elem]['date'].date(), 'smoketime': smoketime, 'countsmoke':countsmoke,
                                    'rabotal': otrab, 'firstaction':firstaction, 'lastaction':lastaction})
                                otrab = timedelta(0)
                                firstaction = timedelta(0)
                                smoketime = timedelta(0)
                                countsmoke = 0
                                timein = timedelta(0)
                                timeout = timedelta(0)
                                deltasmoke = timedelta(0)
                            if visit[elem - 1]['point'] == 'in':
                                lastaction = timedelta(hours=23, minutes=59, seconds=59)
                                timein = visit[elem - 1]['time']
                                timeout = timedelta(hours=23, minutes=59, seconds=59)
                                deltatime = timeout - timein
                                otrab += deltatime
                                total[key]['days'].append({'date':visit[elem - 1]['date'].date(), 'smoketime': smoketime, 'countsmoke':countsmoke,
                                    'rabotal': otrab, 'firstaction':firstaction, 'lastaction':lastaction})
                                otrab = timedelta(0)
                                firstaction = timedelta(0)
                                smoketime = timedelta(0)
                                countsmoke = 0
                                timein = timedelta(0)
                                timeout = timedelta(0)
                                deltasmoke = timedelta(0)
                            if visit[elem]['point'] == 'out':
                                timeout = visit[elem]['time']
                                timein = timedelta(0)
                                deltatime = timeout - timein
                                otrab += deltatime
                            if visit[elem]['point'] == 'in':
                                firstaction = visit[elem]['time']
                                timein = visit[elem]['time']
                    total[key]['otrab'] = otrab
            except Exception as e:
                print(e)
                pass
        return total

    def timedelta2(self, param):
        hours, minutes, seconds = param.split(":")
        time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return time

    def reformatetime(self, changeTime):
        if changeTime.days > 1:
            days, time = str(changeTime).split("days,")
            dayHours = int(days) * 24
            hours, minute, second = time.split(":")
            resultHours = dayHours + int(hours)
        elif changeTime.days == 1:
            days, time = str(changeTime).split("day,")
            dayHours = int(days) * 24
            hours, minute, second = time.split(":")
            resultHours = dayHours + int(hours)
        else:
            resultHours, minute, second = str(changeTime).split(":")
        return "%s:%s:%s" % (resultHours, minute, second)

    def restructuring(self, date):
        year, month = date.split("-")
        obj1 = BSM()
        log = obj1.parseBSM(year, month)

        MS_ACCESS = self.getUsersId()
        history = self.rename(log, MS_ACCESS)

        mysql = MySQLDBConnect()
        cursorMySQL = mysql.connect()
        queryMySQL = "SELECT u.id,u.otpusk,u.bolezn,u.poezdka,u.deni,u.workdays,u.other,u.work_time_start,u.work_time_end,hr.hr FROM users u left join hr on hr.id = u.id WHERE month(u.time) = %s and year(u.time) = %s" % (
        month, year)
        resQueryMySQL = mysql.query(cursorMySQL, queryMySQL)

        for res in resQueryMySQL:
            if str(res['id']) in history.keys():
                history[str(res['id'])]['info'] = {'otpusk': res['otpusk'], 'bolezn': res['bolezn'],
                                                   'poezdka': res['poezdka'], 'deni': res['deni'],
                                                   'workdays': res['workdays'], 'other': res['other'],
                                                   'work_time_start': res['work_time_start'],
                                                   'work_time_end': res['work_time_end'],
                                                   'hr': res['hr']}

        stat = self.statistic(history)

        for key in stat.keys():
            otrabotano = timedelta(0)
            neobxodimo = timedelta(0)
            nedorabotka = timedelta(0)
            deni = timedelta(0)
            if 'FIO' in history[key].keys() and 'id' in history[key].keys():
                stat[key]['FIO'] = history[key]['FIO']
                stat[key]['id'] = int(history[key]['id'])
                stat[key]['info'] = {}
                if 'info' in history[key].keys():
                    info = history[key]['info']
                    stat[key]['info'].update(info)
                    for time in stat[key]['days']:
                        otrabotano += time['rabotal']
                    if info['deni'] == 8.0:
                        deni = timedelta(hours=8)
                    elif info['deni'] == 8.5:
                        deni = timedelta(hours=8, minutes=30)
                    elif info['deni'] == 12:
                        deni = timedelta(hours=12)
                    neobxodimo = (info['workdays'] - (info['otpusk'] + info['bolezn'] + info['poezdka'])) * deni + timedelta(hours=float(info['other']))
                    nedorabotka = neobxodimo - otrabotano
                    stat[key]['neobxodimo'] = self.reformatetime(neobxodimo)
                    stat[key]['otrabotano'] = self.reformatetime(otrabotano)
                    if neobxodimo < otrabotano:
                        stat[key]['nedorabotka'] = "-" + str(self.reformatetime(abs(nedorabotka)))
                    else:
                        stat[key]['nedorabotka'] = str(self.reformatetime(abs(nedorabotka)))
        statnormal = {}
        
        for key in stat.keys():
            if stat[key]['days'] is [] or ('FIO' not in history[key].keys() and 'id' not in history[key].keys()):
                pass
            else:
                stat[key]['visit'] = stat[key]['days'].sort(key=itemgetter('date'))
                statnormal[key] = stat[key]

        return OrderedDict(sorted(statnormal.items(), key=lambda key_value: key_value[1]['FIO']))
