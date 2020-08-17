"""
main.py passes over an object as argument of class Repository

returns commits and their attached message
"""


import urllib.request
import json


def code_pattern(repo_obj, auth):
    # print(repo_obj.get_contents("main.js").decoded_content)
    print(repo_obj.contents_url[:-7])
    with urllib.request.urlopen(repo_obj.contents_url[:-7]) as url:
        json_obj = json.load(url)
        for data in json_obj:
            # if data['path'][-3:] == *repos language* dann gehe hinein und schaue weiter
            print(data["path"])
            file_content = repo_obj.get_contents(data["path"])
            print(file_content)
            if isinstance(file_content, list):
                for file in file_content:
                    print(file_content, ' is a list')
                    print(file.content)
            else:
                print(file_content, ' is not a list')
                print(file_content.content)
                print(file_content.download_url)
            # print(file_content)
