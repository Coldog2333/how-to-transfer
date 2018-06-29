# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 14:21:16 2018

@author: HP
"""
#一些cookies常量
Spots=dict()
Spots['广州']='%u5E7F%u5DDE%2CGZQ'
Spots['端州']='%u7AEF%u5DDE%2CWZQ'
Spots['广州南']='%u5E7F%u5DDE%u5357%2CIZQ'
Spots['肇庆东']='%u8087%u5E86%u4E1C%2CFCQ'
Spots['鼎湖东']='%u9F0E%u6E56%u4E1C%2CUWQ'

from splinter.browser import Browser
from time import sleep
import datetime

def find_all(string,substr):
    Index=[]
    for i in range(len(string)):
        if string[i]==substr:
            Index.append(i)
    return Index
    
#t1,t2为字符串  'xx:xx'
def calcmin(t1,t2):
    if t1>t2:
        return -1
    elif t1==t2:
        return 0
    else:
        #距离00：00的分钟数之差
        T1=600*eval(t1[0])+60*eval(t1[1])+10*eval(t1[3])+eval(t1[4])
        T2=600*eval(t2[0])+60*eval(t2[1])+10*eval(t2[3])+eval(t2[4])
        return T2-T1

def getInfo(x,Time,Start,End):
    x.cookies.add({"_jc_save_fromDate":Time})
    x.cookies.add({"_jc_save_fromStation":Spots[Start]})
    x.cookies.add({"_jc_save_toStation":Spots[End]})
    x.cookies.all()
    x.reload()
    sleep(1)
    x.find_by_text("查询").click()

    sleep(1)
    x.find_by_text("GC-高铁/城际").click()
    x.find_by_text("D-动车").click()

    query_left_table=x.find_by_xpath(r'//tbody[@id="queryLeftTable"]/tr/td')
    #cds_txt=x.find_by_xpath('//div[@class="cds"]')   #时间
    #cdz_txt=x.find_by_xpath('//div[@class="cdz"]')   #站点
    #num_txt=x.find_by_xpath('//div[@class="train"]') #车次
    #ls_txt=x.find_by_xpath('//div[@class="ls"]')     #所需时间
    #query_left_table=x.find_by_id('queryLeftTable')
    Info=[]    #important imformations
    for i in range(0,len(query_left_table),13):
        temp=dict()
        txt=query_left_table[i].text
        Index=find_all(txt,'\n')
        temp['No']=txt[:Index[0]]
        temp['start_station']=txt[Index[0]+1:Index[1]]
        temp['end_station']=txt[Index[1]+1:Index[2]] 
        temp['start_time']=txt[Index[2]+1:Index[3]] 
        if(temp['start_time'].find('-')>=0):
            continue
        temp['end_time']=txt[Index[3]+1:Index[4]] 
        temp['cost_time']=txt[Index[4]+1:Index[5]] 
        for j in range(3):
            temp['seat_first']=query_left_table[i+2].text
            temp['seat_second']=query_left_table[i+3].text
            temp['seat_none']=query_left_table[i+10].text
        Info.append(temp)
    return Info

def main(From,To,MinTime,MaxTime,Start_flag=0):
    #鲁棒
    if(Start_flag=='0' or Start_flag=='今天' or Start_flag=='today'):
        flag=0
    elif(Start_flag=='1' or Start_flag=='明天' or Start_flag=='tomorrow'):
        flag=1
    
    if(From=='广州南'):
        From_to='肇庆东'
        To_from='鼎湖东'
    elif(From=='端州'):
        From_to='鼎湖东'
        To_from='肇庆东'
    MinTime=int(MinTime)
    MaxTime=int(MaxTime)
    
    url="https://kyfw.12306.cn/otn/leftTicket/init"
    x=Browser(driver_name="chrome")
    x.visit(url)

    #因为每次搭车回家都是出发前才买票，所以购票时间默认为当天
    #debug期间一般是深夜所以day+1
    Year=str(datetime.datetime.now().year)
    if datetime.datetime.now().month>=10:
        Month=str(datetime.datetime.now().month)
    else:
        Month=''.join(['0',str(datetime.datetime.now().month)])
        Day=str(datetime.datetime.now().day+flag)
        Time=''.join([Year,'-',Month,'-',Day])    

    Info_1=getInfo(x,Time,From,From_to)
    Info_2=getInfo(x,Time,To_from,To)


    count=0
    for i in range(len(Info_1)):
        for j in range(len(Info_2)):
            #如果车站不对
            if(Info_1[i]['start_station']!=From or Info_1[i]['end_station']!=From_to):
                continue
            elif(Info_2[j]['start_station']!=To_from or Info_2[j]['end_station']!=To):
                continue
            #如果接驳时间少于15mins或等待时间大于45mins
            elif(calcmin(Info_1[i]['end_time'],Info_2[j]['start_time'])<MinTime or calcmin(Info_1[i]['end_time'],Info_2[j]['start_time'])>=MaxTime):
                continue
            else:
                print('[',Info_1[i]['No'],'->',Info_2[j]['No'],']  ',Info_1[i]['start_time'],'~',Info_2[j]['end_time'],'  接驳时间：',calcmin(Info_1[i]['end_time'],Info_2[j]['start_time']),'mins',sep='')
                count+=1

    if count==0:
        print('没有相应的乘车方案。')
    else:
        print('共有%d个乘车方案。' % count)


def command1():
    mint=input('你需要多少接驳时间？  ')
    maxt=input('你能容忍的最大等待时间？  ')
    Time=input('出发时间(今天:0, 明天:1)  ')
    main('广州南','端州',mint,maxt,Time)
    
def command2():
    mint=input('你需要多少接驳时间？  ')
    maxt=input('你能容忍的最大等待时间？  ')
    Time=input('出发时间(今天:0, 明天:1)  ')
    main('端州','广州南',mint,maxt,Time)


from tkinter import *
win = Tk()  #定义一个窗体  
win.title('Give you an advise to transfer')    #定义窗体标题  
win.geometry('400x150')     #定义窗体的大小
btn1 = Button(win, text='广州南→端州', command=command1, width=20, height=3).pack()
btn2 = Button(win, text='端州→广州南', command=command2, width=20, height=3).pack()
#Button(win, text='退出',command=win.quit, width=20, height=3).pack()
mainloop()

