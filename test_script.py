import requests

response = requests.post(
    "http://localhost:5000/add-secret",
    json={"name": "py_test", "value": "pysecret"}
)

print(response.status_code)
print(response.json())
