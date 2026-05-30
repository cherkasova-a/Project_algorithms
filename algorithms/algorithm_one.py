import json
from datetime import datetime

def algorithm_one(raw_json_str, target_date_str):
    data = json.loads(raw_json_str)
    container = data['result']['containers'][0]

    events = container.get('events', [])
    events = events[::-1]
    
    target_dt = datetime.fromisoformat(target_date_str)
    phases = ['1. Export Prep', '2. Origin Port', '3. Transit', '4. Destination Port', '5. Final Delivery']
    number_of_phase = [1]
    all_labeled_steps = []
    current_phase_at_date = "No status"

    for event in events:
        status = str(event.get('status', '')).upper()
        event_date_raw = event.get('date')
        if event_date_raw:
            event_dt = datetime.fromisoformat(event_date_raw)
        else:
            event_dt = datetime.min
        
        if number_of_phase[-1] >= 4 and any(word in status for word in ['CUSTOMER', 'CONSIGNEE', 'DELIVERY', 'RETURNED', 'EMPTY RETURNED']):
            number_of_phase.append(5)
        elif 3<=number_of_phase[-1]<=4 and any(word in status for word in ['UNLOADED', 'DISCHARGED', 'GATE IN TO INBOUND', 'ARRIVAL']):
            number_of_phase.append(4)
        elif any(word in status for word in ['ON BOARD', 'DEPARTURE', 'TRANSIT', 'T/S']):
            number_of_phase.append(3)
        elif any(word in status for word in ['LOAD', 'GATE IN', 'TERMINAL', 'POL', 'RECEIVED AT']) and number_of_phase[-1] <= 2:
            number_of_phase.append(2)
        else:
            number_of_phase.append(number_of_phase[-1])
            
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

    current_phase_at_date = "Unable to determine"
    if final_timeline:
        first_start = datetime.fromisoformat(final_timeline[0]['start'])
        last_end = datetime.fromisoformat(final_timeline[-1]['end'])

        if target_dt < first_start:
            current_phase_at_date = "Before transportation"
        elif target_dt > last_end:
            current_phase_at_date = "Transportation is over"
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

