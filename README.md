### 1. export data to mongo

mongoexport -d phone -c phone_record  < phone_record.json

mongoexport -d phone -c zip_code < zip_code.json

### 2. run the following script 

python zip_code_record.py

python phone_record.py

python build_up.py


finally, you will get a ‘phone.dat’ file and some temporary file ends with ‘.txt’ which you can romve.



