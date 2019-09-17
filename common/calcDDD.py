#coding:utf8
from common.connectDB import connectDB
from common.configReader import configReader
import common.convert_unit as unit
import os

path=os.path.abspath('../config/new_index.ini')


#计算抗菌药物使用量及消耗总克数
class DDDS():

    def __init__(self):

        #读取配置项
        self.cfR=configReader(path)

        #连接报表数据库
        self.conndb=connectDB()
        self.conn=self.conndb.connect(self.conndb.dbname_report)
        self.cur=self.conndb.getCursor(self.conn)

#获取标准产品及比对的药品的信息，返回的是tuple类型
    def getDrugs(self,field,key,*args):
        try:
            self.field=field
            self.key=key
            self.sql=self.cfR.get(self.field,self.key)
            self.cur.execute(self.sql,(args))
            sqlvalue =self.cur.fetchall()
        except Exception,error:
            sqlvalue=None
        return sqlvalue

#获取符合条件的所有药品ID
    def getDrugids(self,field,key,*args):
        result=self.getDrugs(field,key,*args)
        if result:
            drugids=[id[0] for id in result]
        else:
            drugids=None
        print(drugids)
        return drugids

#将获取的标准产品及比对的药品的信息存放到字典中
    def getdrugsvalue(self,field,key,*args):

        result=self.getDrugs(field,key,*args)
        print 'result',result
        drugs_value={}
        if result:
            i=0
            for each in result:
                if each[0] in drugs_value.keys(): #解决字典中key值相同时一些药品消耗总克数统计不到的问题
                    keyname=each[0]+str(i)
                    i+=1
                else:
                    keyname=each[0]
                drugs_value[keyname] = {'productid':each[1],"count_unit":each[2], "despensing_num":each[3],"qty":each[-2],"qty_unit":each[-1]}
        else:
               drugs_value=None
        return drugs_value

#获取用户自定义的转换规格，转换单位及DDD值，DDD单位
    # def getselfvalues(self,field,key,*args):
    #
    #     result=self.getDrugs(field,key,*args)
    #     self_value={}
    #     if result:
    #         i=0
    #         for each in result:
    #             keyname=each[0].encode('utf8')
    #             self_value[keyname] = {'ddd':each[1],"ddd_unit":each[2], "trans_spec":each[3], "trans_spec_unit":each[4]}
    #     else:
    #            self_value=None
    #     return self_value

# 获取用户自定义的转换规格，转换单位及DDD值，DDD单位
    def getselfvalues_new(self, field, key, *args):

            result = self.getDrugs(field, key, *args)
            self_value = {}
            if result:
                i = 0
                for each in result:
                    keyname = each[0].encode('utf8')
                    if key=='self_values_ddd' or key=='product_ddd':
                        self_value[keyname] = {'ddd': each[1], "ddd_unit": each[2]}
                    if key=='self_values_trans' or key=='product_trans':
                        self_value[keyname]={"trans_spec": each[1],"trans_spec_unit": each[2]}
            else:
                self_value = None
            return self_value
#获取用户传入的qty,qty_unit


#进行指标的计算，qty=1
    def calcddds_1(self,field,key,*args):
        drugids=self.getDrugids(field,key,*args)
        # selfvalue=self.getselfvalues(field,'self_values')
        selfvalue_ddd=self.getselfvalues_new (field,'self_values_ddd')
        selfvalue_trans=self.getselfvalues_new(field,'self_values_trans')
        productvalue_ddd = self.getselfvalues_new(field, 'product_ddd')
        productvalue_trans = self.getselfvalues_new(field, 'product_trans')
        drugsvalue=self.getdrugsvalue(field,key,*args)
        # print drugids,"\n",drugsvalue
        ddds=0
        qty=0
        if drugids:
            try:
                for each in drugsvalue.keys():
                    productid=drugsvalue[each]['productid']
                    #t1.Count_Unit * t1.Despensing_Num * t4.trans_Specification* t4.spec_quantity / t4.ddd
                    self.count_unit=drugsvalue[each]['count_unit']
                    self.despensing_num=drugsvalue[each]['despensing_num']
                    #获取系统的转换规格与ddd值
                    # print productvalue_ddd
                    self.ddd_sys = float(productvalue_ddd[productid]['ddd'])
                    self.dddunit_sys = productvalue_ddd[productid]['ddd_unit']
                    self.spec_quantity_sys = float(productvalue_trans[productid]['trans_spec'])
                    self.en_spec_unit_sys = productvalue_trans[productid]['trans_spec_unit']

                    # self.ddd_sys=drugsvalue[each]['ddd']
                    # self.dddunit_sys = drugsvalue[each]['ddd_unit']
                    # self.spec_quantity_sys=drugsvalue[each]['spec_quantity']
                    # self.en_spec_unit_sys = drugsvalue[each]['en_spec_unit']

                    # 获取用户的转换规格与ddd值,如果用户没有设置直接赋0
                    # if selfvalue:
                    #     if productid in selfvalue.keys():
                    #         self.ddd_self = selfvalue[productid]['ddd']
                    #         self.dddunit_self = selfvalue[productid]['ddd_unit']
                    #         self.spec_quantity_self = selfvalue[productid]['trans_spec']
                    #         self.en_spec_unit_self = selfvalue[productid]['trans_spec_unit']
                    if selfvalue_ddd:
                        if productid in selfvalue_ddd.keys():
                            self.ddd_self = float(selfvalue_ddd[productid]['ddd'])
                            self.dddunit_self = selfvalue_ddd[productid]['ddd_unit']
                        else:
                            self.ddd_self = 0
                            self.dddunit_self = 0

                    if selfvalue_trans:
                        if productid in selfvalue_trans.keys():
                            self.spec_quantity_self = float(selfvalue_trans[productid]['trans_spec'])
                            self.en_spec_unit_self = selfvalue_trans[productid]['trans_spec_unit']
                        else:
                            self.spec_quantity_self = 0
                            self.en_spec_unit_self =0

                    # print self.count_unit, self.despensing_num, self.ddd_sys, self.dddunit_sys, self.spec_quantity_sys,self.en_spec_unit_sys
                    # print self.ddd_self, self.dddunit_self, self.spec_quantity_self, self.en_spec_unit_self
                    # print self.ddd_self,self.dddunit_self
                    # 优先取用户自定义的dddz，都为空不计算
                    if self.ddd_self and self.ddd_self>0 and self.dddunit_self :
                        self.cal_ddd=self.ddd_self
                        self.cal_dddunit=self.dddunit_self

                    elif self.ddd_sys and self.ddd_sys>0  and self.dddunit_sys:
                        self.cal_ddd = self.ddd_sys
                        self.cal_dddunit = self.dddunit_sys
                    else:
                        continue

                    #优先取用户自定义的转换规格，都为空不计算
                    if self.spec_quantity_self and self.spec_quantity_self>0 and self.en_spec_unit_self:
                        self.cal_spec_quantity=self.spec_quantity_self
                        self.cal_enSpecUnit=self.en_spec_unit_self

                    elif self.spec_quantity_sys and self.spec_quantity_sys>0 and self.en_spec_unit_sys:
                        self.cal_spec_quantity = self.spec_quantity_sys
                        self.cal_enSpecUnit = self.en_spec_unit_sys

                    else:
                        continue

                    self.cal_spec_quantity=unit.convert_dddUnit(self.cal_spec_quantity,self.cal_enSpecUnit,self.cal_dddunit)[0]
                    #self.qyt:消耗克数
                    # print "self.count_unit,self.despensing_num,self.cal_spec_quantity,self.cal_ddd",self.count_unit,self.despensing_num,self.cal_spec_quantity,self.cal_ddd

                    qty+=(float(self.count_unit)*self.despensing_num*self.cal_spec_quantity)
                    ddds+=((float(self.count_unit)*self.despensing_num*self.cal_spec_quantity)/self.cal_ddd)
                    # print ddds,qty,self.count_unit,self.despensing_num,self.cal_spec_quantity,self.cal_ddd
                return ddds,qty
            except Exception,e:
                print "计算时错误",e

#qty=0,住院取ipt_drug表中的qty,qty_unit,门诊opt_recipe_drug表中没有qty,qty_unit字段
    def calcddds_0(self,field,key,*args):
        drugids = self.getDrugids(field, key, *args)
        selfvalue_ddd = self.getselfvalues_new(field, 'self_values_ddd')
        productvalue_ddd = self.getselfvalues_new(field, 'product_ddd')
        drugsvalue = self.getdrugsvalue(field, key, *args)
        print(drugsvalue)

        ddds = 0
        qty = 0
        if drugids:
            try:
                for each in drugsvalue.keys():
                    productid=drugsvalue[each]['productid']
                    self.ddd_sys = float(productvalue_ddd[productid]['ddd'])
                    self.dddunit_sys = productvalue_ddd[productid]['ddd_unit']
                    self.qty=drugsvalue[each]['qty']
                    self.qty_unit=drugsvalue[each]['qty_unit']
                    if selfvalue_ddd:
                        if productid in selfvalue_ddd.keys():
                            self.ddd_self = float(selfvalue_ddd[productid]['ddd'])
                            self.dddunit_self = selfvalue_ddd[productid]['ddd_unit']
                        else:
                            self.ddd_self = 0
                            self.dddunit_self = 0

                    # 优先取用户自定义的dddz，都为空不计算
                    if self.ddd_self and self.ddd_self>0 and self.dddunit_self :
                        self.cal_ddd=self.ddd_self
                        self.cal_dddunit=self.dddunit_self

                    elif self.ddd_sys and self.ddd_sys>0  and self.dddunit_sys:
                        self.cal_ddd = self.ddd_sys
                        self.cal_dddunit = self.dddunit_sys
                    else:
                        continue


                    self.qty=unit.convert_dddUnit(self.qty,self.qty_unit,self.cal_dddunit)[0]
                    qty+=self.qty
                    ddds+=(self.qty/self.cal_ddd)

                return ddds,qty
            except Exception,e:
                print "计算时错误",e











#
#
ddds=DDDS()

print ddds.calcddds_0('zone_ddds','住院消耗总克数','4','2014-08-01','2014-08-01','187684')
print ddds.calcddds_1('zone_ddds','住院消耗总克数','4','2014-08-01','2014-08-01','187684')
# #

#right:opt_191025 ，ipt_187698



