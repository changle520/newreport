#coding:utf8
import requests
import json
from common.configReader import configReader
from common.connectDB import connectDB
import os

path=os.path.abspath('./config/sysconfig.ini')

class configValue():
        def __init__(self):
            self.cfR=configReader(path)
            self.url=self.cfR.get('url','url')
            self.headers = {
                'Content-Type': "application/json",
            }

            # self.conndb = connectDB()
            # self.conn = self.conndb.connect(self.conndb.dbname_report)
            # self.cur = self.conndb.getCursor(self.conn)


# 登录系统
        def login(self):
            self.session = requests.session()
            self.api =self.cfR.get('api','login')
            self.addr = "{}/{}".format(self.url, self.api)
            self.name=self.cfR.get('url','username')
            self.passwd = self.cfR.get('url', 'password')
            self.params = {"name": self.name, "password": self.passwd}
            self.loginr=self.session.post(self.addr, data=json.dumps(self.params), headers=self.headers)


#获取系统配置项的值
        def getvalue(self,itemname):

            self.login()
            self.configname=self.cfR.get('confignames_item',itemname)
            self.api = self.cfR.get('api','operationName')
            self.addr = "{}/{}".format(self.url, self.api)
            self.params = {"showName":self.configname}
            response = self.session.get(self.addr, params=self.params, headers=self.headers)
            result = response.json()

            value = result['data']['recordList'][0]['value']
            return value


#获取I类切口手术预防使用抗菌药物合理分类的配置值并转成对应的药品分类供SQL查询
        def getDrugCode(self,itemname):
            self.configValue=self.getvalue(itemname)
            self.configValueStr=self.configValue.encode('utf8')
            codes = []
            for each in self.configValueStr.split("|"):
                if each.startswith('001'):
                    codes.append(each)
                    continue
                self.sql = self.cfR.get('drug', 'drugcode')
                self.cur.execute(self.sql,(each,))
                code = self.cur.fetchone()[0]
                codes.append(code)
            codesrlt='|'.join(codes)
            return codesrlt

if __name__=="__main__":

    configV=configValue()
    print(configV.getvalue("出院患者中抗菌药物治疗使用前病原学检查送检人次"))
