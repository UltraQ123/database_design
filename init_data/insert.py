import json
import pymysql as pm
with open("cardbaglist_cards.json","r",encoding="utf-8") as f:
    cardbaglist = json.load(f)
db = pm.connect(host='localhost',
                     user='root',
                     password='tj_market',
                     database='test')
db_cursor = db.cursor()
details = list()
no_list = list()
num = 1
for i in cardbaglist:
    no_list = list()
    data = (num,i["short_name"] if i["short_name"] is not None else "null"\
        ,i["full_name"] if i["full_name"] is not None else "null" \
        ,i["time"] )
    db_cursor.execute("insert into CardBag values (%s,%s,%s,%s)",\
        data)
    db.commit()
    for j in i["cards"]:
        try:
            db_cursor.execute("select * from cards where cards.id={};".format(j))
            result = db_cursor.fetchall()
            if len(result) == 0:
                no_list.append(j)
                db_cursor.execute("delete from Bagcontent where CardBagid={}".format(num))
                db_cursor.execute("delete from CardBag where id={}".format(num))
                db.commit()
                break
            else:
                db_cursor.execute("insert into bagcontent value {}".format((num,j)))
                db.commit()
        except Exception as e:
            print(j,num)
            print(repr(e))
            exit(0)
    if len(no_list)>0:
        details.append({"baghref":i["href"],"no_list":no_list})
    else:
        num+=1
        if num%100 == 0:
            print(num)


db_cursor.close()
db.close()
with open("no_list.json","w",encoding="utf-8") as f:
    json.dump(details,f,ensure_ascii=False)

