# coding:utf-8
from common.configReader import configReader
from common.connectDB import connectDB
from configvalue.getconfigvalue import configValue
from common.calcDDD import DDDS
from common.log import mylog, mylog_except
import os


path=os.path.abspath('./config/new_index.ini')

class getZoneSQLvalue():
    def __init__(self):
        # 连接报表数据库
        self.conndb = connectDB()
        self.conn = self.conndb.connect(self.conndb.dbname_report)
        self.cur = self.conndb.getCursor(self.conn)

        # 从配置文件中获取SQL配置项
        self.confR = configReader(path)

        #获取用户中心配置项的值
        self.configValue = configValue()
        self.configKey = 'ConfigurationItem_zone'

        #计算DDDS
        self.calcddds=DDDS()

        self.hospitalitems = self.confR.getitems('hospital')  # 全院指标的SQL
        self.optitems = self.confR.getitems('zone')  # 常规SQL
        self.optcalc = self.confR.getitems('item_calc')  # 计算指标的SQL，两个数相乘
        self.optcalc100 = self.confR.getitems('item_calc100')  # 计算指标乘以100的SQL
        self.optcalcminus = self.confR.getitems('item_calc_minus')  # 两个指标相减
        self.itemname_config = self.confR.getitems('ConfigurationItem_zone')
        self.zoneddds = self.confR.getitems('zone_ddds')
        self.hospitalddds = self.confR.getitems('hospital_ddds')
        self.drugzone = self.confR.getitems('drug_zone')
        self.productInfor = self.confR.getitems('drug_productInfor')
        self.operation=self.confR.getitems('operation_zone')

    def getValueInZone(self, itemname, zoneid, startT, endT):
        self.sql = self.confR.get("zone", itemname)
        sqlValue = self.conndb.executeSQL_zoneid_one(self.cur, self.sql, zoneid, startT, endT)
        return sqlValue

    def getValueInddds(self, itemname, zoneid, startT, endT,productID=None):


        self.zoneddds=self.confR.getitems('zone_ddds')
        self.hospitalddds=self.confR.getitems('hospital_ddds')

        #获取qty计算方法配置项的值，根据配置项进行消耗克数的计算
        qtyvalue=self.configValue.getvalue('qty')
        qtyvalue_int=int(qtyvalue.encode('utf8'))
        if qtyvalue_int==1:
            if itemname in self.zoneddds:
                self.sqlValue=self.calcddds.calcddds_1('zone_ddds',itemname,zoneid,startT,endT)
            elif itemname in self.hospitalddds:
                self.sqlValue = self.calcddds.calcddds_1('hospital_ddds', itemname, zoneid, startT, endT,productID,zoneid, startT, endT,productID)
                print self.sqlValue
        else:
            mylog('配置项错误')
        return self.sqlValue

    def getValueInConfig(self, itemname, zoneid, startT, endT, configValue, configKey):
        self.sql = self.confR.get(configKey, itemname)
        sqlValue = self.conndb.executeSQL_zoneid_three(self.cur, self.sql, zoneid, startT, endT, configValue)

        return sqlValue

    def getValueInHospital(self, itemname, zoneid, startT, endT):
        self.sql = self.confR.get("hospital", itemname)
        sqlValue = self.conndb.executeSQL_zoneid_two(self.cur, self.sql, zoneid, startT, endT)
        return sqlValue

    def getValueInCalcminus(self, itemname, zoneid, startT, endT):

        try:
            self.sql = self.confR.get("item_calc_minus", itemname)
            self.itemnames = self.sql.split("-")
            self.itemnameTwoO, self.itemnameTwoT = self.itemnames[0], self.itemnames[1]
            if self.itemnameTwoO == '医疗药品总收入' and self.itemnameTwoT == '全院患者使用中药饮片费用':
                self.itemTwoOsql = self.confR.get("hospital", self.itemnameTwoO)
                self.itemTwoTsql = self.confR.get("hospital", self.itemnameTwoT)
                self.value_itemTwoO = self.conndb.executeSQL_zoneid_two(self.cur, self.itemTwoOsql, zoneid, startT,
                                                                        endT)
                self.value_itemTwoT = self.conndb.executeSQL_zoneid_two(self.cur, self.itemTwoTsql, zoneid, startT,
                                                                        endT)
            else:
                self.itemTwoOsql = self.confR.get("zone", self.itemnameTwoO)
                self.itemTwoTsql = self.confR.get("zone", self.itemnameTwoT)
                self.value_itemTwoO = self.conndb.executeSQL_zoneid_one(self.cur, self.itemTwoOsql, zoneid, startT,
                                                                        endT)
                self.value_itemTwoT = self.conndb.executeSQL_zoneid_one(self.cur, self.itemTwoTsql, zoneid, startT,
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

    def getValueInCalc(self, itemname, zoneid, startT, endT, optcalcminus):

        self.sql = self.confR.get("item_calc", itemname)
        self.itemnames = self.sql.split("/")
        self.itemnameOne, self.itemnameTwo = self.itemnames[0], self.itemnames[1]
        self.itemvalue_one = self.getCalc_Numerator_zone(self.itemnameOne, zoneid, startT, endT, optcalcminus)
        self.itemvalue_two = self.getCalc_denominator_zone(self.itemnameTwo, zoneid, startT, endT, optcalcminus)
        print self.itemvalue_one,self.itemvalue_two

        try:

            if self.itemvalue_one and self.itemvalue_two:
                sqlValue = self.itemvalue_one / self.itemvalue_two
                return sqlValue
            else:
                mylog("计算指标不成功，有指标值为空")

        except Exception, error:

            mylog("计算指标发生错误")
            mylog_except(error)

    def getValueInCalc100(self, itemname, zoneid, startT, endT):

        self.sql = self.confR.get("item_calc100", itemname)
        self.itemnames = self.sql.split("/")
        self.itemnameOne, self.itemnameTwo = self.itemnames[0], self.itemnames[1]

        if self.itemnameOne in self.zoneddds:
                self.itemvalue_one = self.calcddds.calcddds_1('zone_ddds', self.itemnameOne, zoneid, startT, endT)[0]

        elif self.itemnameOne in self.hospitalddds:
            self.itemvalue_one = self.calcddds.calcddds_1('hospital_ddds', self.itemnameOne, zoneid, startT, endT, zoneid, startT, endT)[0]
        else:
            self.itemOneSql = self.confR.get("zone", self.itemnameOne)
            self.itemvalue_one = self.conndb.executeSQL_zoneid_one(self.cur, self.itemOneSql, zoneid, startT, endT)

        self.itemTwoSql = self.confR.get('zone', self.itemnameTwo)
        self.itemvalue_two = self.conndb.executeSQL_zoneid_one(self.cur, self.itemTwoSql, zoneid, startT, endT)
        try:
            if self.itemvalue_one and self.itemvalue_two:
                sqlValue = float(self.itemvalue_one) / float(self.itemvalue_two) * 100
                return sqlValue
            else:
                mylog("计算指标不成功，有指标值为空")

        except Exception, error:
            mylog("计算指标发生错误")
            mylog_except(error)

#得到药品维度下面计算指标的值
    def getValueInCalc100_drug(self, itemname,zoneid,startT, endT,productID):

            self.sql = self.confR.get("item_calc100", itemname)
            self.itemnames = self.sql.split("/")
            self.itemnameOne, self.itemnameTwo = self.itemnames[0], self.itemnames[1]
            self.itemOneSql = self.confR.get("drug_zone", self.itemnameOne)
            self.itemvalue_one = self.conndb.executeSQL_zoneid_three(self.cur, self.itemOneSql, zoneid, startT, endT,productID)
            self.itemTwoSql = self.confR.get('drug_zone', self.itemnameTwo)
            self.itemvalue_two = self.conndb.executeSQL_zoneid_three(self.cur, self.itemTwoSql, zoneid, startT, endT,productID)
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
    def getCalc_Numerator_zone(self, itemnameOne, zoneid, startT, endT, optcalcminus):

        self.itemnameOne = itemnameOne
        if (self.itemnameOne == '全院抗菌药物使用金额' or self.itemnameOne == '国家基药目录品种使用金额'):
            self.itemOneSql = self.confR.get("hospital", self.itemnameOne)
            self.itemvalue_one = self.conndb.executeSQL_zoneid_two(self.cur, self.itemOneSql, zoneid, startT, endT)
            if self.itemvalue_one:
                self.itemvalue_one = float(self.itemvalue_one)
            else:
                self.itemvalue_one=0

        elif self.itemnameOne in optcalcminus:

            self.itemvalue_one = self.getValueInCalcminus(itemnameOne, zoneid, startT, endT)

        elif self.itemnameOne in self.itemname_config[3:8]:
            configValue = self.configValue.getvalue(self.itemnameOne)
            self.itemvalue_one = self.getValueInConfig(self.itemnameOne, zoneid, startT, endT, configValue,self.configKey)

        elif self.itemnameOne == self.itemname_config[7]:

            drugcodes = self.configValue.getDrugCode(self.itemnameOne)
            self.sql = self.confR.get(self.configKey, self.itemnameOne)
            self.itemvalue_one = self.conndb.executeSQL_zoneid_three(self.cur, self.sql, zoneid, startT, endT, drugcodes)

        elif self.itemnameOne in self.zoneddds or self.itemnameOne in self.hospitalddds:

            try:
                self.itemvalue_one = self.getValueInddds(self.itemnameOne, zoneid, startT, endT)[0]

            except Exception,E:
                self.itemvalue_one=0
                mylog_except(E)

        else:
            self.itemOneSql = self.confR.get("zone", self.itemnameOne)

            self.itemvalue_one = self.conndb.executeSQL_zoneid_one(self.cur, self.itemOneSql, zoneid, startT, endT)

            if self.itemvalue_one:
                self.itemvalue_one = float(self.itemvalue_one)
            else:
                self.itemvalue_one=0

        return self.itemvalue_one

    # 得到计算指标中分母的值
    def getCalc_denominator_zone(self, itemnameTwo, zoneid, startT, endT, optcalcminus):
        self.itemnameTwo = itemnameTwo
        self.optcalcminus = optcalcminus

        if self.itemnameTwo in self.optcalcminus:

            self.itemvalue_two = self.getValueInCalcminus(self.itemnameTwo, zoneid, startT, endT)

        elif self.itemnameTwo in self.itemname_config[3:8]:
            configValue = self.configValue.getvalue(self.itemnameTwo)
            self.itemvalue_two = self.getValueInConfig(self.itemnameTwo, zoneid, startT, endT, configValue,
                                                       self.configKey)
        elif self.itemnameTwo in self.zoneddds or self.itemnameTwo in self.hospitalddds:
            try:
                self.itemvalue_two = self.getValueInddds(self.itemnameOne, zoneid, startT, endT)[0]

            except Exception,E:
                self.itemvalue_two=0
                mylog_except(E)
        else:
            self.itemTwoSql = self.confR.get("zone", self.itemnameTwo)
            self.itemvalue_two = self.conndb.executeSQL_zoneid_one(self.cur, self.itemTwoSql, zoneid, startT, endT)
            self.itemvalue_two = float(self.itemvalue_two)

        return self.itemvalue_two

    # 获取手术维度+机构的SQL值
    def getSqlValue_Operation_Zone(self, itemname, zoneid, startT, endT,operationCode):
        # for i in self.operation:
        #     print i

        if itemname in self.operation:
            self.sql = self.confR.get("operation_zone", itemname)
            sqlValue = self.conndb.executeSQL_zoneid_three(self.cur, self.sql, zoneid, startT, endT,operationCode)
        else:
            print '指标在配置文件中不存在'
            sqlValue=None
        return sqlValue

# 获取药品维度+机构的SQL值
    def getSqlValue_product_Zone(self, itemname, zoneid, startT, endT,productId):
        print productId
        if itemname in self.drugzone:
             self.sql = self.confR.get("drug_zone", itemname)
             self.sqlValue = self.conndb.executeSQL_zoneid_three(self.cur, self.sql, zoneid, startT, endT,productId)
        elif itemname in self.productInfor:
             self.sql = self.confR.get("drug_productInfor", itemname)
             self.sqlValue=self.conndb.executeSQL_drug_productinfor(self.cur,self.sql,productId)
        elif itemname in self.optcalc100:
             self.sqlValue=self.getValueInCalc100_drug(itemname,zoneid,startT,endT,productId)
        elif itemname =='全院患者使用频次' or itemname=='全院患者使用数量':
            self.sql = self.confR.get('hospital_ddds', itemname)
            self.sqlValue = self.conndb.executeSQL_drug(self.cur, self.sql, zoneid, startT, endT, productId)
        elif itemname=='消耗总克数':
            try:
                self.sqlValue = self.getValueInddds(itemname, zoneid, startT, endT,productId)[1]
            except Exception,E:
                self.sqlValue=0
                mylog_except(E)
        else:
            self.sqlValue= '指标不存在'.decode('utf8')
        return self.sqlValue

    # 获取警示维度+机构的SQL值
    def getSqlValue_analysis_Zone(self, itemname, zoneid, startT, endT, analysis_type):
        self.messgeItems = self.confR.getitems("message_zone")
        self.calc = self.confR.getitems('item_calc')

        if itemname in self.messgeItems:
            self.sql = self.confR.get("message_zone", itemname)
            sqlValue = self.conndb.executeSQL_zoneid_three(self.cur, self.sql, zoneid, startT, endT, analysis_type)
            return sqlValue


        else:
            mylog("没有该指标的配置")


# 获取缺省机构维度指标对应的SQL值
    def getSqlValue_zone(self, itemname, zoneid, startT, endT):


        try:
            
            if itemname in self.optitems:

                sqlValue = self.getValueInZone(itemname, zoneid, startT, endT)
                return sqlValue

            elif itemname in self.hospitalitems:

                sqlValue = self.getValueInHospital(itemname, zoneid, startT, endT)
                return sqlValue

            elif itemname in self.optcalc:

                sqlValue = self.getValueInCalc(itemname, zoneid, startT, endT, self.optcalcminus)
                return sqlValue

            elif itemname in self.optcalcminus:

                sqlValue = self.getValueInCalcminus(itemname, zoneid, startT, endT)
                return sqlValue

            elif itemname in self.optcalc100:

                sqlValue = self.getValueInCalc100(itemname, zoneid, startT, endT)
                return sqlValue

            elif itemname in self.itemname_config[3:8]:
                configValue = self.configValue.getvalue(itemname)
                sqlValue = self.getValueInConfig(itemname, zoneid, startT, endT, configValue, self.configKey)
                return sqlValue

            elif itemname == self.itemname_config[7]:

                drugcodes = self.configValue.getDrugCode(itemname)
                self.sql = self.confR.get(self.configKey, itemname)
                sqlValue = self.conndb.executeSQL_zoneid_three(self.cur, self.sql, zoneid, startT, endT, drugcodes)
                return sqlValue

            elif itemname in self.zoneddds or itemname in self.hospitalddds:
                try:
                    sqlValue = self.getValueInddds(itemname,zoneid,startT,endT)[0]
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





