import requests
import os
import json
import pandas as pd
import numpy as np
import re
import general_analyze as ga
import tkinter
#定义账号数据类型
Account_list = pd.DataFrame(columns = ("seller_roleid","seller_name","price","first_onsale_price","area_name",
                                       "collect_num","key_num","general_value","description"))
PATH = "data/Account_tmp.txt"

def Download(url):
    head = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
    }
    return requests.get(url, headers=head, timeout=60)

#提取出所有武将信息
#对每个账号信息的解析字符串进行处理
def AccountSolve(Account_info):
    Account_info = Account_info["equip"]
    global Account_list
    value_text = Account_info["equip_desc"]  #包含账号价值的字符串
    hero_value,key_num,description = ga.general_value(value_text)
    tmpAccount = pd.DataFrame([[Account_info["game_ordersn"], #用户ID
                                Account_info["seller_name"], #用户名
                                int(Account_info["price"]) / 100,   #价格(元)
                                int(Account_info["first_onsale_price"]) / 100, #首次上架价格
                                Account_info["area_name"], #目前位于哪个游戏区
                                Account_info["collect_num"], #收藏人数
                                key_num,
                                hero_value,
                                description,
                               ]],
                              columns = ("seller_roleid","seller_name","price","first_onsale_price","area_name",
                                         "collect_num","key_num","general_value","description"))
    #Account_list = Account_list.append(tmpAccount,ignore_index = True)
    tmpAccount.to_csv(PATH,mode = 'a',index = True,header=False)
AttributeIndex = {}
hero_id_state = {1:"弓",2:"步",3:"骑"}
hero_id_country = {1:"汉",2:"魏",3:"蜀",4:"吴",5:"群"}
#获取账号的全部信息并且保存在向量中
def Get_Hero_Skill_Num(Account_info,Accountmat):
    global AttributeIndex
    yu_fu = re.search("\\\"yuan_bao\\\":([^,]*)",Account_info).group(1)
    jiang_ling = re.search("\\\"jiang_ling\\\":([^,]*)",Account_info).group(1)
    hufu = re.search("\\\"hufu\\\":([^,]*)",Account_info).group(1)
    honor = re.search("\\\"honor\\\":([^}]*)",Account_info).group(1)
    Accountmat[int(AttributeIndex['yuan_bao'])] = int(yu_fu)
    Accountmat[int(AttributeIndex['jiang_ling'])] = int(jiang_ling)
    Accountmat[int(AttributeIndex['hufu'])] = int(hufu)
    Accountmat[int(AttributeIndex['honor'])] = int(honor)
    Hero_List = re.findall("{\\\"hit_range[^}]*}", Account_info)
    for Hero in Hero_List:
        quality = re.search("\\\"quality\\\":([^,]*)", Hero).group(1)
        if int(quality) != 5: continue  # 不考虑非五星武将
        name = re.search("\\\"name\\\":([^,]*)", Hero).group(1)
        name = name.strip(' ').strip('"')
        name = name.encode('utf-8').decode('unicode_escape')  # 姓名
        hero_state = re.search("\\\"hero_type\\\":([^,]*)", Hero).group(1)  # 步骑弓状态
        hero_state = hero_id_state[int(hero_state)]
        hero_country = re.search("\\\"country\\\":([^,]*)", Hero).group(1)  # 国家
        hero_country = hero_id_country[int(hero_country)]
        advance_num = re.search("\\\"advance_num\\\":([^,]*)", Hero).group(1) #进阶状态
        if name != '侍卫':  # 侍卫都一样,其他的需要区分
            name = hero_country + hero_state + name  # 综合状态的姓名,赵云->蜀步赵云
        if name in AttributeIndex:
            Accountmat[int(AttributeIndex[name])] += int(advance_num) + 1
    Skill_List = re.findall("{\\\"skill_type[^}]*}", Account_info)
    for Skill in Skill_List:
        name = re.search("\\\"name\\\":([^,]*)", Skill).group(1)
        name = name.strip(' ').strip('"')
        name = name.encode('utf-8').decode('unicode_escape')  # 姓名
        if name in AttributeIndex:
            Accountmat[int(AttributeIndex[name])] = 1

#获取每个账号的属性
def Account_analyze(Account_info):
    global AttributeIndex
    Accountmat = np.zeros((len(AttributeIndex)))
    Accountmat = Accountmat.tolist()
    Account_info = Account_info["equip"]
    Accountmat[AttributeIndex["price"]] = int(Account_info["price"]) / 100
    Get_Hero_Skill_Num(Account_info["equip_desc"],Accountmat)
    f = open(PATH, 'at')
    for i in Accountmat:
        f.write(str(i) + ' ')
    f.write('\n')
    f.close()
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
    #print(datas["ordersn"])
    html_post = requests.post(pageurl,data = datas,headers = head)
    if html_post:
        Account_analyze(json.loads(html_post.text))

#取出每页的账号id并处理
def Pagework(page_info):
    #print('这页共有%d个武将' % len(page_info['result']))
    for tmp in page_info['result']:
        id = tmp['game_ordersn']
        Accounturl = "https://stzb.cbg.163.com/cgi/mweb/equip/1/%(name)s?view_loc=equip_list" % {'name':id}
        pageurl = "https://stzb.cbg.163.com/cgi/api/get_equip_detail"
        PostAccount(pageurl,id,Accounturl)

def startload(pagestart,pageend):
    Account_list.to_csv(PATH, mode='a', index=True)
    for now_page in range(int(pagestart), int(pageend) + 1):
        url = "https://stzb.cbg.163.com/cgi/api/query?view_loc=equip_list&platform_type=1&order_by=selling_time%20DESC&page=" + str(
            now_page)
        html = Download(url)
        #print('当前正在第%d页寻找' % now_page)
        if (html):
            Pagework(json.loads(html.text))

#获取属性集
def Get_Attribute():
    fr = open('data/Attribute_Set.txt')
    AttributeIndex = {}
    for line in fr.readlines():
        curLine = line.strip().split('\t')
        AttributeIndex[curLine[0]] = curLine[1]
    AttributeIndex['price'] = len(AttributeIndex)
    return AttributeIndex
#进入ios账号的主页并且动态获取每个页面包含账号的id
def main():
    global AttributeIndex
    AttributeIndex = Get_Attribute()
    pagestart = int(input('输入你想从哪页开始找'))
    pageend = int(input('输入你想到哪页结束'))
    for now_page in range(pagestart,pageend + 1):
        url = "https://stzb.cbg.163.com/cgi/api/query?view_loc=equip_list&platform_type=1&order_by=selling_time%20DESC&page=" + str(now_page)
        html = Download(url)
        print('当前正在第%d页寻找' % now_page)
        if(html):
            Pagework(json.loads(html.text))

if __name__ == '__main__':
    main()

