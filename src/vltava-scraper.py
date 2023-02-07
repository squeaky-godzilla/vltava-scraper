import requests
import os
import json
from bs4 import BeautifulSoup
import argparse
from zipfile import ZipFile
from gofile import Gofile

parser = argparse.ArgumentParser(description='download mp3 from Rozhlas Vltava page')
parser.add_argument("-url",type=str)

args = parser.parse_args()

URL = args.url

page_html = requests.get(URL)

html_soup = BeautifulSoup(page_html.content, "html.parser")

metadata_string = html_soup.find(class_="mujRozhlasPlayer").attrs["data-player"].encode().decode("unicode-escape").replace("\\","")


client = Gofile()

try:
    player_metadata = json.loads(metadata_string)
except json.decoder.JSONDecodeError:
    with open("error_metadata", "wb") as metadata_json:
        metadata_json.write(metadata_string.encode())

playlist = player_metadata["data"]["playlist"]

archive_filename = player_metadata["data"]["series"]["title"].split(".")[0] + ".zip"



def download_files(playlist):

    file_list = []
    
    for part in playlist:
        content_name = part["meta"]["ga"]["contentNameShort"]
        try:
            part_number = part["meta"]["ga"]["contentSerialPart"]
        except KeyError:
            part_number = ""
        url = part["audioLinks"][0]["url"]
        filename = "{} - {}.mp3".format(content_name, part_number)

        file_list.append(filename)


        print("stahuju {}".format(filename))
        data = requests.get(url)
        with open(filename, "wb") as file_out:
            file_out.write(data.content)

    print("Hotovo!")
    return(file_list)

def archive_files(archive_filename, file_list):
    
    print("pakuju do archivu {}".format(archive_filename))
    with ZipFile(archive_filename, "w") as archive:
        for filename in file_list:
            archive.write(filename)


def delete_files(file_list):
    for filename in file_list:
        os.remove(filename)

def upload_archive(archive_filename):
    response = client.upload_file(archive_filename)
    print("download link: {}".format(response["downloadPage"]))

file_list = download_files(playlist)
archive_files(archive_filename, file_list)
upload_archive(archive_filename)
delete_files(file_list)
delete_files([archive_filename])