import requests

api_key="6RDGH9fMHHTvCiQbmBKRnat77Y49vS0p"



def enrolment_check(cycle_name, idnr, programme_code, enrolled, api_key):
    url = "https://studdup.tvet.org.za/enrolment-check"
    payload = {
        "cycle_name": cycle_name,
        "idnr": idnr,
        "programme_code": programme_code,
        "enrolled": enrolled
    }
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['status'], data['duplicates']
           

with open('export.csv', 'r') as f,open('results.txt', 'w') as results_file:
    lines = f.readlines()
    # Assuming the first line contains the header
    header = lines[0].strip().split(',')
    # Write the header to the results file
    results_file.write(f"IdNr,Cycle,ProgrammeCode, Enrolled,Result,Duplicated\n")
    # Assuming the second line contains the data
    for line in lines[1:]:
        data = line.strip().split(',')
        cycle_name = data[0]
        idnr = data[1] 
        programme_code = data[2]
        enrolled = data[3]
        result = enrolment_check(cycle_name, idnr, programme_code, enrolled, api_key)
        # Write the result to the file
        if not result:
            result ="Error - No response from server"
        elif isinstance(result, tuple):
            result, duplicates = result
        
        print(f"IDNR: {idnr}, Cycle: {cycle_name}, Programme Code: {programme_code}, Enrolled: {enrolled} ,Result: {result}, Duplicated: {duplicates if len(duplicates)>0 else 'N/A'}")
        results_file.write(f"{idnr},{cycle_name},{programme_code},{enrolled},{result},{duplicates if len(duplicates)>0 else 'N/A'}\n")




