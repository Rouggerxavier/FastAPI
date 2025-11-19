import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3IiwiZXhwIjoxNzYzNTU0OTUxfQ.SjFqpiNIr2YVYS406wPLZpseIJwCB4D2JaOY-1Gju8c"

headers = {
    "Authorization": f"Bearer {token}"
}

requisicao = requests.get(
    "http://127.0.0.1:8000/auth/refresh",
    headers=headers,
)

print(requisicao.status_code)
print(requisicao.json())
