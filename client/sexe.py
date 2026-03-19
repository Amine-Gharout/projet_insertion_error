import requests as r 

endpoint = 'http://localhost:8000/api/v1/Student/'

response = r.get(endpoint)

data = response.json()
i = 0 
for student in data:
    if(i %2 == 0):
        r.patch(f"{endpoint}{student['id']}/" , json={"sexe": "Male"})
    else:
        r.patch(f"{endpoint}{student['id']}/" , json={"sexe": "Female"})
    i += 1
