import os
import re
import json

def scan_leveldb(directory):
    if not os.path.exists(directory):
        return []
    
    found_data = []
    # Regex to find JSON arrays of vehicles that have id, name, type, plate, etc.
    # Because leveldb strings might have binary prefixes, we just look for something that starts with {"settings": and has "vehicles":
    # Or just look for any valid JSON state of vehiclehub_v5
    pattern = re.compile(b'(\\{"settings":.*?"vehicles":\\[.*?\\]\\})')
    pattern2 = re.compile(b'(\\{"vehicles":\\[.*?"drivers":\\[.*?\\})')

    for file in os.listdir(directory):
        if file.endswith('.log') or file.endswith('.ldb'):
            filepath = os.path.join(directory, file)
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                    
                    matches = pattern.findall(content)
                    matches.extend(pattern2.findall(content))
                    
                    for match in matches:
                        try:
                            # Try decoding as utf-8
                            text = match.decode('utf-8', errors='ignore')
                            # See if it parses as JSON
                            parsed = json.loads(text)
                            if 'vehicles' in parsed and isinstance(parsed['vehicles'], list):
                                found_data.append(parsed)
                        except Exception as e:
                            pass
            except Exception as e:
                pass
    return found_data

app_data = os.environ.get('LOCALAPPDATA', '')
chrome_dir = os.path.join(app_data, r'Google\Chrome\User Data\Default\Local Storage\leveldb')
edge_dir = os.path.join(app_data, r'Microsoft\Edge\User Data\Default\Local Storage\leveldb')

print("Scanning Chrome LevelDB...")
chrome_data = scan_leveldb(chrome_dir)
print("Scanning Edge LevelDB...")
edge_data = scan_leveldb(edge_dir)

all_data = chrome_data + edge_data

if not all_data:
    print("No data found in deep scan.")
else:
    # Find the one with the most vehicles and bills
    best_data = None
    max_score = -1
    
    for d in all_data:
        score = len(d.get('vehicles', [])) + len(d.get('bills', [])) + len(d.get('fuel', []))
        if score > max_score:
            max_score = score
            best_data = d
            
    if best_data and max_score > 0:
        with open('recovered_backup.json', 'w', encoding='utf-8') as f:
            json.dump(best_data, f, indent=2)
        print(f"SUCCESS: Recovered data with {len(best_data.get('vehicles', []))} vehicles, {len(best_data.get('bills', []))} bills.")
    else:
        print("Data found but it was empty.")
