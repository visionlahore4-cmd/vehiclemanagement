import os, json

ldb_dir = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Local Storage\leveldb')

for fname in os.listdir(ldb_dir):
    if not (fname.endswith('.ldb') or fname.endswith('.log')):
        continue
    fpath = os.path.join(ldb_dir, fname)
    try:
        with open(fpath, 'rb') as f:
            data = f.read()
        text = data.decode('utf-8', errors='replace')
        
        # Look for JSON with vehicles array
        idx = text.find('"vehicles":[{')
        if idx == -1:
            idx = text.find('"vehicles": [{')
        if idx != -1:
            # Try to extract JSON from before this point
            # Find opening brace
            start = max(0, idx - 200)
            chunk = text[start:idx+50000]
            # Try to find the start of the outer JSON object
            for si in range(200, -1, -1):
                if si < len(chunk) and chunk[si] == '{':
                    try:
                        # Try to parse from here
                        candidate = chunk[si:]
                        # Find JSON end
                        depth = 0
                        end = -1
                        in_str = False
                        escape = False
                        for ci, ch in enumerate(candidate[:300000]):
                            if escape: escape = False; continue
                            if ch == '\\\\': escape = True; continue
                            if ch == '"' and not escape: in_str = not in_str; continue
                            if in_str: continue
                            if ch == '{': depth += 1
                            elif ch == '}':
                                depth -= 1
                                if depth == 0:
                                    end = ci + 1
                                    break
                        if end > 500:
                            parsed = json.loads(candidate[:end])
                            if 'vehicles' in parsed and len(parsed['vehicles']) > 0:
                                v_count = len(parsed.get('vehicles',[]))
                                f_count = len(parsed.get('fuel',[]))
                                b_count = len(parsed.get('bills',[]))
                                print(f"FOUND in {fname}: {v_count} vehicles, {f_count} fuel, {b_count} bills")
                                with open('recovered_data.json', 'w', encoding='utf-8') as out:
                                    json.dump(parsed, out, ensure_ascii=False, indent=2)
                                print("Saved!")
                    except:
                        pass
    except Exception as e:
        pass

print("Done scanning")
