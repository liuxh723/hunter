from bs4 import BeautifulSoup
from lxml import etree
import re
import xlwt
import os
import xlrd
from xlutils.copy import copy
import tushare as ts
import datetime
import pymysql
import time

from xlrd import xldate_as_tuple

path = "black"
filePath = path+'\codes.xls'
ts.set_token('29fa15c6fb00b315153cab6aa695a011ae78cc59752d90548272dfd8')
pro = ts.pro_api()

db = pymysql.connect(host='127.0.0.1', user='root', passwd='root', db='hunter', charset='utf8')
cursor = db.cursor()
def date(dates):#定义转化日期戳的函数,dates为日期戳
    '''delta=datetime.timedelta(days=dates)
    today=datetime.datetime.strptime('1899-12-30','%Y-%m-%d')+delta
    return datetime.datetime.strftime(today,'%Y%m%d')'''
    return datetime.datetime.strptime(dates, "%Y-%m-%d %H:%M:%S")

#建表
def getTradeDate(date,tradeNum):
    count = 0
    delta = datetime.timedelta(days=tradeNum*2)
    startDate = datetime.datetime.strftime( date - delta, "%Y%m%d")
    endDate = datetime.datetime.strftime( date , "%Y%m%d")
    print(startDate)

    try:
        df = pro.trade_cal(exchange='', start_date=startDate, end_date=endDate)
        c_len = df.shape[0]
        print(df)

    except Exception as aa:
        print(aa)

    for j in range(c_len):
        resu0 = list(df.loc[c_len - 1 - j])
        resu = []
        if resu0[2] == 1:
            count += 1
            if count == tradeNum:
                return resu0[1]

def insertDate(tableName,ts_code,columns,dataFrame,day):
    sql_insert = "replace INTO "+tableName+"(ts_code,"
    for i in range(len(columns)):
        strcloum = ""
        for j in range(day):
            strcloum += columns[i] + str(j) + ","
        sql_insert += strcloum
    sql_insert = sql_insert[0:len(sql_insert) - 1]
    sql_insert += ") VALUES('" + ts_code + "',"

    for k in range(len(columns)):
        for index, row in dataFrame.iterrows():
            sql_insert += "'"+str(row[columns[k]])+"'" + ","
    sql_insert = sql_insert[0:len(sql_insert) - 1]
    sql_insert += ")"
    print(sql_insert)
    cursor.execute(sql_insert)
    db.commit()

def createTable(tableName,columns,day):
    strSql = "CREATE TABLE IF NOT EXISTS "+tableName+"(ts_code VARCHAR(25),"
    strCloum = []
    for i in range(len(columns)):
        print(columns[i])
        strcloum = ""
        for j in range(day):
            strcloum += columns[i] + str(j) + " VARCHAR(25),"
        strSql += strcloum
    strSql = strSql[0:len(strSql) - 1]
    strSql += ")"
    print(strSql)
    cursor.execute(strSql)
    db.commit()

def getDailyBasic():
    cursor.execute("CREATE TABLE IF NOT EXISTS daily_basic(ts_code VARCHAR(25),trade_date VARCHAR(25),circ_mv VARCHAR(25),free_share VARCHAR(25))")
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_index(0)
    rows = sheet.nrows
    cols = sheet.ncols

    for i in range(rows):
        print(sheet.cell_value(i,1))
        endDate = date(sheet.cell_value(i,0))#datetime.datetime.strptime(sheet.cell_value(i+1,0), "%Y/%m/%d %H:%M:%S")

         #= datetime.datetime.strftime(Date, "%Y%m%d")
        startDate = getTradeDate(endDate, 1)
        try:
            df = pro.daily_basic(ts_code=sheet.cell_value(i,1), fields='ts_code,trade_date,circ_mv,free_share',start_date=startDate, end_date=endDate)
            c_len = df.shape[0]
            #print(df)

        except Exception as aa:
            print(aa)

        for j in range(c_len):
            resu0 = list(df.loc[c_len - 1 - j])
            try:
                sql_insert = "replace INTO daily_basic (ts_code,trade_date,circ_mv,free_share) VALUES ('%s', '%s', '%s', '%s')" % (
                    resu0[1], resu0[0],resu0[2],resu0[3]
                    )
                cursor.execute(sql_insert)
                db.commit()
            except Exception as err:
                print("insert err:" + err)
        time.sleep(1)

def getMoneyflow():
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_index(0)
    rows = sheet.nrows
    cols = sheet.ncols
    createTable("moneyflow_sm",["buy_sm_amount","sell_sm_amount"],30)
    createTable("moneyflow_md", ["buy_md_amount", "sell_md_amount"], 30)
    createTable("moneyflow_lg", ["buy_lg_amount", "sell_lg_amount"], 30)
    createTable("moneyflow_elg", ["buy_elg_amount", "sell_elg_amount"], 30)
    createTable("moneyflow_mf", ["net_mf_amount"],30)
    for i in range(rows-1):
        i=i+1
        print(sheet.cell_value(i, 0))
        endDate = date(sheet.cell_value(i, 0))
        startDate = getTradeDate(endDate, 30)
        try:
            df = pro.moneyflow(ts_code=sheet.cell_value(i, 1), start_date=startDate, end_date=endDate)
            insertDate("moneyflow_sm", sheet.cell_value(i, 1), ["buy_sm_amount", "sell_sm_amount"], df, 30)
            insertDate("moneyflow_md", sheet.cell_value(i, 1), ["buy_md_amount", "sell_md_amount"], df, 30)
            insertDate("moneyflow_lg", sheet.cell_value(i, 1), ["buy_lg_amount", "sell_lg_amount"], df, 30)
            insertDate("moneyflow_elg", sheet.cell_value(i, 1), ["buy_elg_amount", "sell_elg_amount"], df, 30)
            insertDate("moneyflow_mf", sheet.cell_value(i, 1), ["net_mf_amount"], df, 30)
        except Exception as aa:
            print(aa)
        time.sleep(1)

#df = pro.daily(ts_code='603189.SH', start_date=date, end_date="20200701")
#df = pro.moneyflow(ts_code='603189.SH', start_date=date, end_date="20200701")
#df = ts.get_tick_data('600848',date='2018-12-12',src='tt')
#df.head(10)
#df = pro.top10_floatholders(ts_code='603189.SH', start_date=date, end_date="20200701")
#df = pro.daily_basic(ts_code='', trade_date='20180726', fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb')

getMoneyflow()#资金
#df = pro.stk_holdertrade(ts_code='002693.SZ')

#print(df)