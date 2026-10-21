import os, json, re, struct

ldb_dir = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Local Storage\leveldb')

def try_extract(filepath):
    results = []
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # Search for vehiclehub key
        key = b'vehiclehub_v5'
        idx = 0
        while True:
            idx = data.find(key, idx)
            if idx == -1:
                break
            
            # Try to find JSON after this position  
            search_area = data[idx:idx+500000]
            
            # Look for JSON patterns - the actual value might be encoded
            # Try reading bytes after the key name
            after_key = data[idx + len(key):]
            
            # Find { char which starts JSON
            json_candidates = []
            for i in range(min(100, len(after_key))):
                if after_key[i:i+1] == b'{':
                    json_candidates.append(idx + len(key) + i)
            
            for jstart in json_candidates:
                chunk = data[jstart:]
                # Try to decode and find valid JSON
                try:
                    text = chunk.decode('utf-8', errors='replace')
                    # Find matching closing brace
                    depth = 0
                    end = -1
                    for ci, ch in enumerate(text[:200000]):
                        if ch == '{': depth += 1
                        elif ch == '}': 
                            depth -= 1
                            if depth == 0:
                                end = ci + 1
                                break
                    if end > 100:
                        candidate = text[:end]
                        parsed = json.loads(candidate)
                        if 'vehicles' in parsed:
                            results.append(parsed)
                except:
                    pass
            idx += 1
    except Exception as e:
        print(f"Error: {e}")
    return results

all_results = []
for f in os.listdir(ldb_dir):
    if f.endswith('.ldb') or f.endswith('.log'):
        r = try_extract(os.path.join(ldb_dir, f))
        if r:
            print(f"Found {len(r)} datasets in {f}")
            all_results.extend(r)

if all_results:
    best = max(all_results, key=lambda x: len(x.get('vehicles',[])) + len(x.get('bills',[])) + len(x.get('fuel',[])))
    print(f"Best dataset: {len(best.get('vehicles',[]))} vehicles, {len(best.get('fuel',[]))} fuel, {len(best.get('bills',[]))} bills, {len(best.get('maintenance',[]))} maintenance")
    with open('recovered_data.json', 'w', encoding='utf-8') as fout:
        json.dump(best, fout, ensure_ascii=False, indent=2)
    print("Saved to recovered_data.json")
else:
    print("No valid JSON data found")
