from requests import get, post
from time import perf_counter, sleep
import json
import time
import random
import requests

api_url = "http://fyxt.nytdc.edu.cn:12078/"

def get_dname() -> str:
    name_json = get(url=api_url + "api/getDname?dguid=61").json()
    if (name_json["msg"]=="成功"):
        school_name = name_json["data"]["dname"]
        print("学校名称："+school_name)
    else:
        print("Get school name failed.")
        school_name = False
    return school_name

def veri_user_token(user_token):
    user_token_headers = {'x-user-token': user_token, 'x-requested-with': "XMLHttpRequest"}
    veri_response_json = get(url = api_url + "tApi/verifyToken", headers = user_token_headers).json()
    if veri_response_json["msg"] == "成功":
        print("token验证成功")
        return True
    else:
        print("token验证失败")
        return False
        

def get_new_checkin(user_token):
    user_token_headers = {'x-user-token': user_token, 'x-requested-with': "XMLHttpRequest"}
    veri_response_json = get(url = api_url + "tApi/getNewCheckin", headers = user_token_headers).json()
    if veri_response_json["msg"] == "成功":
        print("getNewCheckin成功")
        return veri_response_json
    else:
        print("getNewCheckin失败")

def get_latest_checkin(user_token, uuid):
    user_token_headers = {'x-user-token': user_token, 'x-requested-with': "XMLHttpRequest"}
    get_checkin_url = api_url + "tApi/getCheckin?unitguid=" + uuid 
    response_json = get(url = get_checkin_url, headers = user_token_headers).json()
    return response_json


def auto_checkin(tel, id):
    if (get_dname() == "南邮通达学院"):
        stu_url = api_url + "api/login?mobile="+ str(tel) + "&code=" + str(id) + "&openid=&dguid=61"
        stu_json = get(url=stu_url).json()
        user_token = stu_json["data"]["token"]
        #print("Token:"+user_token)
        veri_user_token(user_token)
        last_upload_json = get_new_checkin(user_token)
        print(str(last_upload_json))
        veri_user_token(user_token)
        checkin_list = {
            "date" : str(time.strftime("%Y-%m-%d", time.localtime())), 
            "ishubei": "否",
            "fromWhere":"江苏省扬州市邗江区",
            "province":"江苏省",
            "city":"扬州市",
            "county":"邗江区",
            "tempnum1":"36." + str(random.randint(0,9)),
            "tempnum2":"36." + str(random.randint(0,9)),
            "tempnum3":"36." + str(random.randint(0,9)),
            "isgohubei":"否",
            "iscontacthubei":"否",
            "iscontactpatient":"否",
            "istemp":"否",
            "isfamilypatient":"否",
            "isabroad":"否",
            "isfamilyhubei":"正常"
            }
        print(checkin_list)
        post_headers = {'x-user-token': user_token, 'x-requested-with': "XMLHttpRequest"}
        respond_data_json = post(url = api_url + "tApi/postCheckin", data = checkin_list, headers = post_headers).json()
        # requests.post(url = "http://127.0.0.1:3000/", data = checkin_list)
        data_uuid = respond_data_json["data"]
        veri_user_token(user_token)
        latest_checkin_json = get_latest_checkin(user_token, data_uuid)
        veri_user_token(user_token)
        print(str(latest_checkin_json))
        if latest_checkin_json["data"]["pass"]=="通过":
            return True
        else:
            return False

if auto_checkin(__这边填你的手机号__, __这边填你的学号__):
    print("签到成功")

#如何使用
#将上面的手机号和学号修改好，例如auto_checkin(12345678901, 21122222)
#然后需要安装一个python环境并配置好环境变量
#然后在当前目录下打开cmd
#输入python checkin.py
#查看输出信息为签到成功的话就成功了