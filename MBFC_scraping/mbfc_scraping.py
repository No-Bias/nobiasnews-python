from bs4 import BeautifulSoup
import requests
import json
import time
from pathlib import Path

website_links = {
    "left": "https://mediabiasfactcheck.com/left/",
    "left center": "https://mediabiasfactcheck.com/leftcenter/",
    "center": "https://mediabiasfactcheck.com/center/",
    "right center": "https://mediabiasfactcheck.com/right-center/",
    "right": "https://mediabiasfactcheck.com/right/",
}

with open("website_mapping.json") as f:
    website_mapping = json.load(f)


def construct_dictionary(website_link):
    d = {}
    resp = requests.get(website_link)
    soup = BeautifulSoup(resp.content, "html.parser")
    tds = soup.find_all("td")
    for td in tds:
        try:
            text_tup = td.text.split("(")
            mbfc_site = td.a["href"]
            name = text_tup[0].strip()
            site = text_tup[-1].strip(") ")
            if site.startswith("http"):
                site = site.split("//")[1]
            if name == site or "." not in site:
                if name not in website_mapping:
                    print("New News site detected: " + name)
                    # something new, not included in website_mapping
                else:
                    site = website_mapping.get(name) or name
                    # omitting sites that are offline and have no websites
                    # indexing such sites with their names itself
            d[site] = (name, mbfc_site)
        except Exception as e:
            pass
            # ignoring advertisements in table rows
            # print(td)
    return d


bias_data = {}
# data will be structured as:
# bias_type1:
#   news_website URL:
#       news_website name
#       news_website link on MBFC

for type, link in website_links.items():
    bias_data[type] = construct_dictionary(link)


file_location = Path("data")
file_name = f"data{time.strftime('%Y%m%d_%H%M',time.gmtime())}.json"
# file_name contains UTC timestamp; to prevent automatic overwriting
file_path = file_location / file_name

with open(file_path, "w") as outfile:
    json.dump(bias_data, outfile)
