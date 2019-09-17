#coding:utf8
"""
Created on 2018年5月4日
@author: changl
"""
import os,xlrd
import MySQLdb
from common.configReader import configReader
from common.log import mylog,mylog_except

path=os.path.abspath('../config/new_index.ini')

class connectDB():
    def __init__(self):

        self.dbconf=configReader(path)
        self.host=self.dbconf.get("mysql","host")
        self.port = self.dbconf.getint("mysql", "port")
        self.username=self.dbconf.get("mysql","username")
        self.passwd=self.dbconf.get("mysql","passwd")
        self.dbname_dp=self.dbconf.get('mysql',"dbname_dp")
        self.dbname_sys=self.dbconf.get("mysql","dbname_sys")
        self.dbname_report=self.dbconf.get("mysql","dbname_report")
        self.charset=self.dbconf.get("mysql","charset")

    def connect(self,dbname):
        try:
            return MySQLdb.Connect(host=self.host,port=self.port,user=self.username,passwd=self.passwd,db=dbname,charset=self.charset)
        except Exception,error:
            mylog("数据库连接出错")
            mylog_except(error)


    def getCursor(self,conn):
        if conn is not None:
            return conn.cursor()

    def closeConn(self,conn):
        if conn is not None:
            conn.close()

    def closeCur(self,cur):
        if cur is not None:
            cur.closeCur()


#执行的SQL语句传入的值是机构，开始时间，结束时间
    def executeSQL_zoneid_one(self,cur,sql,zoneid,startT,endT):
            cur.execute(sql, (zoneid, startT, endT))
            return cur.fetchone()[0]

#执行的SQL语句传入的值是机构，开始时间，结束时间，机构，开始时间，结束时间（用于统计全院的指标数据）
    def executeSQL_zoneid_two(self,cur,sql,zoneid,startT,endT):
            cur.execute(sql,(zoneid, startT, endT,zoneid, startT, endT))
            return cur.fetchone()[0]

# 执行的SQL语句传入的值是机构，开始时间，结束时间，配置项的值
    def executeSQL_zoneid_three(self, cur, sql, zoneid, startT, endT,configValue):
        try:
            cur.execute(sql, (zoneid, startT, endT,configValue))
            self.rlt=cur.fetchone()[0]
        except Exception,error:
            print error
            self.rlt='no data'
        return self.rlt

# 药品维度下获取标准产品属性的SQL执行，传入的是一个标准产品的id
    def executeSQL_drug_productinfor(self, cur, sql, productid):
        try:
            cur.execute(sql,(productid,))
            self.rlt=cur.fetchone()[0]
        except Exception,error:
            print error
            self.rlt='no data'
        return self.rlt

# 执行的SQL语句传入的值是机构，科室，开始时间，结束时间
    def executeSQL_deptid_one(self,cur,sql,zoneid,deptid,startT,endT):
        cur.execute(sql, (zoneid,deptid,startT,endT))
        return cur.fetchone()[0]

# 执行的SQL语句传入的值是机构，科室，开始时间，结束时间，机构，科室，开始时间，结束时间
    def executeSQL_deptid_two(self, cur, sql, zoneid,deptid,startT, endT):
            cur.execute(sql, (zoneid, deptid,startT, endT, zoneid, deptid,startT, endT))
            return cur.fetchone()[0]

# 执行的SQL语句传入的值是机构，科室，开始时间，结束时间，配置项的值
    def executeSQL_deptid_three(self, cur, sql, zoneid,deptid, startT, endT, configValue):
        try:
            cur.execute(sql, (zoneid,deptid, startT, endT, configValue))
            self.rlt = cur.fetchone()[0]
        except Exception, error:
            print error
            self.rlt = 'no data'
        return self.rlt

# 执行的SQL语句传入的值是机构，医生，开始时间，结束时间，配置项的值
    def executeSQL_docid_three(self, cur, sql, zoneid, docid, startT, endT, configValue):
            try:
                cur.execute(sql, (zoneid, docid, startT, endT, configValue))
                self.rlt = cur.fetchone()[0]
            except Exception, error:
                print error
                self.rlt = 'no data'
            return self.rlt

# 执行的SQL语句传入的值是机构，医生，开始时间，结束时间
    def executeSQL_docid_one(self,cur,sql,zoneid,docid,startT,endT):
        cur.execute(sql, (zoneid,docid,startT,endT))
        return cur.fetchone()[0]

# 执行的SQL语句传入的值是机构，医生，开始时间，结束时间，机构，医生，开始时间，结束时间
    def executeSQL_docid_two(self,cur,sql,zoneid,docid,startT,endT):
        cur.execute(sql, (zoneid,docid,startT,endT,zoneid,docid,startT,endT))
        return cur.fetchone()[0]

# 执行的SQL语句传入的值是机构，医疗组，开始时间，结束时间
    def executeSQL_groupone(self,cur,sql,zoneid,groupname,startT,endT):
        cur.execute(sql, (zoneid,groupname,startT,endT))
        return cur.fetchone()[0]

# 执行的SQL语句传入的值是机构，医疗组，开始时间，结束时间，机构，医疗组，开始时间，结束时间
    def executeSQL_group_two(self,cur,sql,zoneid,groupname,startT,endT):
        cur.execute(sql, (zoneid,groupname,startT,endT,zoneid,groupname,startT,endT))
        return cur.fetchone()[0]

#执行的SQL语句传入的值是机构，开始时间，结束时间，产品，机构，开始时间，结束时间，产品
    def executeSQL_drug(self,cur,sql,zoneid,startT,endT,productId):
        cur.execute(sql,(zoneid,startT,endT,productId,zoneid,startT,endT,productId))
        return cur.fetchone()[0]

#测试指标用，临时的
    def getrecipeids(self):
        worksheet = xlrd.open_workbook('C:\\Users\\ipharmacare\\recipeid.xlsx')
        sheet1 = worksheet.sheet_by_name('Sheet1')
        cols = sheet1.col_values(46)
        return cols

if __name__=="__main__":
    connectDB=connectDB()
    conn=connectDB.connect(connectDB.dbname_report)
    cur=connectDB.getCursor(conn)
    confr=configReader(path)
    sql=confr.get('zone',"出院患者中联合使用抗菌药物人次")
    print sql

    # cur.execute(sql,('4','2014-08-01','2014-08-01','4','2014-08-01','2014-08-01'))
    cur.execute(sql, ('4', '2014-08-01', '2014-08-01'))
    rlt =cur.fetchall()[0]
    print(rlt)
    # ids=[str(rid[0]) for rid in rlt]
    # print(ids)

    # recipeids = connectDB.getrecipeids()
    # print(recipeids)
    # recipeids_new = [int(recipeid) for recipeid in recipeids]

    # print(set(ids)-set(recipeids_new))
    #
    #
    # f1=open("C:\\Users\\ipharmacare\\baseid.txt",'r')
    # baseids=[line.strip() for line in f1.readlines()]
    # print(baseids)
    # print(set(baseids)-set(ids))












