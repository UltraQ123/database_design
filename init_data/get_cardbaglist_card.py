from lxml import etree
import requests
import json
from copy import deepcopy
with open("cardbaglist.json","r",encoding="utf-8") as f:
    cardbaglist = json.load(f)
plist = list()
num = 0
for i in cardbaglist:
    j = deepcopy(i)
    url = j["href"]
    j["cards"] = list()
    req = requests.get(url=url,headers={'Connection':'close'})
    text = etree.HTML(req.text)
    p = text.xpath("//p[@class='buttons']")
    for k in p:
        h3 = k.getprevious().getprevious()
        if int(h3.getchildren()[0].text) not in j["cards"]:
            j["cards"].append(int(h3.getchildren()[0].text))
    plist.append(j)
    num+=1
    if num%100==0:
        print(num)
with open("cardbaglist_cards.json","w",encoding="utf-8") as f:
    json.dump(plist,f,ensure_ascii=False)

