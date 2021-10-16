import requests
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser(description='download mp3 from Rozhlas Vltava page')
parser.add_argument("-url",type=str)

args = parser.parse_args()

URL = args.url
MULTIPLE_PARTS = False

page_html = requests.get(URL)
# page_html = req.read()

html_soup = BeautifulSoup(page_html.content, "html.parser")

try:
    html_player_list_items = html_soup.find(id="file-serial-player").find("ul").find_all("li")
    MULTIPLE_PARTS = True
except:
    html_player_list_items = html_soup.find(class_="file-audio").find_all("li")[0]
    MULTIPLE_PARTS = False

# import pdb; pdb.set_trace()

# get the series title
# html_soup.find(id="file-serial-player").find("ul").find_all("li")[0].find("a").contents[0].get("title")

# get the mp3 title:
# html_soup.find(id="file-serial-player").find("ul").find_all("li")[0].find("a").find(class_="filename__text").contents

# get the mp3 url:
# html_soup.find(id="file-serial-player").find("ul").find_all("li")[0].find('a').get("href")

def replace_chars(string):
    string = "".join([c if c.isalnum() else "_" for c in string])
    return string

def extract_metadata(html_player_items): 

    metadata = {}
    metadata["parts"] = []

    if MULTIPLE_PARTS:

        metadata["title"] = html_player_items[0].find("a").contents[0].get("title")

        for part in html_player_items:
            part_name = part.find("a").find(class_="filename__text").contents[0]
            part_url = part.find('a').get("href")
            part_filename = replace_chars("{} {}".format(metadata["title"], part_name))
            metadata["parts"].append(
                {
                    "part_name": part_name,
                    "part_url": part_url, 
                    "part_filename": part_filename + ".mp3"
                }
                )

    else:
        metadata["title"] = html_player_items.find("a").contents[0]
        part_name = html_player_items.find("a").contents[0]
        part_url = html_player_items.find("a").get("href")
        part_filename = replace_chars("{}".format(part_name))
        metadata["parts"].append(
                {
                    "part_name": part_name,
                    "part_url": part_url, 
                    "part_filename": part_filename + ".mp3"
                }
                )

    return metadata

print(extract_metadata(html_player_list_items))
import pdb; pdb.set_trace()

def download_files(metadata):

    for part in metadata["parts"]:
        print("now downloading {} from {}".format(
            part["part_filename"],
            part["part_url"]
        ))
        file = requests.get(part["part_url"])
        with open(part["part_filename"], 'wb') as file_output:
            print("writing {}".format(part["part_filename"]))
            file_output.write(file.content)
            print("done")

series_metadata = extract_metadata(html_player_list_items)
# download_files(series_metadata)