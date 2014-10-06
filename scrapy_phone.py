#coding:utf-8

###
### 爬取电话号码记录
###

import sys

# if 'threading' in sys.modules:
#     del sys.modules['threading']

import gevent
import gevent.monkey
import urllib2
import pymongo
import json
import datetime
from BeautifulSoup import BeautifulSoup
import time

from gevent.queue import Queue

gevent.monkey.patch_all(thread=False)

def boss(start):
    if start == 1340000:
        end = start + 9000
    else:
        end = start + 10000
    for i in xrange(start,end):
        tasks.put_nowait(i)
    #t = db.phone_record.find({"province":{"$exists":False}})
    #for p in t:
    #    tasks.put_nowait(p['_id'])



def getPhoneInfoUrlFromShowji(phone,ingnore=True,debug=True):
    #就这么用，7是超时时间，后面的False表示不抛出其他异常了！
    url = "http://api.showji.com/Locating/www.showji.c.o.m.aspx?m=%s&output=json"
    if debug:
        print phone
    with gevent.Timeout(5, False) as timeout:
        request_url = url%phone
        try:
            res = urllib2.urlopen(request_url)
            result = json.loads(res.read())
            if not result["Province"]:
                result = {}
                result["_id"] = int(phone)
                result["status"] = "not_found"
            else:
                result["_id"] = int(phone)
                result["status"] = "ok"
                result = formatShowjiDataInfo(result)
            #result["update_time"] = str(datetime.datetime.now())
            print result
            print result['province'],result['city']
        except Exception as e:
            import traceback
            print traceback.format_exc()
            time.sleep(5)
            result = {"_id":int(phone)}
            result["status"] = "get_error"

    return result
            

def getPhoneInfoUrlFromIP138(phone,ingnore=True,debug=True):
    request_url = "http://www.ip138.com:8080/search.asp?mobile=%s&action=mobile"%phone
    if debug:
        print phone
    with gevent.Timeout(5, False) as timeout:
        try:
            result = {}
            result["_id"] = int(phone)
            result["status"] = "ok"
            html = urllib2.urlopen(request_url).read()
            html = html.decode("gb2312")
            bt = BeautifulSoup(html)
            tds = bt.findAll("td",{"class":"tdc2"})[1:]
            # print tds
            if tds[0].text.startswith("<td>"):
                PC = tds[0].text[9:].split("&nbsp;")
            else:
                PC = tds[0].text.split("&nbsp;")
            if PC[0] == u"未知":
                print "not found"
                result["status"] = "not_found"
            else:
                result['province'] = PC[0]
                result['city'] = PC[1] if len(PC) >=2 else result['province']
                result['code'] = tds[2].text
                result['zip_code'] = tds[3].text[:6]
                if debug:
                    print result
                    print result['province'],result['city']
        except Exception as e:
            import traceback
            print traceback.format_exc()
            result["status"] = "get_error"
            if debug:
                print result
    return result


def analysisIP138Html(phone):
    request_url = "http://www.ip138.com:8080/search.asp?mobile=%s&action=mobile"%phone
    html = urllib2.urlopen(request_url).read()
    html = html.decode("gb2312")
    bt = BeautifulSoup(html)
    tds = bt.findAll("td",{"class":"tdc2"})[1:]
    return bt,tds

def saveResultFromIP138(result,fmt=False):
    status = result.pop('status')
    if 'province' not in result:
        tasks.put_nowait(result['_id'])

    if status == "ok":
        if fmt:
            phone = result.pop("_id")
            zip_code = result["zip_code"]
            result["phone"] = phone
            result["_id"] = zip_code
            db.zip_code.save(result)
        else:
            db.phone_record.save(result)
    elif status == "not_found":
        db.phone_not_found.save(result)
    elif status == "get_error":
        tasks.put_nowait(result['_id'])

def formatShowjiDataInfo(result):
    formatResult = {}
    formatResult['province'] = result["Province"]
    formatResult['status'] = result["status"]
    formatResult['city'] = result["City"]
    formatResult['code'] = result["AreaCode"]
    formatResult['zip_code'] = result["PostCode"]
    formatResult['_id'] = result["_id"]
    return formatResult

def saveResultFromShowji(result):
    status = result.pop('status')
    if status == "ok":
        #db.phone_record.save(result)
        phone = result.pop('_id')
        result["phone"] = phone
        _id = result["zip_code"]
        db.phone_zip_code.update({"_id":_id},{"$set":{"value":result}},upsert=True)
    elif status == "not_found":
        db.phone_not_found.save(result)
    elif status == "get_error":
        tasks.put_nowait(result["_id"])

def getDataFromIP138AndSaveInMongoDB(phone,fmt=False):
    result = getPhoneInfoUrlFromIP138(phone)
    saveResultFromIP138(result,fmt)

def getDataFromShowjiAndSaveInMongDB(phone):
    result = getPhoneInfoUrlFromShowji(phone)
    saveResultFromShowji(result)

def worker():

    import time
    phones = []
    while not tasks.empty():
        phone = tasks.get()
        phones.append(phone)
        if len(phones) <= 10:
            continue
        else:
           gevent.joinall([ gevent.spawn(getDataFromIP138AndSaveInMongoDB,phone) for phone in phones])
           time.sleep(0.5)
           phones = []

    if phones:
        gevent.joinall([ gevent.spawn(getDataFromIP138AndSaveInMongoDB,phone) for phone in phones])

    print('Quitting time!')



def createMongDB():
    conn = pymongo.MongoClient(
        host='127.0.0.1', port=27017)
    global db
    db = conn.phone

def createTask():
    global tasks
    tasks = Queue()


def startCrawlerPhone(start):
    createMongDB()
    createTask()
    gevent.spawn(boss,start).join()
    worker()


def startFormatPhoneInfo():
    createMongDB()
    createTask()
    t  = db.phone_zip_code.find().sort('_id',1)
    for p in t:
        phone = p["value"]["phone"]
        tasks.put_nowait(phone)

    phones = []
    while not tasks.empty():
        phone = tasks.get()
        phones.append(phone)
        if len(phones) <= 10:
            continue
        else:
           gevent.joinall([ gevent.spawn(getDataFromIP138AndSaveInMongoDB,phone,True) for phone in phones])
           time.sleep(0.5)
           phones = []

    if phones:
           gevent.joinall([ gevent.spawn(getDataFromIP138AndSaveInMongoDB,phone,True) for phone in phones])


def testGetPhoneInfo(phone):
    gevent.spawn(getPhoneInfoUrlFromIP138,phone).join()
    gevent.spawn(getPhoneInfoUrlFromShowji,phone).join()

if __name__ == '__main__':
    #校验
    startFormatPhoneInfo()
