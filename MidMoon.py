from webbot import *
import time

while True:
    hour,mins,second = time.strftime('%H:%M:%S', time.localtime(time.time())).split(":")
    print hour,mins,second
    if hour in ("09","15","19","21","10","16","20","22"):
        if mins in ("59","00","01","13"):
            if True or second in ("57","58","59","60","00","01","02","03","04","05"):
                print hour,mins,second

                X =XSQST()
                X.login()
                print hour,mins,second
                continue
    time.sleep(1)
