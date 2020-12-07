import requests
import http.cookiejar
from bs4 import BeautifulSoup
from lxml import etree
import re
import xlwt
import os
import xlrd
from xlutils.copy import copy
import tushare as ts

url = "http://www.bzneixian.cn/?id="
path = "black"
filePath = path+'\codes.xls'

ts.set_token('29fa15c6fb00b315153cab6aa695a011ae78cc59752d90548272dfd8')
pro = ts.pro_api()

#---------------------------sesssion----------------------------------#
session = requests.Session()
session.cookies = http.cookiejar.LWPCookieJar("cookie")

agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
headers = {
    "Host": "59.211.219.71",
    "Origin": "http://59.211.219.71",
    "Referer": "http://59.211.219.71/sharedportal/pages/government_data/government_data_catalog.html",
    "Content-Type": "application/json;charset=UTF-8",
    'User-Agent': agent
}

result =session.get("http://www.bzneixian.cn")
if result.status_code == 200:
    print("session Success!")
else:
    print(result.status_code)
session.cookies.save(ignore_discard = True,ignore_expires = True)

isExists = os.path.exists(path)
if not isExists:
    os.makedirs(path)
    print("makedirs")

def write_excel_xls_append(path, value):
    index = len(value)  # 获取需要写入数据的行数
    workbook = xlrd.open_workbook(path)  # 打开工作簿
    sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
    worksheet = workbook.sheet_by_name(sheets[0])  # 获取工作簿中所有表格中的的第一个表格
    rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
    new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
    new_worksheet = new_workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            new_worksheet.write(i+rows_old, j, value[i][j])  # 追加写入数据，注意是从i+rows_old行开始写入
    new_workbook.save(path)  # 保存工作簿


#GetCodes

index = 0

for i in range(3811,4200):
    result =session.post(url + str(i))
    if result.status_code == 200:
        soup = BeautifulSoup(result.content, features='html.parser')
        title = str(soup.title)
        if title.find("盘后票完整") >= 0 or title.find("公布昨日") >= 0 or title.find("盘后票") >= 0:
            #/html/body/div[2]/div[1]/div/div[1]/header/div[1]/span[2]/text()
            selector = etree.HTML(result.content)
            des = selector.xpath('//*[@id="divMain"]/div/h2/text()')
            if len(des) == 0:
                des = selector.xpath('/html/body/div[2]/div[1]/div/div[1]/header/h1/text()')

            ret = selector.xpath('//*[@id="divMain"]/div/h4/text()')

            if len(ret) == 0:
                ret = selector.xpath('/html/body/div[2]/div[1]/div/div[1]/header/div[1]/span[2]/text()')

            pattern = re.compile(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
            date = str(pattern.findall(str(ret))[0])
            print(date)
            code = ""
            for item in soup.find_all("strong"):
                code = code + str(item.get_text())
            '''if des.find("午") >= 0:
                #code = selector.xpath("/html/body/div[2]/div[1]/div/div[1]/article/p[2]/text()")
                code = ""
                for item in soup.find_all("strong"):
                    code = code+str(item.get_text())
            else:
                code = selector.xpath("/html/body/div[2]/div[1]/div/div[1]/article/p[2]/strong/span/text()")'''
            codeList = re.findall(r"[0-9]{6}",str(code))
            for code in codeList:
                if code != "000000":
                    if code[0] == "6":
                        code = code[0:6] + ".SH"
                    else:
                        code = code[0:6] + ".SZ"
                    minDate = date[0:10]
                    minDate = minDate.replace("-", "")
                    try:
                        print(code)
                        print(minDate)
                        df = pro.daily(ts_code=code, start_date=minDate, end_date=minDate)
                        c_len = df.shape[0]
                        print(df)
                    except Exception as aa:
                        print(aa)
                        print('No DATA Code: ' + str(i))
                        continue
                    for j in range(c_len):
                        resu0 = list(df.loc[c_len - 1 - j])
                        resu = []
                        for k in range(len(resu0)):
                            if str(resu0[k]) == 'nan':
                                resu.append(-1)
                            else:
                                resu.append(resu0[k])

                    write_excel_xls_append(filePath,[[date,code,des,resu[8]]])

            isExists = os.path.exists(path)
            if not isExists:
                os.makedirs(path)
                print("makedirs")




    else:
        print(result.status_code)
    print(i)

#for i in range(0, 3000):
