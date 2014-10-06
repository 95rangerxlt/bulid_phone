#coding:utf-8
import struct
import pymongo
import os


zip_code_record_file = "zip_code_record.txt"

def writeZipCodeIntoFile(result):
    with open(zip_code_record_file,'ab') as f:
        print result
        content="%s|%s|%s|%s\0"%(
                result['province'],
                result['city'],
                result['code'],
                result['zip_code'],
                )
        content = content.encode("utf-8")
        offset = f.tell()
        f.write(content)
        return offset


def startGenZipCodeFile():
    if os.path.exists(zip_code_record_file):
        os.remove(zip_code_record_file)
    conn = pymongo.MongoClient()
    db = conn.phone
    p = db.zip_code.find().sort("_id",1)
    for t in p:
        offset = writeZipCodeIntoFile(t)
        db.zip_code.update({"_id":t['_id']},{'$set':{"offset":offset}})


if __name__ == "__main__":
    startGenZipCodeFile()
