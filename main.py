#coding:utf8
"""
Created on 2018年5月4日
@author: changl
"""

from check.checkItems import checkItems
from common.getReportContent import getReportContent

def run():

        #在命令行窗口执行时需要进行编码的设置，如下
        # while True:
        #     reportName = raw_input('请输入要验证指标的报表名称(备注：退出请输入exit)：'.decode('utf-8').encode('gbk'))
        #     if reportName and reportName!='exit':
        #          reportName=reportName.decode('gbk').encode('utf-8')
        #          checkIt=checkItems(reportName)
        #          checkIt.executeCheck()
        #     if  not reportName:
        #         print "请输入有效的报表名称!!!".decode('utf-8').encode('gbk')
        #
        #     if reportName=='exit':
        #         return

        getR = getReportContent()
        reportNames = getR.getAllReportNames()#获取数据库中所有的报表名称

        while True:

            reportName = raw_input('请输入要验证指标的报表名称(备注：退出请输入exit)：')

            if reportName and reportName != 'exit':

                if reportName in reportNames:
                    checkIt = checkItems(reportName)
                    checkIt.executeCheck()
                else:
                    print '指标名称不存在,请输入正确的报表名称！'
                    continue

            if not reportName:
                print "请输入有效的报表名称!!!"

            if reportName == 'exit':
                break

if __name__=="__main__":
    run()

