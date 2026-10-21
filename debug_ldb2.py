import os, json

ldb_dir = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Local Storage\leveldb')

filepath = os.path.join(ldb_dir, '000118.ldb')
with open(filepath, 'rb') as f:
    data = f.read()

key = b'vehiclehub_v5'
idx = data.find(key)
print(f'Key found at byte: {idx}')

# Dump surrounding bytes in text
start = max(0, idx - 5)
end = min(len(data), idx + 500)
chunk = data[start:end]
print('Raw context (text):')
try:
    print(chunk.decode('utf-8', errors='replace'))
except:
    print(repr(chunk))
