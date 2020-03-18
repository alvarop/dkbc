# Digi-key Api Tools

These are just a few scripts I wrote to look up part information from Digi-key barcodes as well as look up parts by number. I then use this information to create new, simplified, barcodes for my inventory system.

## Getting Started
* Go to https://developer.digikey.com
* Register/login
* Register application
* Get client id and client secret
* Setup python environment (using virtualenv in this case) for examples
```
virtualenv venv
source venv/bin/activate
pip install -e .
```
* Run `python -m dkbc.post_code` and follow the instructions to get the authorization (you only have to do this once)

## Scanning barcodes
* Run `python examples/scan.py`

## Manually entering part numbers
* Run `python examples/search.py`
