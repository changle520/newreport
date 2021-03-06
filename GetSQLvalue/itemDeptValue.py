# coding:utf-8
from common.configReader import configReader
from common.connectDB import connectDB
from configvalue.getconfigvalue import configValue
from common.calcDDD import DDDS
from common.log import mylog, mylog_except
import os

path=os.path.abspath('./config/new_index.ini')

class getDeptSQLvalue():
    def __init__(self):
        # 连接报表数据库
        self.conndb = connectDB()
        self.conn = self.conndb.connect(self.conndb.dbname_report)
        self.cur = self.conndb.getCursor(self.conn)

        # 从配置文件中获取SQL配置项
        self.confR = configReader(path)

        #获取用户中心配置项的值
        self.configValue = configValue()
        self.configKey = 'ConfigurationItem_dept'

        #计算DDDS
        self.calcddds=DDDS()

        self.hospitalitems = self.confR.getitems('hospital_dept')  # 全院指标的SQL
        self.optitems = self.confR.getitems('default_dept')  # 常规SQL
        self.optcalc = self.confR.getitems('item_calc')  # 计算指标的SQL，两个数相乘
        self.optcalc100 = self.confR.getitems('item_calc100')  # 计算指标乘以100的SQL
        self.optcalcminus = self.confR.getitems('item_calc_minus')  # 两个指标相减
        self.itemname_config = self.confR.getitems('ConfigurationItem_dept')
        self.deptddds = self.confR.getitems('dept_ddds')
        self.hospitalddds = self.confR.getitems('hospitalDept_ddds')


    def getValueInDept(self, itemname, zoneid,deptid, startT, endT):
        self.sql = self.confR.get("default_dept", itemname)
        sqlValue = self.conndb.executeSQL_deptid_one(self.cur, self.sql, zoneid,deptid, startT, endT)
        return sqlValue

    def getValueInddds(self, itemname, zoneid,deptid, startT, endT,productID=None):


        self.deptddds=self.confR.getitems('dept_ddds')
        self.hospitalddds=self.confR.getitems('hospitalDept_ddds')

        #获取qty计算方法配置项的值，根据配置项进行消耗克数的计算
        qtyvalue=self.configValue.getvalue('qty')
        qtyvalue_int=int(qtyvalue.encode('utf8'))
        if qtyvalue_int==1:
            if itemname in self.deptddds:
                self.sqlValue=self.calcddds.calcddds_1('dept_ddds',itemname,zoneid,deptid,startT,endT)
            elif itemname in self.hospitalddds:
                self.sqlValue = self.calcddds.calcddds_1('hospitalDept_ddds', itemname, zoneid,deptid, startT, endT,productID,zoneid, startT, endT,productID)
                print self.sqlValue
        else:
            mylog('配置项错误')
        return self.sqlValue

    def getValueInConfig(self, itemname, zoneid,deptid, startT, endT, configValue, configKey):
        self.sql = self.confR.get(configKey, itemname)
        sqlValue = self.conndb.executeSQL_deptid_three(self.cur, self.sql, zoneid,deptid,startT, endT, configValue)
        return sqlValue

    def getValueInHospital(self, itemname, zoneid,deptid,startT, endT):
        self.sql = self.confR.get("hospital_dept", itemname)
        sqlValue = self.conndb.executeSQL_deptid_two(self.cur, self.sql, zoneid,deptid, startT, endT)
        return sqlValue

    def getValueInCalcminus(self, itemname, zoneid, deptid,startT, endT):

        try:
            self.sql = self.confR.get("item_calc_minus", itemname)
            self.itemnames = self.sql.split("-")
            self.itemnameTwoO, self.itemnameTwoT = self.itemnames[0], self.itemnames[1]
            if self.itemnameTwoO == '医疗药品总收入' and self.itemnameTwoT == '全院患者使用中药饮片费用':
                self.itemTwoOsql = self.confR.get("hospital_dept", self.itemnameTwoO)
                self.itemTwoTsql = self.confR.get("hospital_dept", self.itemnameTwoT)
                self.value_itemTwoO = self.conndb.executeSQL_deptid_two(self.cur, self.itemTwoOsql, zoneid,deptid, startT,
                                                                        endT)
                self.value_itemTwoT = self.conndb.executeSQL_deptid_two(self.cur, self.itemTwoTsql, zoneid,deptid, startT,
                                                                        endT)
            else:
                self.itemTwoOsql = self.confR.get("default_dept", self.itemnameTwoO)
                self.itemTwoTsql = self.confR.get("default_dept", self.itemnameTwoT)
                self.value_itemTwoO = self.conndb.executeSQL_deptid_one(self.cur, self.itemTwoOsql, zoneid,deptid, startT,
                                                                        endT)
                self.value_itemTwoT = self.conndb.executeSQL_deptid_one(self.cur, self.itemTwoTsql, zoneid,deptid, startT,
                                                                        endT)

            if self.value_itemTwoO == None:
                self.value_itemTwoO = 0
            if self.value_itemTwoT == None:
                self.value_itemTwoT = 0
            self.itemvalue_two = float(self.value_itemTwoO) - float(self.value_itemTwoT)

            return self.itemvalue_two

        except Exception, error:
            mylog("指标计算时出错")
            mylog_except(error)

    def getValueInCalc(self, itemname, zoneid,deptid, startT, endT, optcalcminus):

        self.sql = self.confR.get("item_calc", itemname)
        self.itemnames = self.sql.split("/")
        self.itemnameOne, self.itemnameTwo = self.itemnames[0], self.itemnames[1]
        self.itemvalue_one = self.getCalc_Numerator_zone(self.itemnameOne, zoneid,deptid, startT, endT, optcalcminus)
        self.itemvalue_two = self.getCalc_denominator_zone(self.itemnameTwo, zoneid,deptid, startT, endT, optcalcminus)

        try:

            if self.itemvalue_one and self.itemvalue_two:
                sqlValue = self.itemvalue_one / self.itemvalue_two
                return sqlValue
            else:
                mylog("计算指标不成功，有指标值为空")

        except Exception, error:

            mylog("计算指标发生错误")
            mylog_except(error)

    def getValueInCalc100(self, itemname, zoneid,deptid, startT, endT):

        self.sql = self.confR.get("item_calc100", itemname)
        self.itemnames = self.sql.split("/")
        self.itemnameOne, self.itemnameTwo = self.itemnames[0], self.itemnames[1]

        if self.itemnameOne in self.deptddds:
                self.itemvalue_one = self.calcddds.calcddds_1('dept_ddds', self.itemnameOne, zoneid,deptid, startT, endT)[0]

        elif self.itemnameOne in self.hospitalddds:
            self.itemvalue_one = self.calcddds.calcddds_1('hospitalDept_ddds', self.itemnameOne, zoneid,deptid, startT, endT, zoneid, startT, endT)[0]
        else:
            self.itemOneSql = self.confR.get("default_dept", self.itemnameOne)
            self.itemvalue_one = self.conndb.executeSQL_deptid_one(self.cur, self.itemOneSql, zoneid,deptid,startT, endT)

        self.itemTwoSql = self.confR.get('default_dept', self.itemnameTwo)
        self.itemvalue_two = self.conndb.executeSQL_deptid_one(self.cur, self.itemTwoSql, zoneid,deptid,startT, endT)
        try:
            if self.itemvalue_one and self.itemvalue_two:
                sqlValue = float(self.itemvalue_one) / float(self.itemvalue_two) * 100
                return sqlValue
            else:
                mylog("计算指标不成功，有指标值为空")

        except Exception, error:
            mylog("计算指标发生错误")
            mylog_except(error)


    # 得到计算指标中分子的值
    def getCalc_Numerator_zone(self, itemnameOne, zoneid,deptid, startT, endT, optcalcminus):

        self.itemnameOne = itemnameOne
        if (self.itemnameOne == '全院抗菌药物使用金额' or self.itemnameOne == '国家基药目录品种使用金额'):
            self.itemOneSql = self.confR.get("hospital_dept", self.itemnameOne)
            self.itemvalue_one = self.conndb.executeSQL_deptid_two(self.cur, self.itemOneSql, zoneid,deptid, startT, endT)
            if self.itemvalue_one:
                self.itemvalue_one = float(self.itemvalue_one)
            else:
                self.itemvalue_one=0

        elif self.itemnameOne in optcalcminus:

            self.itemvalue_one = self.getValueInCalcminus(itemnameOne, zoneid,deptid, startT, endT)

        elif self.itemnameOne in self.itemname_config[0:4]:
            configValue = self.configValue.getvalue(self.itemnameOne)
            self.itemvalue_one = self.getValueInConfig(self.itemnameOne, zoneid,deptid, startT, endT, configValue,self.configKey)

        elif self.itemnameOne == self.itemname_config[4]:

            drugcodes = self.configValue.getDrugCode(self.itemnameOne)
            self.sql = self.confR.get(self.configKey, self.itemnameOne)
            self.itemvalue_one = self.conndb.executeSQL_deptid_three(self.cur, self.sql, zoneid,deptid, startT, endT, drugcodes)


        elif self.itemnameOne in self.deptddds or self.itemnameOne in self.hospitalddds:

            try:
                self.itemvalue_one = self.getValueInddds(self.itemnameOne, zoneid,deptid, startT, endT)[0]

            except Exception,E:
                self.itemvalue_one=0
                mylog_except(E)

        else:
            self.itemOneSql = self.confR.get("default_dept", self.itemnameOne)

            self.itemvalue_one = self.conndb.executeSQL_deptid_one(self.cur, self.itemOneSql, zoneid,deptid,startT, endT)

            if self.itemvalue_one:
                self.itemvalue_one = float(self.itemvalue_one)
            else:
                self.itemvalue_one=0

        return self.itemvalue_one

    # 得到计算指标中分母的值
    def getCalc_denominator_zone(self, itemnameTwo, zoneid,deptid, startT, endT, optcalcminus):
        self.itemnameTwo = itemnameTwo
        self.optcalcminus = optcalcminus

        if self.itemnameTwo in self.optcalcminus:

            self.itemvalue_two = self.getValueInCalcminus(self.itemnameTwo, zoneid,deptid, startT, endT)

        elif self.itemnameTwo in self.itemname_config[0:4]:
            configValue = self.configValue.getvalue(self.itemnameTwo)
            self.itemvalue_two = self.getValueInConfig(self.itemnameTwo, zoneid, deptid,startT, endT, configValue,
                                                       self.configKey)
        elif self.itemnameTwo in self.deptddds or self.itemnameTwo in self.hospitalddds:
            try:
                self.itemvalue_two = self.getValueInddds(self.itemnameOne, zoneid, deptid,startT, endT)[0]

            except Exception,E:
                self.itemvalue_two=0
                mylog_except(E)
        else:
            self.itemTwoSql = self.confR.get("default_dept", self.itemnameTwo)
            self.itemvalue_two = self.conndb.executeSQL_deptid_one(self.cur, self.itemTwoSql, zoneid,deptid, startT, endT)
            self.itemvalue_two = float(self.itemvalue_two)

        return self.itemvalue_two


# 获取缺省科室维度指标对应的SQL值
    def getSqlValue_dept(self, itemname, zoneid,deptid, startT, endT):

        try:

            if itemname in self.optitems:

                sqlValue = self.getValueInDept(itemname, zoneid,deptid, startT, endT)
                return sqlValue

            elif itemname in self.hospitalitems:

                sqlValue = self.getValueInHospital(itemname, zoneid, deptid,startT, endT)
                return sqlValue

            elif itemname in self.optcalc:

                sqlValue = self.getValueInCalc(itemname, zoneid,deptid, startT, endT, self.optcalcminus)
                return sqlValue

            elif itemname in self.optcalcminus:

                sqlValue = self.getValueInCalcminus(itemname, zoneid,deptid, startT, endT)
                return sqlValue

            elif itemname in self.optcalc100:

                sqlValue = self.getValueInCalc100(itemname, zoneid,deptid, startT, endT)
                return sqlValue

            elif itemname in self.itemname_config[0:4]:
                configValue = self.configValue.getvalue(itemname)
                sqlValue = self.getValueInConfig(itemname, zoneid,deptid, startT, endT, configValue, self.configKey)
                return sqlValue

            elif itemname == self.itemname_config[4]:

                drugcodes = self.configValue.getDrugCode(itemname)
                self.sql = self.confR.get(self.configKey, itemname)
                sqlValue = self.conndb.executeSQL_deptid_three(self.cur, self.sql, zoneid,deptid, startT, endT, drugcodes)
                return sqlValue

            elif itemname in self.deptddds or itemname in self.hospitalddds:
                try:
                    sqlValue = self.getValueInddds(itemname,zoneid,deptid,startT,endT)[0]
                except Exception,E:
                    sqlValue=0
                    mylog_except(E)
                return sqlValue

            else:
                logcontent = "该指标在指标库中不存在" + ',' + itemname
                mylog(logcontent)

        except Exception, error:
            mylog("执行过程中出错")
            mylog_except(error)





