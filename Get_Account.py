import requests
import os
import json
import pandas as pd
import numpy as np

#定义账号数据类型
Account_list = pd.DataFrame(columns = ("seller_roleid","seller_name","price","first_onsale_price","collect_num"))


def Download(url):
    head = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
    }
    return requests.get(url, headers=head, timeout=60)

#对每个账号信息的解析字符串进行处理
def AccountSolve(Account_info):
    Account_info = Account_info["equip"]
    global Account_list
    tmpAccount = pd.DataFrame([[Account_info["seller_roleid"], #用户ID
                                Account_info["seller_name"], #用户名
                                int(Account_info["price"]) / 100,   #价格(元)
                                int(Account_info["first_onsale_price"]) / 100, #首次上架价格
                                Account_info["area_name"], #目前位于哪个游戏区
                                Account_info["collect_num"], #收藏人数
                               ]],
                              columns = ("seller_roleid","seller_name","price","first_onsale_price","area_name",
                                         "collect_num"))
    Account_list = Account_list.append(tmpAccount,ignore_index = True)



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
        AccountSolve(json.loads(html_post.text))

#取出每页的账号id并处理
def Pagework(page_info):
    print('这页共有%d个武将' % len(page_info['result']))
    for tmp in page_info['result']:
        id = tmp['game_ordersn']
        Accounturl = "https://stzb.cbg.163.com/cgi/mweb/equip/1/%(name)s?view_loc=equip_list" % {'name':id}
        pageurl = "https://stzb.cbg.163.com/cgi/api/get_equip_detail"
        PostAccount(pageurl,id,Accounturl)

#进入ios账号的主页并且动态获取每个页面包含账号的id
def main():
    page = int(input('输入你想找多少页'))
    #Account_list.info()
    for now_page in range(1,page + 1):
        url = "https://stzb.cbg.163.com/cgi/api/query?view_loc=equip_list&platform_type=1&order_by=selling_time%20DESC&page=" + str(now_page)
        html = Download(url)
        if(html):
            Pagework(json.loads(html.text))
    print(Account_list.head(15))
    Account_list.to_excel("./1.xlsx")

if __name__ == '__main__':
    main()

