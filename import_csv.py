import requests

api_key="6RDGH9fMHHTvCiQbmBKRnat77Y49vS0p"



def enrolment_check(cycle_startdate, cycle_enddate, idnr, saqa_id, enrolled, api_key):
    url = "https://studdup.tvet.org.za/enrolment-check"
    payload = {
        "idnr": idnr,
        "cycle_startdate": cycle_startdate,
        "cycle_enddate": cycle_enddate,
        "saqa_id": saqa_id,
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
    results_file.write(f"IdNr,CycleStart,CycleEnd,SaqaId,Enrolled,Result,Duplicated\n")
    # Assuming the second line contains the data
    for line in lines[1:]:
        data = line.strip().split(',')
        cycle_startdate = data[0]
        cycle_enddate = data[1]
        idnr = data[2]
        saqa_id = data[3]
        enrolled = data[4]
        result = enrolment_check(cycle_startdate, cycle_enddate, idnr, saqa_id, enrolled, api_key)
        # Write the result to the file
        if not result:
            result ="Error - No response from server"
        elif isinstance(result, tuple):
            result, duplicates = result
        
        print(f"IDNR: {idnr}, Start: {cycle_startdate}, End: {cycle_enddate}, SAQA ID: {saqa_id}, Enrolled: {enrolled}, Result: {result}, Duplicated: {duplicates if len(duplicates)>0 else 'N/A'}")
        results_file.write(f"{idnr},{cycle_startdate},{cycle_enddate},{saqa_id},{enrolled},{result},{duplicates if len(duplicates)>0 else 'N/A'}\n")




