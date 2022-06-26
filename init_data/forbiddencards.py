
from datetime import date
import json
an = list()
d = dict()
with open("lflist.conf","r",encoding="utf-8") as f:
    t = f.readlines()
    for i in t:
        j = i.strip()
        if len(j) == 0:
            an.append(d)
            d = dict()
            continue
        if j[0] == "#":
            continue
        elif j[0] == "!":
            if len(d):
                an.append(d)
            p = j[1:]
            if " " in p:
                time,env = p.split(" ")
            else:
                time,env = p,"OCG"
            d = dict()
            d["time"] = time+".1"
            d["env"] = env
            d["0"] = list()
            d["1"] = list()
            d["2"] = list()
        else:
            cardid,num=j.split()[:2]
            d[str(num)].append(cardid)
    if len(d):
                an.append(d)


with open("test.json","w",encoding="utf-8") as f:
    json.dump(an,f)

import pymysql as pm
import json
from datetime import date
db = pm.connect(host='localhost',
                     user='root',
                     password='tj_market',
                     database='test')
db_cursor = db.cursor()
num = 0
with open("test.json","r") as f:
    li = json.load(f)
    for i in li:
        for j in range(3):
            for k in i[str(j)]:
                try:
                    data = (int(k),i["env"],i["time"],j)
                    db_cursor.execute("insert into ForbiddenCard value {}".format(data))
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print(str(e))
                    exit(0)
                else:
                    num+=1
                if num%100 == 0:
                    print(num)

print(num)
db_cursor.close()
db.close()