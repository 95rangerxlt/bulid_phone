#coding:utf-8

import os
from phone_record import allPhones
import struct

zip_code_file = "zip_code_record.txt"

sorted(allPhones)

headFmt=("<4si")

version = "0.01"


with open("phone.dat",'wb') as f:

    with open(zip_code_file,'rb') as z:
        zip_content = z.read()
        offeset = z.tell()

    head = struct.pack(headFmt,version, offeset + struct.calcsize(headFmt))

    f.write(head)
    f.write(zip_content)

    for phone in allPhones:
        phone_file = '%s.txt'%phone
        with open(phone_file,'rb') as p:
            phone_content = p.read()
            f.write(phone_content)



