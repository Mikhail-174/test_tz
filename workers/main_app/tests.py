from django.test import TestCase


import requests

url = "http://localhost:8000/api/workers/import/"
files = {'file': open('C:/Users/Дорофеев Михаил/PycharmProjects/workers/workers/example_import.xlsx', 'rb')}
# headers = {
#     'Authorization': 'Token your_token'  # если требуется
# }

response = requests.post(url, files=files)
print(response.status_code)
print(response.json())
