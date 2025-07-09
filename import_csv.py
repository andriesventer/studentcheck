import requests

collegeid="1"

def enrolment_check(collegeid,cycle_name, idnr, programme_code, enrolled):
    url = "http://localhost:8000/enrolment-check"
    payload = {
        "cycle_name": cycle_name,
        "idnr": idnr,
        "programme_code": programme_code,
        "enrolled": enrolled,
        "collegeid": collegeid
    }
    response = requests.post(url, json=payload)
    return response.json()

with open('export.csv', 'r') as f:
    lines = f.readlines()
    # Assuming the first line contains the header
    header = lines[0].strip().split(',')
    # Assuming the second line contains the data
    for line in lines[1:]:
        data = line.strip().split(',')
        cycle_name = data[0]
        idnr = data[1] 
        programme_code = data[2]
        enrolled = data[3]
        result = enrolment_check(collegeid,cycle_name, idnr, programme_code, enrolled)
        print(result)
        
        

