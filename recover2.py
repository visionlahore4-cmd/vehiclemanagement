import os
import re
import json

def scan_leveldb_for_word(directory, keyword):
    if not os.path.exists(directory):
        return
    
    keyword_bytes = keyword.encode('utf-8')

    for file in os.listdir(directory):
        if file.endswith('.log') or file.endswith('.ldb'):
            filepath = os.path.join(directory, file)
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                    
                    # Find all occurrences of the keyword
                    idx = 0
                    while True:
                        idx = content.find(keyword_bytes, idx)
                        if idx == -1:
                            break
                            
                        # Found it! Extract surrounding bytes
                        start = max(0, idx - 500)
                        end = min(len(content), idx + 10000)
                        snippet = content[start:end].decode('utf-8', errors='ignore')
                        
                        # Try to find a JSON-like structure within the snippet
                        # Find the first '{' before the keyword and the last '}' after it
                        json_start = snippet.find('{')
                        json_end = snippet.rfind('}')
                        
                        if json_start != -1 and json_end != -1 and json_end > json_start:
                            possible_json = snippet[json_start:json_end+1]
                            # Try parsing
                            try:
                                # we might have captured multiple objects or partial objects. 
                                # Let's just save the snippet to a file to inspect manually
                                with open('found_snippets.txt', 'a', encoding='utf-8') as out:
                                    out.write(f"\n--- Found in {file} at index {idx} ---\n")
                                    out.write(possible_json[:2000]) # write first 2000 chars of the json
                            except Exception:
                                pass
                        
                        idx += 1
            except Exception as e:
                pass

app_data = os.environ.get('LOCALAPPDATA', '')
chrome_dir = os.path.join(app_data, r'Google\Chrome\User Data\Default\Local Storage\leveldb')
edge_dir = os.path.join(app_data, r'Microsoft\Edge\User Data\Default\Local Storage\leveldb')

# Clear old output
if os.path.exists('found_snippets.txt'):
    os.remove('found_snippets.txt')

print("Scanning for 'Motorcycle' in Chrome...")
scan_leveldb_for_word(chrome_dir, 'Motorcycle')
print("Scanning for 'Motorcycle' in Edge...")
scan_leveldb_for_word(edge_dir, 'Motorcycle')

if os.path.exists('found_snippets.txt'):
    print("Found some snippets! Check found_snippets.txt")
else:
    print("No snippets found at all.")
