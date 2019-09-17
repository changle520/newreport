# coding:utf-8
from common.configReader import configReader
from common.connectDB import connectDB
from common.log import mylog, mylog_except
import os


path=os.path.abspath('./config/new_index.ini')

class getGroupSQLvalue():
    def __init__(self):
        # 连接报表数据库
        self.conndb = connectDB()
        self.conn = self.conndb.connect(self.conndb.dbname_report)
        self.cur = self.conndb.getCursor(self.conn)

        # 从配置文件中获取SQL配置项
        self.confR = configReader(path)
        self.optitems = self.confR.getitems('default_group')  # 常规SQL


    def getValueInGroup(self, itemname, zoneid,groupname, startT, endT):
        self.sql = self.confR.get("default_group", itemname)
        sqlValue = self.conndb.executeSQL_groupone(self.cur, self.sql, zoneid,groupname, startT, endT)
        return sqlValue


# 获取缺省医疗组维度指标对应的SQL值
    def getSqlValue_group(self, itemname, zoneid,groupname, startT, endT):

        try:

            if itemname in self.optitems:

                sqlValue = self.getValueInGroup(itemname, zoneid,groupname, startT, endT)
                return sqlValue


            else:
                logcontent = "该指标在指标库中不存在" + ',' + itemname
                mylog(logcontent)

        except Exception, error:
            mylog("执行过程中出错")
            mylog_except(error)





