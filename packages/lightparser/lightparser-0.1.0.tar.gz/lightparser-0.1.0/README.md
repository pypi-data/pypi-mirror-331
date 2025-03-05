# lightparser

A lightweight parsing library inspired by Scrapy.

## Installation

```bash
pip install lightparser
```

## Usage

```python
import requests
from lightparser import Selector, Item, yield_item

response = requests.get("https://example.com")
selector = Selector(response.text)

for product in selector.xpath('//div[@class="product"]'):
    item = Item()
    item["title"] = product.xpath(".//h2/text()").get()
    item["price"] = product.xpath(".//span[@class='price']/text()").get()
    yield_item(item)
```

## Command-line Usage

```bash
python my_script.py -o output.csv
```
