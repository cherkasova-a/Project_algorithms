import json
from datetime import datetime
lish=set()

def algorithm_ALL(raw_json_str, target_date_str):
    data = json.loads(raw_json_str)
    container = data['result']['containers'][0]

    events = container.get('events', [])
    events = events[::-1]
    
    target_dt = datetime.fromisoformat(target_date_str)
    phases = ['1. Export Prep', '2. Origin Port', '3. Transit', '4. Destination Port', '5. Final Delivery']
    number_of_phase = [1]
    all_labeled_steps = []
    current_phase_at_date = "No status"
    status_word_2 = ['CGI', 'LTS', 'CLL', 'CPS']
    status_word_3 = ['BTS', 'CDT', 'CLT', 'VDL', 'VDT', 'VAT', 'CDT', 'TSD']
    status_word_4 = ['CDD', 'VAD']
    status_word_5 = ['CEP', 'CER', 'CGO', 'LTS', 'CDC']


    for event in events:
        status = str(event.get('status_code', '')).upper()


        event_date_raw = event.get('date')
        if event_date_raw:
            event_dt = datetime.fromisoformat(event_date_raw)
        else:
            event_dt = datetime.min


        if number_of_phase[-1]>=4 and (status in status_word_5):
            number_of_phase.append(5)
        elif number_of_phase[-1]>=3 and (status in status_word_4):
            number_of_phase.append(4)
        elif (status in status_word_3):
            number_of_phase.append(3)
        elif (status in status_word_2) and number_of_phase[-1]<=2:
            number_of_phase.append(2)
        else:
            number_of_phase.append(number_of_phase[-1])
            lish.add(status)
        

        p = phases[number_of_phase[-1]-1]
            
        all_labeled_steps.append({'phase': p, 'date': event['date'], 'dt': event_dt})

    raw_intervals = []

    for p_name in phases:
        if p_name == '4. Destination Port':
            continue
            
        p_steps = [s for s in all_labeled_steps if s['phase'] == p_name and s['date'] is not None]
        if p_steps:
            raw_intervals.append({
                'phase': p_name, 
                'start': p_steps[0]['date'], 
                'end': p_steps[-1]['date']
            })

        if p_name == '3. Transit':
            transit_steps = p_steps
            dest_steps = [s for s in all_labeled_steps if s['phase'] == '4. Destination Port' and s['date'] is not None]
            if dest_steps:
                last_transit_dt = transit_steps[-1]['dt'] if transit_steps else datetime.min
                final_dest_steps = [s for s in dest_steps if s['dt'] >= last_transit_dt]
                if final_dest_steps:
                    raw_intervals.append({
                        'phase': '4. Destination Port',
                        'start': final_dest_steps[0]['date'],
                        'end': final_dest_steps[-1]['date']
                    })

    final_timeline = []
    for i in range(len(raw_intervals)):
        current_int = raw_intervals[i].copy()
        if i < len(raw_intervals) - 1:
            current_int['end'] = raw_intervals[i+1]['start']
        final_timeline.append(current_int)

    current_phase_at_date = "Не определено"
    if final_timeline:
        first_start = datetime.fromisoformat(final_timeline[0]['start'])
        last_end = datetime.fromisoformat(final_timeline[-1]['end'])

        if target_dt < first_start:
            current_phase_at_date = "Путь еще не начат"
        elif target_dt > last_end:
            current_phase_at_date = "Путь уже закончен"
        else:
            for interval in final_timeline:
                if datetime.fromisoformat(interval['start']) <= target_dt < datetime.fromisoformat(interval['end']):
                    current_phase_at_date = interval['phase']
                    break
            if target_dt == last_end:
                current_phase_at_date = final_timeline[-1]['phase']

    return {
        "current_status": current_phase_at_date,
        "history_intervals": final_timeline
    }, number_of_phase

#raw_json = '{"result":{"summary":{"pod":{"date":"2026-04-30T06:00:00","location":0},"origin":{"date":null,"location":null},"destination":{"date":null,"location":null},"company":{"name":"CMA-CGM"},"pol":{"date":"2026-03-01T06:00:00","location":3}},"locations":[{"country":"India","country_iso_code":"IN","lng":69.565444,"locode":"INMUN","name":"Mundra","id":0,"state":null,"lat":22.748083},{"country":"China","country_iso_code":"CN","lng":120.974342,"locode":"CNNGB","name":"Ningbo","id":1,"state":null,"lat":30.130897},{"country":"China","country_iso_code":"CN","lng":122.027386,"locode":"CNNBG","name":"Ningbo","id":2,"state":null,"lat":29.882816},{"country":"Ecuador","country_iso_code":"EC","lng":-80.25130945,"locode":"ECPSJ","name":"Posorja","id":3,"state":null,"lat":-2.685515665}],"containers":[{"number":"","type":null,"events":[{"date":"2026-04-30T06:00:00","actual":false,"status_code":"VAD","vessel":"APL YANGSHAN","location":0,"status":"Vessel Arrival","voyage":"0FFH8E1MA"},{"date":"2026-04-10T04:00:00","actual":false,"status_code":"UNK","vessel":"APL YANGSHAN","location":1,"status":"Vessel Departure","voyage":"0FFH7W1MA"},{"date":"2026-04-01T13:00:00","actual":false,"status_code":"VAT","vessel":"CMA CGM THAMES","location":2,"status":"Vessel Arrival","voyage":"0MH27E1MA"},{"date":"2026-03-01T06:00:00","actual":false,"status_code":"VDL","vessel":"CMA CGM THAMES","location":3,"status":"Vessel Departure","voyage":"0MH1QW1MA"}]}],"shipment_status":"IN_TRANSIT"}}'
raw_json = '{"result":{"summary":{"pod":{"date":"2026-01-17T21:05:00","location":1},"origin":{"date":null,"location":null},"destination":{"date":null,"location":null},"company":{"name":"CMA-CGM"},"pol":{"date":"2026-01-03T09:12:00","location":2}},"locations":[{"country":"United States of America","country_iso_code":"US","lng":-80.1688068,"locode":"USMIA","name":"Miami","id":0,"state":null,"lat":25.7733062},{"country":"United States of America","country_iso_code":"US","lng":-80.1237526,"locode":"USPEF","name":"Port Everglades","id":1,"state":null,"lat":26.0715113},{"country":"Chile","country_iso_code":"CL","lng":-71.616227,"locode":"CLSAI","name":"San Antonio","id":2,"state":null,"lat":-33.591403},{"country":"Chile","country_iso_code":"CL","lng":-71.556669444,"locode":"CLSAI","name":"San Antonio","id":3,"state":null,"lat":-33.4067167}],"containers":[{"number":"CGMU5320000","type":"45R1","events":[{"date":"2026-01-21T11:27:00","actual":true,"status_code":"CER","vessel":null,"location":0,"status":"Container Empty Returned","voyage":null},{"date":"2026-01-20T14:30:00","actual":true,"status_code":"CGO","vessel":null,"location":1,"status":"Gate out to Consignee","voyage":null},{"date":"2026-01-17T22:04:00","actual":true,"status_code":"VAD","vessel":"CAPE HELLAS","location":1,"status":"Vessel Arrival","voyage":"0LI1FS1MA"},{"date":"2026-01-17T21:30:00","actual":true,"status_code":"CDD","vessel":"CAPE HELLAS","location":1,"status":"Discharged","voyage":"0LI1FS1MA"},{"date":"2026-01-03T09:12:00","actual":true,"status_code":"VDL","vessel":"CAPE HELLAS","location":2,"status":"Vessel Departure","voyage":"0LI14N1MA"},{"date":"2026-01-03T05:54:00","actual":true,"status_code":"CLL","vessel":"CAPE HELLAS","location":2,"status":"Loaded on board","voyage":"0LI14N1MA"},{"date":"2025-12-30T17:06:00","actual":true,"status_code":"CGI","vessel":null,"location":2,"status":"Gate in at Port terminal","voyage":null},{"date":"2025-12-29T17:59:00","actual":true,"status_code":"CEP","vessel":null,"location":3,"status":"Empty Picked-up at Depot","voyage":null}]}],"shipment_status":"DELIVERED"}}'
#проверка файла
"""
with open('D:\code\CMACGM.csv', 'r', encoding='utf-8') as file:
    i=1
    for line in file:
        data = line.strip().replace('""', '"')
        data=data[1:][:-1]
        dop=data
        if (3 or 4 or 5) not in algorithm_ALL(data, "2026-02-22T21:00:00")[-1]:
            #print(algorithm_cma_cgm(data, "2026-02-22T21:00:00"))
            data=json.loads(data)['result']['containers'][0]['events']
            #if len(data)>2:
                #print(list(event['status'] for event in data))
                #print(dop)
        #if i>500:
            #break
        i+=1
print('OK',i)
print(algorithm_ALL(raw_json, "2026-02-22T21:00:00")[-1])
"""