#!/usr/bin/env python          
# -*- encoding: utf-8 -*- 

from requests import get, post
from time import perf_counter, sleep
import json
import time
import random

api_url = "http://fyxt.nytdc.edu.cn:12078/"

your_tel = 114514
your_id = 1919810

def get_dname() -> str:
    '''
    @description : 获取学校名称
    @return : 学校名称
    '''
    name_json = get(url=api_url + "api/getDname?dguid=61").json()
    if (name_json["msg"]=="成功"):
        school_name = name_json["data"]["dname"]
        print("学校名称："+school_name)
    else:
        print("Get school name failed.")
        school_name = False
    return school_name

def veri_user_token(user_token):
    """
    @description : 验证用户token
    @return : Bool
    """
    user_token_headers = {'x-user-token': user_token, 'x-requested-with': "XMLHttpRequest"}
    veri_response_json = get(url = api_url + "tApi/verifyToken", headers = user_token_headers).json()
    if veri_response_json["msg"] == "成功":
        print("token验证成功")
        return True
    else:
        print("token验证失败")
        return False

def get_new_checkin(user_token):
    """
    @description : 获取上一次登记的数据
    @return : 反序列化的json数据
    """
    user_token_headers = {'x-user-token': user_token, 'x-requested-with': "XMLHttpRequest"}
    veri_response_json = get(url = api_url + "tApi/getNewCheckin", headers = user_token_headers).json()
    if veri_response_json["msg"] == "成功":
        print("getNewCheckin成功")
        return veri_response_json
    else:
        print("getNewCheckin失败")

def get_latest_checkin(user_token, uuid):
    """
    @description : 获取某一次登记的数据
    @params : 
        user_token : 用户token
        uuid : 要查看的uuid
    @return : 反序列化的json数据
    """
    user_token_headers = {'x-user-token': user_token, 'x-requested-with': "XMLHttpRequest"}
    get_checkin_url = api_url + "tApi/getCheckin?unitguid=" + uuid 
    response_json = get(url = get_checkin_url, headers = user_token_headers).json()
    return response_json

def get_token(tel, id):
    """
    @description : 获取token
    @params : 
        tel : 手机号
        id  : 学号
    @return : user_token 用户token
    """
    if (get_dname() == "南邮通达学院"):
        stu_url = api_url + "api/login?mobile="+ str(tel) + "&code=" + str(id) + "&openid=&dguid=61"
        stu_json = get(url=stu_url).json()
        user_token = stu_json["data"]["token"]
        return user_token

def auto_checkin(tel, id):
    '''
    @description: 自动签到
    @params :
        tel : 手机号
        id  : 学号
    @return 是否签到成功
    '''    
    user_token = get_token(tel, id)
    if(veri_user_token(user_token)):
        last_upload_json = get_new_checkin(user_token)
        print(str(last_upload_json))
        # veri_user_token(user_token)
        is_inoculation = lambda x: "否" if x=="未接种" else "是"
        is_secondrecovery = lambda x: "否" if x=="未二次感染" else "是"
        is_recovery = lambda x: "否" if x[0]=="未" else "是"
        checkin_list = {
            "date" : str(time.strftime("%Y-%m-%d", time.localtime())), 
            "fromWhere": str(last_upload_json["data"]["province"]) + str(last_upload_json["data"]["city"]),
            "province": str(last_upload_json["data"]["province"]),
            "city": str(last_upload_json["data"]["city"]),
            "county": str(last_upload_json["data"]["county"]),
            "tempnum1":"36." + str(random.randint(0,9)),
            "isinoculation": str(last_upload_json["data"]["isinoculation"]),
            "isinoculation1": str(is_inoculation(last_upload_json["data"]["inoculationtime1"])),
            "isinoculation2": str(is_inoculation(last_upload_json["data"]["inoculationtime2"])),
            "issecondrecovery": str(is_secondrecovery(last_upload_json["data"]["secondrecoverytime"])),
            "isinfectcovid": str(last_upload_json["data"]["isinfectcovid"]),
            "isrecovery": str(is_recovery(last_upload_json["data"]["recoverytime"])),
            "issecondinfect": str(last_upload_json["data"]["issecondinfect"]),
            "isinoculation3": str(is_inoculation(last_upload_json["data"]["inoculationtime3"])),
            "isinoculation4": str(is_inoculation(last_upload_json["data"]["inoculationtime4"])),
            "isbasedisease": str(last_upload_json["data"]["isbasedisease"]),
            "inoculationtype1": str(last_upload_json["data"]["inoculationtype1"]),
            "inoculationtype2": str(last_upload_json["data"]["inoculationtype2"]),
            "inoculationtype3": str(last_upload_json["data"]["inoculationtype3"]),
            "inoculationtype4": str(last_upload_json["data"]["inoculationtype4"]),
            "inoculationtime1": str(last_upload_json["data"]["inoculationtime1"]),
            "inoculationtime2": str(last_upload_json["data"]["inoculationtime2"]),
            "inoculationtime3": str(last_upload_json["data"]["inoculationtime3"]),
            "inoculationtime4": str(last_upload_json["data"]["inoculationtime4"]),
            "infecttime": str(last_upload_json["data"]["infecttime"]),
            "recoverytime": str(last_upload_json["data"]["recoverytime"]),
            "secondinfecttime": str(last_upload_json["data"]["secondinfecttime"]),
            "secondrecoverytime": str(last_upload_json["data"]["secondrecoverytime"]),
            "istemp": str(last_upload_json["data"]["istemp"])
            }
        
        print(checkin_list)
        post_headers = {'x-user-token': user_token, 'x-requested-with': "XMLHttpRequest"}
        respond_data_json = post(url = api_url + "tApi/postCheckin", data = checkin_list, headers = post_headers).json()
        data_uuid = respond_data_json["data"]
        veri_user_token(user_token)
        latest_checkin_json = get_latest_checkin(user_token, data_uuid)
        veri_user_token(user_token)
        print(str(latest_checkin_json))
        if latest_checkin_json["data"]["pass"]=="通过":
            return True
        else:
            return False

if(auto_checkin(your_tel, your_id)):
    print("签到成功！")