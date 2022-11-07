# price-tracker
Small webscraper to track price accross the web

## Installation
Install dependencies : 
```
pip install requests
```

## Configuration
### Items
Create a file named `items.json` at the root of the repo and add items you want to track. \
(You can use `--items` argument to change the path) \
Example : 
```
[
  {
    "name": "Dell 27 Inch 4K Monitor",
    "url": "https://www.dell.com/en-ca/shop/dell-27-4k-uhd-monitor-s2721qs/apd/210-axlg/monitors-monitor-accessories",
    "regex": "<div class=\"ps-dell-price ps-simplified\" data-testid=sharedPSPDellPrice>CAD \\$([0-9]+\\.?[0-9]*)</div>"
  },
  {
    "name": "Item 2",
    "url": "Url/to/product/page",
    "regex": "pattern/to/capture/price"
  },
]
```
> The price must be captured in the first group of the `regex`.

### Email notifications
This script use [SendInBlue](https://www.sendinblue.com/) service to send email notifications. \
First thing I found out of Google that had a reasonable free tier. \
You simply need to create an account and generate an API key.


You can then store this API key in `SEND_IN_BLUE_API_KEY` environment variable \
or \
`email.env` file at the root of the repo :
```
SEND_IN_BLUE_API_KEY={your_api_key}
```

## Usage
```
usage: Price tracker [-h] [-i ITEMS] [-e EMAIL]

optional arguments:
  -h, --help            show this help message and exit
  -i ITEMS, --items ITEMS
                        Path to items.json
  -e EMAIL, --email EMAIL
                        Email address at which to send notification
```

You can use `cron` jobs to run this script everyday.

`Run price-tracker every day at 9:00` : 
```
# m h  dom mon dow   command
0 9 * * * python /path/to/price-tracker.py -e your@email.com
```
