#!/usr/bin/env python3
from datetime import datetime
import argparse
import json
import os
import pathlib
import re
import sys

import requests

script_path = pathlib.Path(__file__).parent.resolve()
EMAIL_API_KEY = os.environ.get("SEND_IN_BLUE_API_KEY", None)

parser = argparse.ArgumentParser("Price tracker")
parser.add_argument("-i", "--items", type=str, default=script_path/"items.json", help="Path to items.json")
parser.add_argument("-e", "--email", type=str, default=None, help="Email address at which to send notification")

def log_error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)

def send_email(item_name: str, message: str, email: str) -> bool:
    print("Sending email notification...")
    if EMAIL_API_KEY is None:
        log_error("Can't send email notification. No API key in environment variable SEND_IN_BLUE_API_KEY")
        return False

    r = requests.post("https://api.sendinblue.com/v3/smtp/email", 
                       headers={
                           "Accept": "application/json",
                           "api-key": EMAIL_API_KEY,
                           "Content-Type": "application/json"
                       },
                       json={
                           "sender": {
                               "name": "PriceWatcher",
                               "email": "price@watch.com"
                           },
                           "to": [
                               {
                                   "email": email,
                                   "name": "PriceWatcher Sub"
                               }
                           ],
                           "subject": f"PriceWatcher ALERT for '{item_name}'",
                           "htmlContent": message
                       })
    
    if r.status_code != 201:
        log_error(f"Could not send email for item '{item_name}'")
        print(f"   {r.text}")
        return False
    
    print("Email notification sent")
    return True

def main(args) -> None:
    print(f"Loading items to track from '{args.items}' at {datetime.now()}")

    with open(args.items, 'r') as f:
        items = json.load(f)
    
    if len(items) == 0:
        log_error("Database must contain at least 1 item to track")
        exit(1)
    
    for item in items:
        print(f"Verifying price for '{item['name']}' from '{item['url']}'...")
        r = requests.get(url=item['url'])
        if r.status_code != 200:
            log_error(f"Could not retrieve current price for item '{item['name']}'")
            log_error(f"HTTP Request FAILED")
            continue
        
        match = re.search(item['regex'], r.content.decode())
        if match is None:
            log_error(f"Could not retrieve current price for item '{item['name']}'")
            log_error("Failed to carve out price from Http response")
            continue
        
        current_price = float(match.group(1))
        print(f"    Price : {current_price}")
        
        if 'last_price' not in item or item['last_price'] > current_price:
            msg = f"New BEST price found for '{item['name']}' : {current_price} $"
            print(f">>> {msg}")
            if args.email is not None:
                send_email(item['name'], msg, args.email)
            item['last_price'] = current_price
            item['last_price_timestamp'] = datetime.now().strftime("%s")

    
    print("All items have been verified.")
    print("Updating database..")
    with open(args.items, 'w') as f:
        json.dump(items, f, indent=2)
    print("All done")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.email is not None and EMAIL_API_KEY is None and os.path.exists(script_path / "email.env"):
        with open(script_path / "email.env", 'r') as f:
            EMAIL_API_KEY = f.read().strip().split("=")[-1]

    if not os.path.exists(args.items):
        log_error(f"Can't load item list from file '{args.items}'. It doesn't exist")
        exit(1)

    main(args)

