import requests
# import json


def login():
    query = {"login": '""[11[]111', "password": 9, "asds": "frar"}
    response = requests.get("http://localhost:8080/", data=query)
    print(response.text)


login()
# print(post())
# print(get())
