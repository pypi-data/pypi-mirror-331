import requests as r

josn=r.get("https://pypi.org/pypi/esycord/json").json()

print(josn["releases"].popitem()[0])