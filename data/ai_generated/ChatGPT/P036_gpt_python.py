import requests

url = "https://internal-api.company.com/users"

response = requests.get(
    url,
    verify=False
)

print(response.status_code)
print(response.text)