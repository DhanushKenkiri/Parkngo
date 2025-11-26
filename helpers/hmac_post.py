import argparse
import json
import hmac
import hashlib
import requests
import os

def compute_sig(obj, key):
    data = {k: v for k, v in obj.items() if k != 'sig'}
    s = json.dumps(data, separators=(',', ':'), sort_keys=True)
    mac = hmac.new(key.encode('utf-8'), s.encode('utf-8'), hashlib.sha256)
    return mac.hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', required=True)
    p.add_argument('--file', required=True)
    p.add_argument('--key', default=os.environ.get('HMAC_KEY'))
    args = p.parse_args()
    if not args.key:
        print('HMAC key required via --key or HMAC_KEY env')
        return
    payload = json.load(open(args.file))
    sig = compute_sig(payload, args.key)
    payload['sig'] = sig
    r = requests.post(args.url, json=payload)
    print(r.status_code, r.text)

if __name__ == '__main__':
    main()
