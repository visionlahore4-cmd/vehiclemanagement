import os, json, snappy, struct

ldb_dir = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Local Storage\leveldb')

def read_leveldb_file(filepath):
    results = {}
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # Search for the vehiclehub_v5 key
        key = b'vehiclehub_v5'
        idx = 0
        while True:
            idx = data.find(key, idx)
            if idx == -1:
                break
            
            # After the key, try to find the value
            # In LevelDB .ldb files, values can be snappy-compressed
            after = data[idx + len(key):]
            
            # Try snappy decompression on chunks after the key
            for offset in range(1, 200):
                if offset >= len(after):
                    break
                chunk = after[offset:]
                try:
                    decompressed = snappy.decompress(chunk[:min(500000, len(chunk))])
                    text = decompressed.decode('utf-8', errors='replace')
                    if '"vehicles"' in text:
                        print(f"SUCCESS! Snappy decompressed at offset {offset}")
                        print(f"Preview: {text[:300]}")
                        # Try to parse JSON
                        json_start = text.find('{')
                        if json_start >= 0:
                            parsed = json.loads(text[json_start:])
                            results['data'] = parsed
                        break
                except:
                    pass
            
            idx += 1
    except Exception as e:
        print(f"Error in {filepath}: {e}")
    return results

print("Scanning LDB files with Snappy decompression...")
for fname in os.listdir(ldb_dir):
    if fname.endswith('.ldb') or fname.endswith('.log'):
        fpath = os.path.join(ldb_dir, fname)
        r = read_leveldb_file(fpath)
        if r and 'data' in r:
            d = r['data']
            print(f"In {fname}: {len(d.get('vehicles',[]))} vehicles, {len(d.get('fuel',[]))} fuel, {len(d.get('bills',[]))} bills")
            with open('recovered_data.json', 'w', encoding='utf-8') as out:
                json.dump(d, out, ensure_ascii=False, indent=2)
            print("SAVED to recovered_data.json!")

print("Scan complete")
