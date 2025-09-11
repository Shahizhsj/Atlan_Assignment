import json
from WebCrawler_1 import res
from WebCrawler_2 import res_


all_urls_ = res()
all_urls=res_()
with open("developer_atlan_urls.json", "w") as f:
    json.dump(list(all_urls), f)


with open("docs_atlan_urls.json", "w") as f:
    json.dump(list(all_urls_), f)
