import os
import re
from turtle import position
import app
import time
import json
import random
import string
import smtplib
from datetime import datetime
from copy import deepcopy
from Base.Enumtype import *
from Base.models import *
from typing import Dict,List,Tuple
from flask_login import current_user
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.image import MIMEImage
def forma(s: str) -> str:
    return s.replace('\\', '/').replace('//', '/').split('/')[-1]


def emailChanel(sender, receiverList, user, emailPwd, smtpServer, commonPort, emailTitle, htmlPath=None, attachPathList=None, text=None):
    multiPart = MIMEMultipart()
    multiPart['From'] = sender
    multiPart['To'] = ','.join(receiverList)
    subject = emailTitle
    multiPart['Subject'] = Header(subject, "utf-8")
    if text == None and htmlPath == None:
        return {"status": False, "message": "请传入邮件正文"}
    # 正文/html
    if htmlPath != None:
        if os.path.isfile(htmlPath):
            if os.path.exists(htmlPath):
                pass
            else:
                return {"status":False,"message":"htmlPath not exist"}
        else:
            return {"status":False,"message":"html path is not file.."}
        emailBody = MIMEText(_text=open(htmlPath, 'rb').read(), _subtype='html', _charset="utf-8")
        multiPart.attach(emailBody)
    # 正文/text
    elif text != None:
        if isinstance(text, str):
            multiPart.attach(MIMEText(text, 'plain', 'utf-8'))
        else:
            return {"status":False,"message":f"expected type is str,but get {type(text).__name__}"}

    # 附件
    if attachPathList != None:
        if isinstance(attachPathList, list):
            for attachPath in attachPathList:
                if os.path.exists(attachPath):
                    pass
                else:
                    return {"status":False,"message":"attachPath not exist"}
        else:
            return {"status":False,\
                "message":"expected type is list,but get {}".format(type(attachPathList).__name__)}
        for attachPath in attachPathList:
            if os.path.splitext(attachPath)[-1] in [".png", ".jpg", ".webp", ".jpeg"]:
                msg = MIMEImage(open(attachPath, 'rb').read(), _subtype='octet-stream')
                msg.add_header('Content-Disposition', 'attachment', filename=forma(attachPath))
                multiPart.attach(msg)
            else:
                #if os.path.splitext(attachPath)[-1] == ".log":
                # 第二种写法
                msg = MIMEText(open(attachPath, 'rb').read(), 'base64', 'utf-8')
                msg["Content-Type"] = 'application/octet-stream'
                msg["Content-Disposition"] = f'attachment; filename={forma(attachPath)}'
                multiPart.attach(msg)
    smtp = smtplib.SMTP_SSL(smtpServer, commonPort)
    try:
        smtp.login(user, emailPwd)
        smtp.sendmail(sender, receiverList, multiPart.as_string())
    except smtplib.SMTPException as e:
        return {"status": False, "message": repr(e)}
    else:  # 无论是否异常都执行的代码
        try:
            smtp.quit()
            smtp.close()
        except smtplib.SMTPException as e:
            return {"status": False, "message": repr(e)}
        else:
            return {"status": True, "message": "邮件发送成功"}


def send_email(emailTitle: str, receiverList: list, text: str = None, htmlPath: str = None, attachPathList: list = None) -> json:
    if type(receiverList) == str:
        receiverList = [receiverList]
    sender = "1355211477@qq.com"
    user = "1355211477@qq.com"
    emailPwd = 'igcwbddarjdvibgb'
    smtpServer = 'smtp.qq.com'
    commonPort = 465
    return emailChanel(sender, receiverList, user, emailPwd, smtpServer, commonPort, emailTitle, htmlPath, attachPathList, text)


def create_string_number(n):
    """
    生成一串指定位数的字符+数组混合的字符串
    """
    m = random.randint(1, n)
    a = "".join([str(random.randint(0, 9)) for _ in range(m)])
    b = "".join([random.choice(string.ascii_letters) for _ in range(n - m)])
    return ''.join(random.sample(list(a + b), n))


def check_user_pattern(username:str)->Tuple[bool,str]:
    if len(username) < 8 or len(username)>20:
        return (False,"用户名长度不符合要求")
    username_pattern = re.compile("^[0-9a-zA-Z]+$")
    if username_pattern.search(username) is None:
        return (False,"用户名不满足格式要求")
    return (True,"用户名检验完成")


def check_password_pattern(password:str)-> Tuple[bool,str]:
    if len(password)<6 or len(password)>20:
        return (False,"密码长度不符合要求")
    password_pattern = re.compile("^[0-9a-zA-Z_]+$")
    sub = [re.compile("[0-9]"),re.compile("[a-zA-Z]")]
    if password_pattern.search(password) is None:
        return (False,"密码不满足格式要求")
    test = [ i.search(password) is not None for i in sub]
    if sum(test) != len(sub):
        return (False,"密码不满足格式要求")
    return (True,"账号密码满足要求")

def check_email(email:str,verify:str)->Tuple[bool,str]:
    try:
        with open(os.path.join(app.app.static_folder,"verify.json"),"r") as fp:
            pre = json.load(fp)
    except Exception as e:
        print(repr(e))
        return (False,"验证码信息丢失,请联系管理员")
    num = -1
    for i,j in enumerate(pre):
        if j["email"] == email:
            num = i
            break
    if num == -1 or pre[num]["verify"] != verify:
        return (False,"验证码信息错误")
    elif int(time.time()) - pre[num]["time"] >=300:
        return (False,"验证码已过期")
    return (True,"验证码检验正确")

def check_register_data(data:Dict[str,str])->Tuple[bool,str]:
    need = {"email":"没有指定邮箱","verify":"没有输入验证码","username":"未指定用户名","password":"未输入密码"}
    for i in need:
        if i not in data:
            return (False,need[i])
    check = check_email(data["email"],data["verify"])
    if check[0] == False:
        return check
    check = check_user_pattern(data["username"])
    if check[0] == False:
        return check
    check = check_password_pattern(data["password"])
    if check[0] == False:
        return check
    try:
        user = User.get(User.name == data["username"])
    except Exception:
        pass
    else:
        return (False,"该用户名已被使用")
    try:
        user = User.get(User.email == data["email"])
    except Exception as e:
        return (True,"允许注册")
    else:
        return (False,"该邮箱已被人使用")

def search_monster(data:Dict[str,str|List[str]])->Tuple[bool,List[Dict[str,str|bool|int]]|str]:
    need = [Cards.id,Cards.name,Cards.card_type,Monstercards.type,\
        Monstercards.star_number,Monstercards.pendulum_number]
    for i in monster_special._value2member_map_:
        need.append(eval(f"Monstercards.is_{monster_special._value2member_map_[i].name}"))
    condition = list()
    if "card_type" not in data:
        cons = ["type","race","attrib","special","linkmark",\
            "starNumber_min","starMunber_max","PendulumNumber_min","PendulumNumber_max",\
            "atk_min","atk_max","def_min","def_max"]
        for i in cons:
            if i in data:
                return (False,"请求格式不对")
    else:
        if "type" in data:
            if data["type"] not in monster_type._value2member_map_:
                return (False,"请求格式不对")
            condition.append(Monstercards.type == data["type"])
        if "race" in data:
            if data["race"] not in race._value2member_map_:
                return (False,"请求格式不对")
            condition.append(Monstercards.race == data["race"])
        if "attrib" in data:
            if data["attrib"] not in attribute._value2member_map_:
                return (False,"请求格式不对")
            condition.append(Monstercards.attrib == data["attrib"])
        if "special" in data:
            if not isinstance(data["special"],list):
                return (False,"请求格式不对")
            for i in data["special"]:
                if i not in monster_special._value2member_map_:
                    return (False,"请求格式不对")
                condition.append(eval(f"Monstercards.is_{monster_special._value2member_map_[i].name}==True"))
        if "linkmark" in data:
            if not isinstance(data["linkmark"],list):
                return (False,"请求格式不对")
            mark = 0
            for i in data["linkmark"]:
                try:
                    j = int(i)
                except Exception as e:
                    return (False,"请求格式不对")
                if j in linkmark._value2member_map_:
                    mark+=j
                else:
                    return (False,"请求格式不对")
            condition.append(Monstercards.link_mark.bin_and(mark) == mark)
        if "starNumber_min" in data:
            try:
                starNumber_min = int(data["starNumber_min"])
            except Exception as e:
                return (False,"请求格式不对")
            if starNumber_min < 0:
                return (False,"请求格式不对")
            condition.append(Monstercards.star_number>=starNumber_min)
        if "starNumber_max" in data:
            try:
                starNumber_max = int(data["starNumber_max"])
            except Exception as e:
                return (False,"请求格式不对")
            if starNumber_max < 0:
                return (False,"请求格式不对")
            condition.append(Monstercards.star_number<=starNumber_max)
        if "PendulumNumber_min" in data:
            try:
                PendulumNumber_min = int(data["PendulumNumber_min"])
            except Exception as e:
                return (False,"请求格式不对")
            if PendulumNumber_min < 0:
                return (False,"请求格式不对")
            condition.append(Monstercards.pendulum_number>=PendulumNumber_min)
        if "PendulumNumber_max" in data:
            try:
                PendulumNumber_max = int(data["PendulumNumber_max"])
            except Exception as e:
                return (False,"请求格式不对")
            if PendulumNumber_max < 0:
                return (False,"请求格式不对")
            condition.append(Monstercards.pendulum_number<=PendulumNumber_max)
        if "atk_min" in data:
            try:
                atk_min = int(data["atk_min"])
            except Exception as e:
                return (False,"请求格式不对")
            if atk_min < -1:
                return (False,"请求格式不对")
            condition.append(Monstercards._atk>=atk_min)
        if "atk_max" in data:
            try:
                atk_max = int(data["atk_max"])
            except Exception as e:
                return (False,"请求格式不对")
            if atk_max < -1:
                return (False,"请求格式不对")
            condition.append(Monstercards._atk<=atk_max)
        if "def_min" in data:
            try:
                def_min = int(data["def_min"])
            except Exception as e:
                return (False,"请求格式不对")
            if def_min < -1:
                return (False,"请求格式不对")
            condition.append(Monstercards._def>=def_min)
        if "def_max" in data:
            try:
                def_max = int(data["def_max"])
            except Exception as e:
                return (False,"请求格式不对")
            if def_max < -1:
                return (False,"请求格式不对")
            condition.append(Monstercards._def<=def_max)
    if "card_name" in data:
        condition.append(Cards.name.contains(data["card_name"]))
    if "effect" in data:
        condition.append((Monstercards.monster_effect.contains(data["effect"]))|(Monstercards.pendulum_effect.contains(data["effect"])))
    try:
        if len(condition) > 0:
            result = Monstercards.select(*need).join(Cards,on=(Monstercards.cardid == Cards.id))\
            .where(*condition).order_by(Monstercards.star_number.desc(),Monstercards.type.asc()).execute()
        else:
            result = Monstercards.select(*need)\
            .join(Cards,on=(Monstercards.cardid == Cards.id))\
            .order_by(Monstercards.star_number.desc(),Monstercards.type.asc()).execute()
    except Exception as e:
        print(repr(e))
        return (False,"数据库查询出错,请联系系统管理员1355211477@qq.com")
    p = list()
    for i in result:
        j,k = deepcopy(i.__data__),deepcopy(i.cardid.__data__)
        j.update(k)
        j.pop("cardid")
        j["tag"] = [i.type]
        j.pop("type")
        for s in monster_special._value2member_map_:
            j.pop(f"is_{monster_special._value2member_map_[s].name}")
            if eval(f"i.is_{monster_special._value2member_map_[s].name}") == 1:
                if s not in j["tag"]:
                    j["tag"].append(s)
        p.append(j)
    return (True,p)

def search_magic(data:Dict[str,str])->Tuple[bool,List[Dict[str,str|bool|int]]|str]:
    need = [Cards.id,Cards.name,Cards.card_type,Magiccards.type]
    condition = list()
    if "card_type" in data:
        if "type" in data:
            if data["type"] not in magic_type._value2member_map_:
                return (False,"请求格式不对")
            condition.append(Magiccards.type == data["type"])
    else:
        if "type" in data:
            return (False,"请求格式不对")
    if "card_name" in data:
        condition.append(Cards.name.contains(data["card_name"]))
    if "effect" in data:
        condition.append(Magiccards.effect.contains(data["effect"]))
    try:
        if len(condition) > 0:
            result = Magiccards.select(*need).join(Cards,on=(Magiccards.cardid == Cards.id))\
            .where(*condition).order_by(Magiccards.type.desc()).execute()
        else:
            result = Magiccards.select(*need)\
            .join(Cards,on=(Magiccards.cardid == Cards.id)).order_by(Magiccards.type.desc()).execute()
    except Exception as e:
        print(repr(e))
        return (False,"数据库查询出错,请联系系统管理员1355211477@qq.com")
    p = list()
    for i in result:
        j,k = deepcopy(i.__data__),deepcopy(i.cardid.__data__)
        j.update(k)
        j.pop("cardid")
        p.append(j)
    return (True,p)

def search_trap(data:Dict[str,str])->Tuple[bool,List[Dict[str,str|bool|int]]|str]:
    need = [Cards.id,Cards.name,Cards.card_type,Trapcards.type]
    condition = list()
    if "card_type" in data:
        if "type" in data:
            if data["type"] not in trap_type._value2member_map_:
                return (False,"请求格式不对")
            condition.append(Trapcards.type == data["type"])
    else:
        if "type" in data:
            return (False,"请求格式不对")
    if "card_name" in data:
        condition.append(Cards.name.contains(data["card_name"]))
    if "effect" in data:
        condition.append(Trapcards.effect.contains(data["effect"]))
    try:
        if len(condition) > 0:
            result = Trapcards.select(*need).join(Cards,on=(Trapcards.cardid == Cards.id))\
            .where(*condition).order_by(Trapcards.type.desc()).execute()
        else:
            result = Trapcards.select(*need)\
            .join(Cards,on=(Trapcards.cardid == Cards.id)).order_by(Trapcards.type.desc()).execute()
    except Exception as e:
        print(repr(e))
        return (False,"数据库查询出错,请联系系统管理员1355211477@qq.com")
    p = list()
    for i in result:
        j,k = deepcopy(i.__data__),deepcopy(i.cardid.__data__)
        j.update(k)
        j.pop("cardid")
        p.append(j)
    return (True,p)


def read_ydk(path:str)->Dict[int,Dict[int,int]]:
    with open(path,"r",encoding="utf-8") as fp:
        k = fp.readlines()
        temp = {0:dict(),1:dict(),2:dict()}
        num = -1
        for t in k:
            j = t.strip()
            if j == "#main":
                num = 0
            elif j == "#extra":
                num = 1
            elif j == "!side":
                num = 2
            else:
                try:
                    cid = int(j)
                except Exception as e:
                    pass
                else:
                    if num > -1:
                        if cid not in temp[num]:
                            temp[num][cid] = 0
                        temp[num][cid]+=1
    return temp

def insert_new_ydk(name:str,data:Dict[int,Dict[int,int]])->Tuple[bool,str]:
    num = 0
    fin_name = deepcopy(name)
    while True:
        try:
            tmp = Cardset.get(Cardset.name == fin_name,Cardset.user == current_user)
        except Exception as e:
            break
        else:
            num += 1
            fin_name = "{}_{}".format(name,num)
    tmp = Cardset.create(name=fin_name,user=current_user,create_time=datetime.now().strftime("%Y-%m-%d")\
        ,last_alter_time=datetime.now().strftime("%Y-%m-%d"))
    for i in data:
        for j in data[i]:
            Setcontent.create(set_user=current_user,set_name=fin_name,number=data[i][j],position=i,cardid=j)
    return (True,"新建成功")


if __name__ == '__main__':
    #loop = asyncio.get_event_loop()
    a = send_email("mail test", '1355211477@qq.com', "fx13579")
    print(a)
    #b = send_email("mail test", 'didiking@yeah.net', "final02468")
    #print(loop.run_until_complete(asyncio.gather(a, b)))
    #send_email()