#coding:utf8
"""
Created on 2018年5月4日
@author: changl
"""

from common.configReader import configReader
from common.getReportContent import getReportContent
from common.saveTestResult import getTestResult
from GetSQLvalue.itemZoneValue import getZoneSQLvalue
from GetSQLvalue.itemDocValue import getDocSQLvalue
from GetSQLvalue.itemDeptValue import getDeptSQLvalue
from GetSQLvalue.itemGroupValue import getGroupSQLvalue
import json,os

path=os.path.abspath('./config/new_index.ini')
class checkItems():

    def __init__(self,reportName=None):
        self.reportName=reportName
        self.getRC=getReportContent()
        self.getReportConfig(self.reportName)

        # 从配置文件中获取SQL配置项
        self.confR = configReader(path)

        #保存测试结果
        self.saveTR=getTestResult(self.reportName)

        # 获取SQL值的类
        self.getSqlValueZone = getZoneSQLvalue()  #数据维度：机构
        self.getSqlValueDoc=getDocSQLvalue()      #数据维度：医生
        self.getSqlValueDept=getDeptSQLvalue()    #数据维度：科室
        self.getSqlValueGroup=getGroupSQLvalue()  #数据维度：医疗组

        self.dimension={'缺省维度':'default','药品维度':'drug','手术维度':'operation','警示维度':'warning'} #各维度对应的方法名

#判断指标的SQL值与ES值是否相等
    def isEqual(self,esvalue,sqlvalue):
        if esvalue == sqlvalue:
           return "pass"
        else:
            return "fail"

#获取报表的相关内容
    def getReportConfig(self,reportName):

           #得到报表名称对应的ID
            self.reportID = self.getRC.getReportID(reportName)[0]
           #得到报表ID对应的recordid(最近一条的)
            self.recordid=self.getRC.getRecordId(self.reportID)[-1][0]
           #得到指标值（es统计出来的值）存储的表名
            self.reportDataName = self.getRC.getReportDataName(self.recordid)
           #得到报表中所有的指标ID
            self.items = self.getRC.getReportItem(self.reportID)
            self.items_new = [str(ele[0]) for ele in self.items]
           #得到数据库中所有的指标ID,指标名称（用字典类型存储）
            self.allitems = self.getRC.getAllItems()
           #得到报表中所有已生成的指标值
            self.values = self.getRC.getESvalue(self.reportDataName)
            self.columnname=self.getRC.getItemsID(self.reportDataName)
            self.esvalues=dict(zip(self.columnname,self.values))

            #得到zoneid
            self.zoneid=self.getRC.getzoneId(self.esvalues['zoneId'])
           #获取报表中的时间范围
            self.reportTime=self.getRC.getReportTime(self.recordid)
           #获取报表的数据维度
            self.dataDimensionName=self.getRC.getDataDimensionName(reportName)
           # 获取报表的统计维度维度
            self.bussinessDimensionName=self.getRC.getBusinessDimensionName(reportName)

#计算指标SQL值时，缺省维度执行此方法
    def default(self,itemname):
        if self.dataDimensionName_new == "机构":
            sqlvalue = self.getSqlValueZone.getSqlValue_zone(itemname, self.zoneid, self.startT, self.endT)
            return sqlvalue

        elif self.dataDimensionName_new == "医生":
            self.docid =self.esvalues['docId']
            self.docid_new = self.docid.encode('utf-8')  # 将unicode类型转换成字符串
            self.docname = self.getRC.getDocName(self.docid_new)
            return self.getSqlValueDoc.getSqlValue_doc(itemname, self.zoneid, self.docname, self.startT, self.endT)

        elif self.dataDimensionName_new == "科室":
            self.deptid = self.esvalues['deptId']
            self.deptid_new = self.deptid.encode('utf-8')  # 将unicode类型转换成字符串
            self.deptname = self.getRC.getDeptName(self.deptid_new)
            return self.getSqlValueDept.getSqlValue_dept(itemname, self.zoneid, self.deptname, self.startT, self.endT)

        elif self.dataDimensionName_new == "医疗组":
            self.groupid = self.esvalues['docGroup']
            return self.getSqlValueGroup.getSqlValue_group(itemname, self.zoneid, self.groupid, self.startT, self.endT)

        elif self.dataDimensionName_new == '汇总':
            print "暂无统计汇总的SQL配置，待后续完善"

# 计算指标SQL值时，警示维度执行此方法
    def warning(self,itemname):
        self.analysis_type = self.esvalues['analysisResultType']
        sqlvalue = self.getSqlValueZone.getSqlValue_analysis_Zone(itemname, self.zoneid, self.startT, self.endT,
                                                                  self.analysis_type)
        return sqlvalue

# 计算指标SQL值时，药品维度执行此方法
    def drug(self,itemname):
         self.productId=self.esvalues['productId'] #数据库表结构调整后标准产品对应的产品ID取不到
         sqlvalue = self.getSqlValueZone.getSqlValue_product_Zone(itemname, self.zoneid, self.startT, self.endT,
                                                                   self.productId)
         return sqlvalue

# 计算指标SQL值时，手术维度执行此方法
    def operation(self,itemname):
        if self.dataDimensionName_new == '机构':
            self.operationName = self.esvalues['operationCode']
            self.operationCode=self.getRC.getOperationCode(self.operationName)
            sqlvalue = self.getSqlValueZone.getSqlValue_Operation_Zone(itemname, self.zoneid, self.startT, self.endT,self.operationCode)
            return sqlvalue

#获取报表中指标的sql值
    def getItemsSql(self,itemname):

        name = 'self.{}'.format(self.dimension[self.bussinessDimensionName_str])
        functionName = eval(name)
        self.sqlvalue = functionName(self.itemname)
        if self.sqlvalue == None:  # 当SQL查询结果为None时
            self.sqlvalue_new = "The SQL's result is None"

        else:
            try:
                self.sqlvalue_f = round(float(self.sqlvalue), 2)  # 将指标值转换成浮点类型并保留两位小数点
                self.sqlvalue_new=self.sqlvalue_f
            except Exception:
                self.sqlvalue_new=self.sqlvalue.encode('utf8')
        return self.sqlvalue_new

#获取报表中指标的ES值
    def getItemESvalue(self,itemKey):

        if itemKey not in self.esvalues:
            itemname = self.allitems[long(itemKey)]
            itemname = itemname.encode("utf-8")
            esvalue_new = "Nodata"

        elif itemKey in self.esvalues:
            esvalue = self.esvalues[itemKey]  # 获取指标对应的ES指标值
            if isinstance(esvalue,unicode)==True:
                if ',' in esvalue:
                    esvalue=esvalue.replace(",", "")

            itemname = self.allitems[long(itemKey)]  # 获取指标的名称
            itemname = itemname.encode("utf-8")

            # esvalue = esvalue.encode("utf-8")
            # esvalue_replace = esvalue.replace(",", "")
            try:
                if esvalue and esvalue!=None:
                    esvalue_f=round(float(esvalue),2) # 将指标值转换成浮点类型并保留两位小数点
                    esvalue_new=esvalue_f
                else:
                    esvalue_new=None
            except Exception,error:
                print error
                esvalue_new=None

        return esvalue_new,itemname

#执行报表中指标的验证并输出测试结果
    def executeCheck(self):

        self.saveTR.createXlsx() #创建Excel文件
        self.saveTR.writeColName()
        count=1

        # self.hospitalInfor = self.getRC.getHospitalInfor(self.reportDataName)
        self.bussinessDimensionName_str = self.bussinessDimensionName.encode('utf-8')#统计维度
        self.dataDimensionName_new = self.dataDimensionName.encode('utf-8')  # 数据维度
        self.startT = self.reportTime[0]  # 报表数据开始时间
        self.endT = self.reportTime[1]  # 报表数据结束时间
        self.functionName = self.dimension[self.bussinessDimensionName_str] + "(self.itemname)"

        for itemkey in self.items_new:
            self.esValue=self.getItemESvalue(itemkey)
            self.esvalue_f,self.itemname=self.esValue[0],self.esValue[1]
            self.sqlvalue_f=self.getItemsSql(self.itemname)
            self.rlt=self.isEqual(self.esvalue_f,self.sqlvalue_f)
            #将内容打印到日志里面
            # self.content=self.rlt+","+self.itemname+","+str(self.esvalue_f)+','+str(self.sqlvalue_f)
            # mylog(self.content)

            print self.rlt,self.itemname, self.esvalue_f, self.sqlvalue_f,"\n"

            self.saveTR.writeData(self.itemname,self.esvalue_f,self.sqlvalue_f,self.rlt,count,itemkey)
            count+=1
        self.saveTR.closexlsx()











