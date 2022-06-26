import pymysql as pm
from copy import deepcopy
import sqlite3
import sys
import re
from typing import Tuple

Attribute = {
    0:"N/A",
    0x1:"地",
    0x2:"水",
    0x4:"炎",
    0x8:"风",
    0x10:"光",
    0x20:"暗",
    0x40:"神"}

Race = {
    0x0	:"N/A",
    0x1	:"战士族",
    0x2	:"魔法师族",
    0x4	:"天使族",
    0x8	:"恶魔族",
    0x10	:"不死族",
    0x20	:"机械族",
    0x40	:"水族",
    0x80	:"炎族",
    0x100	:"岩石族",
    0x200	:"鸟兽族",
    0x400	:"植物族",
    0x800	:"昆虫族",
    0x1000	:"雷族",
    0x2000	:"龙族",
    0x4000	:"兽族",
    0x8000	:"兽战士族",
    0x10000	:"恐龙族",
    0x20000	:"鱼族",
    0x40000	:"海龙族",
    0x80000	:"爬虫类族",
    0x100000	:"念动力族",
    0x200000	:"幻神兽族",
    0x400000	:"创造神族",
    0x800000	:"幻龙族",
    0x1000000	:"电子界族"
}

typeList = {
0x1:"怪兽",
0x2:"魔法",
0x4:"陷阱",
0x8:"N/A",
0x10:"通常",
0x20:"效果",
0x40:"融合",
0x80:"仪式",
0x100:"N/A",
0x200:"灵魂",
0x400:"同盟",
0x800:"二重",
0x1000:"调整",
0x2000:"同调",
0x4000:"衍生物",
0x8000:"N/A",
0x10000:"速攻",
0x20000:"永续",
0x40000:"装备",
0x80000:"场地",
0x100000:"反击",
0x200000:"反转",
0x400000:"卡通",
0x800000:"超量",
0x1000000:"灵摆",
0x2000000:"特殊召唤",
0x4000000:"连接"
}


card = {
    "id":None,
    "name":None,
    "type":None,
    "stateNumber":None,
    "isOcg":None,
    "isTcg":None
}

Malist = [0x80,0x10000,0x20000,0x40000,0x80000]
Macard = {
    "Cardid":None,
	"type":None,
    "effect":None
}
Tlist = [0x20000,0x100000]
Tcard = {
    "Cardid":None,
	"type":None,
    "effect":None
}

def data_transfer(data:Tuple[int,str,int,int,int,int,str,int,int,int])->str:
    #print(data)
    base = dict()
    base["Cardid"] = data[0]
    base["isNormal"] = (data[2]&0x10)>0
    base["isEffect"] = (data[2]&0x20)>0
    if base["isNormal"]:
        base["type"] = "通常"
    else:
        base["type"] = "效果"
        for i in [0x40,0x80,0x2000,0x800000,0x4000000]:
            if data[2]&i:
                base["type"] = typeList[i]
                break
    if data[2]&0x1000000:
        base["PendulumNumber"] = (data[7]&0xf0000)>>16
        p = re.search("(【怪兽.{2}】)",data[6])
        desc = p.group(1)
        peffect,meffect = data[6].split(desc)
        base["pendulumEffect"] = peffect.strip()
        base["monsterEffect"] = meffect.strip()
    else:
        base["monsterEffect"] = data[6].strip()
    if base["type"] == "连接":
        base["linkMark"] = data[4]
    else:
        base["def"] = data[4] if data[4]>=0 else -1
    base["isTuner"] = (data[2]&0x1000)>0
    base["isReversal"]=(data[2]&0x200000)>0
    base["isSoul"]=(data[2]&0x200)>0
    base["isDouble"]=(data[2]&0x800)>0
    base["isAlliance"]=(data[2]&0x400)>0
    base["isCartoon"]=(data[2]&0x400000)>0
    base["isToken"]=(data[2]&0x4000)>0
    base["isSpecial"] = (data[2]&0x2000000)>0
    base["starNumber"] = data[7]&0xf
    base["atk"] = data[3] if data[3]>=0 else -1
    base["race"] = Race[data[8]]
    base["attrib"] = Attribute[data[9]]
    p = ""
    for i,j in enumerate(base.keys()):
        p+="`{}`".format(j)
        if i!= len(base)-1:
            p+=','
    #print("insert into MonsterCards ({}) value {};".format(p,tuple(base.values())))
    return "insert into MonsterCards ({}) value {};".format(p,tuple(base.values()))

# t = open("limit.json")
# limits = json.load(t)
# print(type(limits))
db = pm.connect(host='localhost',
                     user='root',
                     password='tj_market',
                     database='test')
db_cursor = db.cursor()
conn = sqlite3.connect("cards.cdb")
cur = conn.cursor()
cur.execute("select id,name,type,atk,def,ot,desc,level,race,attribute from texts natural join datas;")
num = 0
while True:
    res = cur.fetchmany(50)
    if len(res) == 0:
        break
    else:
        for i in range(len(res)):
            my_data = deepcopy(card)
            my_data["id"] = res[i][0]
            my_data["name"] = res[i][1]
            my_data["type"] = typeList[res[i][2]&7]
            my_data["stateNumber"] = 3
            my_data["isOcg"] = res[i][5]&1
            my_data["isTcg"] = (res[i][5]&2)>>1
            sql = "insert into Cards values {}".format(tuple(my_data.values()))
            try:
                db_cursor.execute(sql)
                db.commit()
            except Exception as e:
                db.rollback()
                print(str(e),repr(e))
                sys.exit(-1)
            else:
                if my_data["type"] == typeList[0x1]:
                    #full_data = deepcopy(Mocard)
                    ansql = data_transfer(res[i])
                elif my_data["type"] == typeList[0x2]:
                    full_data = deepcopy(Macard)
                    full_data["Cardid"] = my_data["id"]
                    full_data["type"] = "通常"
                    for j in Malist:
                        if res[i][2]&j:
                            full_data["type"] = typeList[j]
                    full_data ["effect"] = res[i][6]
                    ansql = "insert into MagicCards value {}".format(tuple(full_data.values()))
                elif my_data["type"] == typeList[0x4]:
                    full_data = deepcopy(Tcard)
                    full_data["Cardid"] = my_data["id"]
                    full_data["type"] = "通常"
                    for j in Tlist:
                        if res[i][2]&j:
                            full_data["type"] = typeList[j]
                    full_data ["effect"] = res[i][6]
                    ansql = "insert into Trapcards value {}".format(tuple(full_data.values()))
                else:
                    continue
                try:
                    db_cursor.execute(ansql)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print(ansql)
                    print(str(e),repr(e))
                    sys.exit(-1)
    num+=len(res)
    print(num)

cur.close()
conn.close()
db_cursor.close()
db.close()