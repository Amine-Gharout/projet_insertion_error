import requests as r 

endpoint = 'http://localhost:8000/api/v1/Student/unique/'

response = r.get(endpoint , json={"matricule":"24/003"})
print(response.json())