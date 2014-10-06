#coding:utf-8

### 
#  生成每个号段的记录
###
import struct
import pymongo
import os


def getMongoDB():
    conn = pymongo.MongoClient()
    db = conn.phone
    return db

def getZipCodeOffest():
    db = getMongoDB()
    result = {}
    p = db.zip_code.find()
    for t in p:
        result[t['_id']] = t['offset']

    return result


def getCartType(phone):
    t3 = int(str(phone)[:3])
    if t3 in (133,153,180,181,189,177):
        return 3

    elif t3 in(130,131,132,155,156,145,185,186,176):
        return 2

    else:
        return 1

offsetDict = getZipCodeOffest()
db = getMongoDB()

def writePhoneRecordIntoFile(phone,zip_code,code):
    pfile = '%s.txt'%(int(phone)/10000,)
    zip_code = str(zip_code)
    print phone,zip_code,code
    #try:
    offset = offsetDict[str(zip_code)]
    #except:
    #    offset =  db.zip_code.find_one({"code":code})['offset']
    cartType = getCartType(phone)
    fmt = "<iiB"
    b = struct.pack(fmt,phone,offset,cartType)
    with open(pfile,'ab') as f:
        f.write(b)

def startWritePhoneRecord(start):
    mini = start * 10000
    maxi = mini + 9999
    if os.path.exists('%s.txt'%start):
        os.remove("%s.txt"%start)
    p = db.phone_record.find({"_id":{"$gte":mini,"$lte":maxi},"zip_code":{"$gt":''}})
    print p.count()
    for t in p:
        writePhoneRecordIntoFile(t["_id"],t["zip_code"],t["code"])


p13 = [130+i for i in range(0,10)]
p14 = [145,147]
p15 = [150+i for i in range(0,10)]
p18 = [180+i for i in range(0,10)]

allPhones = p13 + p14 + p15 + p18

def main():
    for i in allPhones:
        startWritePhoneRecord(i)

if __name__ == '__main__':
    main()
