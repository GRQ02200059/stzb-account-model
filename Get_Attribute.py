#获取属性集
import requests
import os
import json
import pandas as pd
import numpy as np
import re
import tkinter

def Download(url):
    head = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
    }
    return requests.get(url, headers=head, timeout=60)

AttributeIndex = {}
AttributeNum = 0
#属性集的初始化
def AttributeInit():
    global AttributeNum
    AttributeNum = -1
    AttributeNum += 1;AttributeIndex['yuan_bao'] = int(AttributeNum)  #玉府
    AttributeNum += 1;AttributeIndex['jiang_ling'] = int(AttributeNum) #将令
    AttributeNum += 1;AttributeIndex['hufu'] = int(AttributeNum) #虎符
    AttributeNum += 1;AttributeIndex['honor'] = int(AttributeNum) #荣誉

#对属性集的完善
hero_id_state = {1:"弓",2:"步",3:"骑"}
hero_id_country = {1:"汉",2:"魏",3:"蜀",4:"吴",5:"群"}
#获取武将组
def Attribute_Hero(Account_info):
    global AttributeNum
    Hero_List = re.findall("{\\\"hit_range[^}]*}", Account_info)
    for Hero in Hero_List:
        quality = re.search("\\\"quality\\\":([^,]*)", Hero).group(1)
        if int(quality) != 5: continue #不考虑非五星武将
        name = re.search("\\\"name\\\":([^,]*)", Hero).group(1)
        name = name.strip(' ').strip('"')
        name = name.encode('utf-8').decode('unicode_escape') #姓名
        hero_state = re.search("\\\"hero_type\\\":([^,]*)", Hero).group(1) #步骑弓状态
        hero_state = hero_id_state[int(hero_state)]
        hero_country = re.search("\\\"country\\\":([^,]*)", Hero).group(1)  #国家
        hero_country = hero_id_country[int(hero_country)]
        if name != '侍卫': #侍卫都一样,其他的需要区分
            name = hero_country + hero_state + name #综合状态的姓名,赵云->蜀步赵云
        if name not in AttributeIndex:
            AttributeNum += 1
            AttributeIndex[name] = AttributeNum
#获取技能组
def Attribute_Skill(Account_info):
    global AttributeNum
    Skill_List = re.findall("{\\\"skill_type[^}]*}", Account_info)
    for Skill in Skill_List:
        name = re.search("\\\"name\\\":([^,]*)", Skill).group(1)
        name = name.strip(' ').strip('"')
        name = name.encode('utf-8').decode('unicode_escape')  # 姓名
        #print(name)
        if name not in AttributeIndex:
            AttributeNum += 1
            AttributeIndex[name] = AttributeNum

def AttributeSolve(Account_info):
    Account_info = Account_info["equip"]
    Account_info = Account_info["equip_desc"]
    Attribute_Hero(Account_info)
    Attribute_Skill(Account_info)


#通过将每个id发送给服务器的方式 获取每个账号的详细信息
def PostAccount(pageurl,Accountid,Accounturl):
    head = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Referer": Accounturl
    }
    datas = {
        "serverid":"1",
        "ordersn":Accountid,
        "view_loc":"equip_list",
    }
    datas["ordersn"] = Accountid
    html_post = requests.post(pageurl,data = datas,headers = head)
    if html_post:
        AttributeSolve(json.loads(html_post.text))

#取出每页的账号id并处理
def Pagework(page_info):
    #print('这页共有%d个武将' % len(page_info['result']))
    for tmp in page_info['result']:
        id = tmp['game_ordersn']
        Accounturl = "https://stzb.cbg.163.com/cgi/mweb/equip/1/%(name)s?view_loc=equip_list" % {'name':id}
        pageurl = "https://stzb.cbg.163.com/cgi/api/get_equip_detail"
        PostAccount(pageurl,id,Accounturl)

def startload(pagestart,pageend):
    for now_page in range(int(pagestart), int(pageend) + 1):
        url = "https://stzb.cbg.163.com/cgi/api/query?view_loc=equip_list&platform_type=1&order_by=selling_time%20DESC&page=" + str(
            now_page)
        html = Download(url)
        if (html):
            Pagework(json.loads(html.text))


#进入ios账号的主页并且动态获取每个页面包含账号的id
def main():
    pagestart = int(input('输入你想从哪页开始找'))
    pageend = int(input('输入你想到哪页结束'))
    AttributeInit()
    for now_page in range(pagestart,pageend + 1):
        url = "https://stzb.cbg.163.com/cgi/api/query?view_loc=equip_list&platform_type=1&order_by=selling_time%20DESC&page=" + str(now_page)
        html = Download(url)
        print('当前正在第%d页寻找' % now_page)
        if(html):
            Pagework(json.loads(html.text))
    f = open('data/Attribute_Set.txt', 'w')
    for key in AttributeIndex: #输出获取到的属性集
        f.write(str(key) + '\t' + str(AttributeIndex[key]) + '\n')
    f.close()

if __name__ == '__main__':
    main()

