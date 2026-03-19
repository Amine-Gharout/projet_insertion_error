import requests as r 

endpoint = 'http://localhost:8000/api/v1/Student/'

response = r.get(endpoint)

data = response.json()

i = 0 
for student in data:
    r.patch(f"{endpoint}{student['id']}/" , json={"matricule": f"74/{i:04d}"})
    i += 1