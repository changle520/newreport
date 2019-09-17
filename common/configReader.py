#coding:utf8
"""
Created on 2018年5月4日
@author: changl
"""

# from ConfigParser import ConfigParser
from ConfigParser import SafeConfigParser,RawConfigParser
from common.log import mylog,mylog_except


class configReader():
    def __init__(self,path):
        self.path=path
        try:
            # self.conf=ConfigParser()
            self.conf=SafeConfigParser()
            self.conf.read(self.path)
        except Exception,error:
            # print "初始化发生了错误",error
            mylog("初始化发生了错误")
            mylog_except(error)

    def get(self,field,key):

        try:
            return self.conf.get(field,key)

        except Exception,error:
            logcontent= "读取配置项发生了错误"+","+field+","+key
            mylog(logcontent)
            mylog_except(error)


    def getint(self,field,key):
        try:
            return self.conf.getint(field,key)
        except Exception,error:
            logcontent= "读取配置项发生了错误"+","+field+","+key
            mylog(logcontent)
            mylog_except(error)

    def geti(self,field):
        return self.conf.items(field)

    def getitems(self,field):
        try:
            defaultvalue=self.conf.items('zone')
            defaultKey=[key for key,value in defaultvalue]
            result=self.conf.items(field)
            hospitalItemnames=[]
            for key,value in result:
                if key not in defaultKey or key.startswith('i'):
                    hospitalItemnames.append(key.upper())
                else:
                    hospitalItemnames.append(key)
            return hospitalItemnames

        except Exception,error:
            # print "读取配置项发生了错误",field
            logcontent = "读取配置项发生了错误" + "," + field
            mylog(logcontent)
            mylog_except(error)


#
# if __name__=="__main__":
#     confR=configReader("../config/new_index.ini")
#
#     result=confR.get('mysql','host')
#     result2 = confR.geti('zone')
#     print result,result2
