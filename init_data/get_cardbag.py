from lxml import etree
import requests
import json
from copy import deepcopy

node = {
        "time": None,
        "short_name": None,
        "num": None,
        "full_name": None,
        "href": None
    }
cardbaglist = list()
num = 0
url = "https://ygocdb.com/packs"
req = requests.get(url=url,headers={'Connection':'close'})
text = etree.HTML(req.text)
p = text.xpath("//li[@class='pack']")
for i in p:
    i_node = deepcopy(node)
    time,shortname,num,href=i.getchildren()
    i_node["time"] = time.text
    i_node["short_name"] = shortname.text
    i_node["num"] = num.text
    i_node["full_name"] = href.text
    i_node["href"] = "https://ygocdb.com"+ href.attrib["href"]
    cardbaglist.append(i_node)
    print(i_node)

with open("cardbaglist.json","w",encoding="utf-8") as f:
    json.dump(cardbaglist,f,ensure_ascii=False)