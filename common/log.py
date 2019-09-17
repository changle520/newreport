#coding:utf8
import logging
import os,datetime


curdate=datetime.datetime.now().strftime("%Y-%m-%d")
path="../log/{}.txt".format(curdate)

def mylog(content):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=path,
                        filemode='a',
                        encode='utf-8')

    logging.debug(content)

def mylog_except(error):
    logging.exception(error)



