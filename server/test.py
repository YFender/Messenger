import requests
# import json


def login():
    query = {"login": 1, "password": 9, "asds": "frar"}
    response = requests.post("http://localhost:8080/login", data=query)
    print(response.text)


login()
# print(post())
# print(get())
