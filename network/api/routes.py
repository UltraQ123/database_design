import re
import os
import time
import json
import app
import random
from api.utils import *
from api import api_blue
from Base import database
from Base.models import *
from Base.Enumtype import *
from werkzeug.security import generate_password_hash
from flask import make_response, request,jsonify,url_for
from flask_login import current_user, login_user
from datetime import datetime,timedelta
@api_blue.before_request
def before_request():
    if database.is_closed():
        database.connect()


@api_blue.teardown_request
def teardown_request(exc):  #exc必须写上
    if not database.is_closed():
        database.close()


@api_blue.route("/get_envs",methods=["GET"])
def get_envs():
    return make_response(jsonify(list(envs._value2member_map_)))

@api_blue.route("/get_card_type",methods = ["GET"])
def get_card_type():
    return make_response(jsonify(list(card_type._value2member_map_)))

@api_blue.route("/get_detail_select",methods=["GET"])
def get_detail_select():
    try:
        c_type = request.args.get("type")
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"请求格式错误"}))
    if c_type not in card_type._value2member_map_:
        return make_response(jsonify({"success":False,"message":"请求格式错误"}))
    if c_type == "魔法":
        data = {"success":True,"data":[{"name":"type","text":"魔法类型",
        "type":"select","list":list(magic_type._value2member_map_.keys())}]}
    elif c_type == "陷阱":
        data = {"success":True,"data":[{"name":"type","text":"陷阱类型",
            "type":"select","list":list(trap_type._value2member_map_.keys())}]}
    elif c_type == "怪兽":
        data = {"success":True,"data":list()}
        data["data"].append({"name":"attrib","text":"属性","type":"select","list":list(attribute._value2member_map_.keys())})
        data["data"].append({"name":"race","text":"种族","type":"select","list":list(race._value2member_map_.keys())})
        data["data"].append({"name":"type","text":"类型","type":"select","list":list(monster_type._value2member_map_.keys())})
        data["data"].append({"name":"special","text":"特殊选项","type":"checkbox",\
            "list":list(monster_special._value2member_map_.keys()),"size":[len(monster_special),1],"disable":[],\
                "values":list(monster_special._value2member_map_.keys())})
        data["data"].append({"name":"linkmark","text":"连接标记","type":"checkbox",\
            "list":[""]*9,"size":[3,3],"disable":[4],\
                "values":[0x40,0x80,0x100,0x8,0x10,0x20,0x1,0x2,0x4]})
        data["data"].append({"name":"show","text":"对应箭头","type":"show","list":["↖","↑","↗","←","&ensp;","→","↙","↓","↘"],"size":[3,3]})
        data["data"].append({"name":"starNumber_min","text":"等级最小值","type":"input"})
        data["data"].append({"name":"starNumber_max","text":"等级最大值","type":"input"})
        data["data"].append({"name":"PendulumNumber_min","text":"灵摆刻度最小值","type":"input"})
        data["data"].append({"name":"PendulumNumber_max","text":"灵摆刻度最大值","type":"input"})
        data["data"].append({"name":"atk_min","text":"攻击力最小值","type":"input"})
        data["data"].append({"name":"atk_max","text":"攻击力最大值","type":"input"})
        data["data"].append({"name":"def_min","text":"防御力最小值","type":"input"})
        data["data"].append({"name":"def_max","text":"防御力最大值","type":"input"})
    return make_response(jsonify(data))

@api_blue.route("/search",methods=["POST"])
def search():
    data = request.get_json()
    """
    Cards.select().join(Monstercards,on=(Monstercards.cardid == Cards.id),join_type=pw.JOIN.LEFT_OUTER)\
    .join(Magiccards,on=(Magiccards.cardid == Cards.id),join_type=pw.JOIN.LEFT_OUTER)\
    .join(Trapcards,on=(Trapcards.cardid == Cards.id),join_type=pw.JOIN.LEFT_OUTER).where().order_by().execute()
    """
    if "page" not in data:
        page = 1
    else:
        try:
            page = int(data["page"])
        except Exception as e:
            return make_response(jsonify({"success":False,"message":"请求格式不对"}))
        if page < 1:
            return make_response(jsonify({"success":False,"message":"请求格式不对"}))

    if "card_type" not in data:
        result = [True,list()]
        funcs = [search_monster,search_magic,search_trap]
        for i in funcs:
            p = i(data)
            if p[0] == False:
                return make_response(jsonify({"success":False,"message":p[1]}))
            else:
                result[1]+=p[1]
        result = tuple(result)
    else:
        if data["card_type"] not in card_type._value2member_map_:
            return make_response(jsonify({"success":False,"message":"请求格式不对"}))
        else:
            if data["card_type"] == card_type.monster.value:
                result = search_monster(data)
            elif data["card_type"] == card_type.magic.value:
                result = search_magic(data)
            elif data["card_type"] == card_type.trap.value:
                result = search_trap(data)
            if result[0] == False:
                return make_response(jsonify({"success":False,"message":result[1]}))
    total_page = len(result[1])//50+1
    if total_page >= page:
        p = result[1][(page-1)*50:min(len(result[1]),page*50)]
    else:
        p = list()
    return make_response(jsonify({"success":True,"message":"搜索结果如下","data":p,"page":min(total_page,page),"total_page":total_page}))

from copy import deepcopy


@api_blue.route("/get_card_data",methods=["GET"])
def get_card_data():
    env = request.args.get("env")
    if env is None or env not in envs._value2member_map_:
        env = "OCG"
    #print(env)
    try:
        card_id = int(request.args.get("id"))
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"请求格式错误"}))
    try:
        card = Cards.get(Cards.id == card_id)
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"请求的卡不存在"}))
    data = dict()
    data["success"] = True
    data["data"] = deepcopy(card.__data__)
    if card.card_type == card_type.monster.value:
        try:
            card_detail = Monstercards.get(Monstercards.cardid == card_id)
        except Exception as e:
            return make_response(jsonify({"success":False,"message":"数据库存储错误,请联系系统管理员1355211477@qq.com"}))
    elif card.card_type == card_type.magic.value:
        try:
            card_detail = Magiccards.get(Magiccards.cardid == card_id)
        except Exception as e:
            return make_response(jsonify({"success":False,"message":"数据库存储错误,请联系系统管理员1355211477@qq.com"}))
    elif card.card_type == card_type.trap.value:
        try:
            card_detail = Trapcards.get(Trapcards.cardid == card_id)
        except Exception as e:
            return make_response(jsonify({"success":False,"message":"数据库存储错误,请联系系统管理员1355211477@qq.com"}))
    data["data"]["detail"] =deepcopy(card_detail.__data__)
    data["data"]["detail"].pop("cardid")
    if card.card_type == card_type.monster.value:
        data["data"]["detail"]["tag"] = [card_detail.type]
        data["data"]["detail"].pop("type")
        for s in monster_special._value2member_map_:
            data["data"]["detail"].pop(f"is_{monster_special._value2member_map_[s].name}")
            if eval(f"card_detail.is_{monster_special._value2member_map_[s].name}") == 1:
                if s not in data["data"]["detail"]["tag"]:
                    data["data"]["detail"]["tag"].append(s)
    try:
        forbid = Forbiddencard.select(Forbiddencard.number)\
            .where(Forbiddencard.cardid == data["data"]["id"],pw.Tuple(env,Forbiddencard.time)\
                .in_(Forbiddencard.select(Forbiddencard.env,pw.fn.MAX(Forbiddencard.time))\
                    .group_by(Forbiddencard.env)))
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库存储错误,请联系系统管理员1355211477@qq.com"}))
    else:
        if forbid.count() == 0:
            data["data"]["detail"]["number"] = 3
        else:
            data["data"]["detail"]["number"] = forbid.get().number
    return make_response(jsonify(data))


@api_blue.route("/get_forbidden_tables",methods=["GET"])
def get_forbidden_tables():
    try:
        datas = Forbiddencard.select(Forbiddencard.time.distinct(),Forbiddencard.env)\
        .order_by(Forbiddencard.time.desc()).execute()
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库存储错误,请联系系统管理员1355211477@qq.com"}))
    data = dict()
    data["success"] = True
    data["data"] = list()
    for i in datas:
        j = i.__data__
        j["time"] = str(j["time"])
        data["data"].append(j)
    return make_response(jsonify(data))

@api_blue.route("/get_forbidden",methods=["GET"])
def get_forbidden():
    data = dict(request.args)
    if "env" not in data:
        env = "OCG"
    else:
        env = data["env"]
    if "time" not in data:
        temp = Forbiddencard.select(pw.fn.Max(Forbiddencard.time).alias("ans"))\
            .where(Forbiddencard.env == env).execute()
        if len(temp) == 0:
            return make_response(jsonify({"success":False,"message":"指定了不存在的环境"}))
        table_time = temp[0].ans
    else:
        try:
            table_time = datetime.strptime(data["time"],"%Y-%m-%d").date()
        except Exception as e:
            print(repr(e))
            return make_response(jsonify({"success":False,"message":"指定的时间信息错误"}))
    try:
        table = Forbiddencard.select(Forbiddencard.cardid,Forbiddencard.number)\
            .join(Cards,on=(Cards.id==Forbiddencard.cardid))\
            .join(Monstercards,on=(Monstercards.cardid==Forbiddencard.cardid),join_type=pw.JOIN.LEFT_OUTER)\
            .join(Magiccards,on=(Magiccards.cardid==Forbiddencard.cardid),join_type=pw.JOIN.LEFT_OUTER)\
            .join(Trapcards,on=(Trapcards.cardid==Forbiddencard.cardid),join_type=pw.JOIN.LEFT_OUTER)\
            .where((Forbiddencard.env == env)&(Forbiddencard.time == table_time))\
            .order_by(Forbiddencard.number,Cards.card_type,Monstercards.type.asc(),\
            Magiccards.type.asc(),Trapcards.type.desc(),Monstercards.star_number.desc()).execute()
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库存储错误,请联系系统管理员1355211477@qq.com"}))
    datas = dict()
    datas["success"] = True
    datas["data"] = list()
    for i in table:
        j = i.__data__
        j["name"] = i.cardid.name
        datas["data"].append(j)
    print(datas)
    return make_response(jsonify(datas))


@api_blue.route("/send_verify",methods=["POST"])
def send_verify():
    try:
        email = request.get_json()["email"]
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"请求格式错误"}))
    if not os.path.exists(os.path.join(app.app.static_folder,"verify.json")):
        try:
            os.makedirs(app.app.static_folder)
        except Exception as e:
            pass
        with open(os.path.join(app.app.static_folder,"verify.json"),"w") as f:
            pass
    with open(os.path.join(app.app.static_folder,"verify.json"),"r+",encoding="utf-8") as fp:
        try:
            pre = json.load(fp)
        except Exception as e:
            pre = list()
        #print(pre)
        for i in pre:
            if i["email"] == email and int(time.time()) - i["time"] < 300:
                # json.dump(list(filter(lambda x:int(time.time())-x["time"] < 300,pre)),fp,ensure_ascii=False)
                return make_response({"success":False,"message":"验证码请求过于频繁"})
        verify = create_string_number(6)
        ret = send_email("游戏王卡片系统验证码",[email],f'您的注册验证码为：{verify}。有效期为5分钟。\n此邮件为系统自动发出，请勿回复。')
        if ret["status"] == False:
            print(ret["message"])
            return make_response(jsonify({"success":False,"message":"验证码发送失败,请检查输入邮箱,或联系管理员邮箱1355211477@qq.com"}))
        pre.append({"time":int(time.time()),"email":email,"verify":verify})
        fp.seek(0,0)
        fp.truncate(0)
        new_pre = list(filter(lambda x:int(time.time())-x["time"] < 300,pre))
        #print(new_pre)
        json.dump(new_pre,fp,ensure_ascii=False)
        return make_response(jsonify({"success":True,"message":"验证码发送成功,请检查邮箱"}))

@api_blue.route("/register",methods=["POST"])
def register():
    if current_user.is_authenticated:
        return make_response(jsonify({"success":False,"message":"您已经登录","url":url_for('user.space')}))
    data = request.get_json()
    check_data = check_register_data(data)
    if not check_data[0]:
        return make_response(jsonify({"success":False,"message":check_data[1]}))
    try:
        user = User.create(name=data["username"],email=data["email"]\
            ,password = generate_password_hash(data["password"]))
        login_user(user,True,timedelta(days=15))
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据建立出现问题,请联系系统管理员1355211477@qq.com"}))
    return make_response(jsonify({"success":True,"message":"注册成功","url":url_for('user.space')}))

@api_blue.route("/forget",methods=["POST"])
def forget():
    if current_user.is_authenticated:
        return make_response(jsonify({"success":False,"message":"您已经登录","url":url_for('user.space')}))
    data = request.get_json()
    if "email" not in data or "verify" not in data or "password" not in data:
        return make_response(jsonify({"success":False,"message":"请求格式不对"}))
    check = check_email(data["email"],data["verify"])
    if check[0] == False:
        return make_response(jsonify({"success":False,"message":check[1]}))
    try:
        user:User = User.get(User.email == data["email"])
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"此邮箱无用户使用"}))
    if user.check_password(data["password"]):
        return make_response(jsonify({"success":False,"message":"新密码不得与原密码相同"}))
    check = check_password_pattern(data["password"])
    if check[0] == False:
        return make_response(jsonify({"success":False,"message":check[1]}))
    try:
        user.password = generate_password_hash(data["password"])
        user.save()
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"数据库存储失败,请联系系统管理员1355211477@qq.com"}))
    login_user(user,True,timedelta(days=10))
    return make_response(jsonify({"success":True,"message":"登录成功","url":url_for('user.space')}))


@api_blue.route("/password_login",methods=["POST"])
def password_login():
    if current_user.is_authenticated:
        return make_response(jsonify({"success":False,"message":"您已经登录","url":url_for('user.space')}))
    data = request.get_json()
    try:
        username = data["username"]
        password = data["password"]
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"请求格式错误"}))
    check = check_user_pattern(username)
    if check[0] == False:
        return make_response(jsonify({"success":False,"message":check[1]}))
    check = check_password_pattern(password)
    if check[0] == False:
        return make_response(jsonify({"success":False,"message":check[1]}))
    try:
        user:User = User.get(User.name == username)
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"不存在的用户,请注册"}))
    if not user.check_password(password):
        return make_response(jsonify({"success":False,"message":"密码错误"}))
    login_user(user,True,timedelta(days=10))
    return make_response(jsonify({"success":True,"message":"登录成功","url":url_for('user.space')}))

@api_blue.route("/get_current_data",methods=["GET"])
def get_current_data():
    if not current_user.is_authenticated:
        return make_response(jsonify({"success":False,"message":"当前用户未登录"}))
    data =deepcopy(current_user.__data__)
    data.pop("password")
    return make_response(jsonify({"success":True,"message":"获取成功","data":data}))

@api_blue.route("/change_password",methods=["POST"])
def change_password():
    if not current_user.is_authenticated:
        return make_response(jsonify({"success":False,"message":"当前用户未登录"}))
    data = request.get_json()
    if "old_password" not in data or "password" not in data:
        return make_response(jsonify({"success":False,"message":"请求格式不对"}))
    if data["old_password"] == data["password"]:
        return make_response(jsonify({"success":False,"message":"修改前后密码不可一致"}))
    check = check_password_pattern(data["old_password"])
    if check[0] == False:
        return make_response(jsonify({"success":False,"message":check[1]}))
    check = check_password_pattern(data["password"])
    if check[0] == False:
        return make_response(jsonify({"success":False,"message":check[1]}))
    if not current_user.check_password(data["old_password"]):
        return make_response(jsonify({"success":False,"message":"原密码输入错误"}))
    try:
        current_user.password = generate_password_hash(data["password"])
        current_user.save()
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库存储失败,请联系系统管理员1355211477@qq.com"}))
    return make_response(jsonify({"success":True,"message":"修改成功"}))

@api_blue.route("/get_current_set_list",methods=["GET"])
def get_current_set_list():
    if not current_user.is_authenticated:
        return make_response(jsonify({"success":False,"message":"当前用户未登录"}))
    try:
        result = Cardset.select().where(Cardset.user == current_user)\
        .order_by(Cardset.create_time.desc()).execute()
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库存储失败,请联系系统管理员1355211477@qq.com"}))
    p = list()
    for i in result:
        j = deepcopy(i.__data__)
        j["create_time"] = str(j["create_time"])
        j["last_alter_time"] = str(j["last_alter_time"])
        p.append(j)
    return make_response(jsonify({"success":True,"message":"查询成功","data":p}))

@api_blue.route("/get_set",methods=["GET"])
def get_set():
    try:
        user = request.args.get("user")
        name = request.args.get("name")
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"请求格式不对"}))
    try:
        card_set = Cardset.get(Cardset.user==user,Cardset.name==name)
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"此卡组不存在"}))
    need = [Cards.id,Cards.name,Setcontent.number,Setcontent.position]
    try:
        result = Setcontent.select(*need).join(Cards,on=(Cards.id==Setcontent.cardid))\
        .join(Monstercards,on=(Monstercards.cardid==Setcontent.cardid),join_type=pw.JOIN.LEFT_OUTER)\
        .join(Magiccards,on=(Magiccards.cardid==Setcontent.cardid),join_type=pw.JOIN.LEFT_OUTER)\
        .join(Trapcards,on=(Trapcards.cardid==Setcontent.cardid),join_type=pw.JOIN.LEFT_OUTER)\
        .where(Setcontent.set_user==user,Setcontent.set_name==name)\
        .order_by(Setcontent.position.asc(),Cards.card_type.asc(),Monstercards.type.asc(),\
        Magiccards.type.asc(),Trapcards.type.desc(),Monstercards.star_number.desc()).execute()
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库查询失败,请联系系统管理员1355211477@qq.com"}))
    p = list()
    for i in result:
        p.append(i.__data__)
        p[-1].update(i.cardid.__data__)
        p[-1].pop("id")
    return make_response(jsonify({"success":True,"message":"查询成功","data":p}))

@api_blue.route("/search_cardset",methods=["POST"])
def search_cardset():
    data = request.get_json()
    #print(data)
    need = list()
    condition = list()
    if "page" not in data:
        page = 1
    else:
        try:
            page = int(data["page"])
        except Exception as e:
            return make_response(jsonify({"success":False,"message":"请求格式不对"}))
        if page < 1:
            return make_response(jsonify({"success":False,"message":"请求格式不对"}))
    if "card_name" in data:
        condition.append(Cards.name.contains(data["card_name"]))
    if "set_name" in data:
        condition.append(Cardset.name.contains(data["set_name"]))
    try:
        if len(condition) > 0:
            result = Cardset.select(*need)\
            .join(Setcontent,on=((Setcontent.set_name==Cardset.name)&(Setcontent.set_user==Cardset.user)))\
            .join(Cards,on=(Cards.id==Setcontent.cardid))\
            .where(*condition).distinct().order_by(Cardset.create_time.desc()).execute()
        else:
            result = Cardset.select(*need).order_by(Cardset.create_time.desc()).execute()
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库查询出错,请联系系统管理员1355211477@qq.com"}))
    total_page = len(result)//50+1
    p = list()
    if total_page >= page:
        for i in range((page-1)*50,min(len(result),page*50)):
            j = deepcopy(result[i].__data__)
            j["create_time"] = str(j["create_time"])
            j["last_alter_time"] = str(j["last_alter_time"])
            p.append(j)
    return make_response(jsonify({"success":True,"message":"搜索结果如下","data":p,"page":min(total_page,page),"total_page":total_page}))

@api_blue.route("/delete_set",methods=["DELETE"])
def delete_set():
    if not current_user.is_authenticated:
        return make_response(jsonify({"success":False,"message":"当前用户未登录"}))
    data = request.get_json()
    if "name" not in data:
        return make_response(jsonify({"success":False,"message":"请求格式不对"}))
    try:
        card_set = Cardset.get(Cardset.user==current_user,Cardset.name==data["name"])
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"不存在此卡组"}))
    try:
        with database.atomic() as transcation:
            Setcontent.delete().where(Setcontent.set_user==current_user,Setcontent.set_name==data["name"]).execute()
            card_set.delete_instance()
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库删除失败,请联系系统管理员1355211477@qq.com"}))
    return make_response(jsonify({"success":True,"message":"删除成功"}))




@api_blue.route("/post_set",methods=["POST"])
def post_set():
    if not current_user.is_authenticated:
        return make_response(jsonify({"success":False,"message":"请先登录"}))
    data = request.files.to_dict()
    check_pattern = re.compile("^(.*?).ydk$")
    message = ""
    for i in data:
        res = check_pattern.match(i)
        if res is None:
            continue
        name = res.group(1)
        if data[i].mimetype=="application/octet-stream":
            data[i].save(os.path.join(app.app.static_folder,i))
            data[i].close()
            try:
                temp = read_ydk(os.path.join(app.app.static_folder,i))
            except Exception as e:
                message+=f"{i}读取失败\n"
            else:
                insert_new_ydk(name,temp)
            finally:
                os.remove(os.path.join(app.app.static_folder,data[i].filename))
    return make_response(jsonify({"success":True,"message":message}))

@api_blue.route("/search_cardbag",methods=["POST"])
def search_cardbag():
    data = request.get_json()
    #print(data)
    need = list()
    condition = list()
    if "page" not in data:
        page = 1
    else:
        try:
            page = int(data["page"])
        except Exception as e:
            return make_response(jsonify({"success":False,"message":"请求格式不对"}))
        if page < 1:
            return make_response(jsonify({"success":False,"message":"请求格式不对"}))
    if "card_name" in data:
        condition.append(Cards.name.contains(data["card_name"]))
    try:
        if len(condition) > 0:
            result = Cardbag.select(*need).join(Bagcontent,on=(Cardbag.id==Bagcontent.card_bag))\
            .join(Cards,on=(Cards.id==Bagcontent.cardid))\
            .where(*condition).distinct().order_by(Cardbag.time.desc()).execute()
        else:
            result = Cardbag.select(*need).order_by(Cardbag.time.desc()).execute()
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库查询出错,请联系系统管理员1355211477@qq.com"}))
    total_page = len(result)//50+1
    p = list()
    if total_page >= page:
        for i in range((page-1)*50,min(len(result),page*50)):
            j = deepcopy(result[i].__data__)
            j["time"] = str(j["time"])
            p.append(j)
    return make_response(jsonify({"success":True,"message":"搜索结果如下","data":p,"page":min(total_page,page),"total_page":total_page}))

@api_blue.route("/get_cardBag_data",methods=["GET"])
def get_cardBag_data():
    try:
        cbid = int(request.args.get("id"))
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"请求格式不对"}))
    try:
        result = Cardbag.get_by_id(cbid)
    except Exception as e:
        return make_response(jsonify({"success":False,"message":"此卡包不存在"}))
    p = deepcopy(result.__data__)
    p["time"] = str(p["time"])
    p.pop("id")
    need = [Bagcontent.cardid]
    try:
        detail = Bagcontent.select(*need).where(Bagcontent.card_bag==result).execute()
    except Exception as e:
        print(repr(e))
        return make_response(jsonify({"success":False,"message":"数据库查询出错,请联系系统管理员1355211477@qq.com"}))
    p["detail"] = list()
    for i in detail:
        p["detail"].append({"cardid":i.__data__["cardid"],"name":i.cardid.name})
    return make_response(jsonify({"success":True,"message":"搜索结果如下","data":p}))