# Digi-key Api Tools

These are just a few scripts I wrote to look up part information from Digi-key barcodes as well as look up parts by number. I then use this information to create new, simplified, barcodes for my inventory system.

## Getting Started
* Go to https://developer.digikey.com
* Register/login
* Register application
* Get client id and client secret
* Setup python environment (using pipenv in this case) `pipenv install --three`
* Run `pipenv run python post_code.py` and follow the instructions to get the authorization

## Scanning barcodes
* Run `pipenv run python scan.py`

## Manually entering part numbers
* Run `pipenv run python search.py`
