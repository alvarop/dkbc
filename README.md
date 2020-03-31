# Digi-key Api Tools

These are just a few scripts I wrote to look up part information from Digi-key barcodes as well as look up parts by number. I then use this information to create new, simplified, barcodes for my inventory system.

## Getting Started
* Go to https://developer.digikey.com
* Register/login
* Register application
  * You'll need to register an organization first (https://developer.digikey.com/teams)
  * Once created, click on "production apps"
  * Create production app
  * You can use https://alvarop.com/dkbc/dk_oauth.html as an OAuth Callback URL
  * Select Product Information and Barcode support
* Click on the new application to get client id and client secret from newly created production app
* Setup python environment (using [virtualenv](https://virtualenv.pypa.io) in this case) for examples
```
virtualenv venv
source venv/bin/activate
pip install -e .
```
* Run `python -m dkbc.authorize` and follow the instructions to get the authorization (you only have to do this once)

## Scanning barcodes
* Run `python examples/scan.py`

## Manually entering part numbers
* Run `python examples/search.py`
