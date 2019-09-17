#coding:utf-8
'''
@Created on 2018年5月12日
@author:changl
'''

import xlsxwriter
import os


class getTestResult():

    def __init__(self,reportName):
        self.reportName=reportName.decode('utf8')


    def createXlsx(self):
        self.xlsxname = './result/{}.xlsx'.format(self.reportName.encode('utf8'))
        self.xlsxname = self.xlsxname.decode('utf8')
        self.workbook = xlsxwriter.Workbook(self.xlsxname)
        self.worksheet = self.workbook.add_worksheet()
        self.worksheet.set_column('A:A',50)
        self.worksheet.set_column('B:D', 30)
    #添加固定的表头
    def writeColName(self):
        self.worksheet.write(0, 0,"指标名称".decode('utf8'))
        self.worksheet.write(0, 1, "es指标值".decode('utf8'))
        self.worksheet.write(0, 2, "SQL指标值".decode('utf8'))
        self.worksheet.write(0, 3, "测试结果".decode('utf8'))
        self.worksheet.write(0, 4, "指标ID".decode('utf8'))


    def writeData(self,itemname,esvalue,sqlvalue,result,count,itemid):
            if isinstance(esvalue,str):
                esvalue=esvalue.decode('utf8')
            if isinstance(sqlvalue,str):
                sqlvalue=sqlvalue.decode('utf8')
            self.worksheet.write(count,0,itemname.decode('utf8'))
            self.worksheet.write(count,1,esvalue)
            self.worksheet.write(count,2,sqlvalue)
            self.worksheet.write(count,3,result)
            self.worksheet.write(count, 4, itemid)

    def closexlsx(self):
            self.workbook.close()

if __name__=="__main__":
    # getTR=getTestResult('中文名称')
    # getTR.createXlsx()
    # getTR.writeColName()
    # getTR.writeData("门诊患者就诊总人次","es","sql","pass",1)
    # getTR.closexlsx()
    pass
