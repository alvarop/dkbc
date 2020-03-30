import http.client
import yaml
import json
import requests
import re
import time
import urllib
from pprint import pprint

API_URL = "api.digikey.com"
DEBUG = False


def __get_cfg():
    cfg = None
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    if int(cfg["token-expiration"]) < time.time():
        print("Token has expired, refreshing")
        cfg = refresh_token(cfg)

    return cfg


def refresh_token(cfg):
    # https://api-portal.digikey.com/app_overview

    post_request = {
        "refresh_token": cfg["refresh-token"],
        "client_id": cfg["client-id"],
        "client_secret": cfg["client-secret"],
        "grant_type": "refresh_token",
    }

    # code  The authorization code returned from the initial request (See above example).
    # client_id This is the client id assigned to the application that you generated within the API Portal.
    # client_secret This is the client secret assigned to the application that you generated within the API Portal.
    # redirect_uri  This URI must match the redirect URI that you defined while creating your application within the API Portal.
    # grant_type    As defined in the OAuth 2.0 specification, this field must contain a value of authorization_code.

    request_url = "https://" + API_URL + "/v1/oauth2/token"

    r = requests.post(request_url, data=post_request)
    response = r.json()

    if DEBUG:
        print("Making request to")
        print(r.status_code)
        print(response)

    if r.status_code == 200:
        with open("old_config.yml", "w") as outfile:
            yaml.dump(cfg, outfile, default_flow_style=False)

        cfg["refresh-token"] = response["refresh_token"]
        cfg["access-token"] = response["access_token"]
        cfg["token-expiration"] = int(time.time()) + int(response["expires_in"])
        with open("config.yml", "w") as outfile:
            yaml.dump(cfg, outfile, default_flow_style=False)
    else:
        print("ERROR")

    return cfg


def dk_process_barcode(barcode):
    barcode_1d_re = re.compile("^[0-9]+$")

    if barcode_1d_re.match(barcode):
        return dk_process_1d_barcode(barcode)
    else:
        return dk_process_2d_barcode(barcode)


def dk_process_1d_barcode(barcode):

    cfg = __get_cfg()

    conn = http.client.HTTPSConnection(API_URL)

    headers = {
        "x-DIGIKEY-client-id": cfg["client-id"],
        "authorization": "Bearer " + cfg["access-token"],
        "content-type": "application/json",
        "accept": "application/json",
    }

    conn.request(
        "GET",
        "/Barcoding/v3/ProductBarcodes/" + urllib.parse.quote(barcode),
        None,
        headers,
    )

    res = conn.getresponse()
    data = json.loads(res.read())

    if "httpMessage" in data and data["httpMessage"] == "Unauthorized":
        print("Unauthorized! Need to refresh token.")

    return data


def dk_process_2d_barcode(barcode):

    cfg = __get_cfg()

    conn = http.client.HTTPSConnection(API_URL)

    headers = {
        "x-DIGIKEY-client-id": cfg["client-id"],
        "authorization": "Bearer " + cfg["access-token"],
        "content-type": "application/json",
        "accept": "application/json",
    }

    conn.request(
        "GET",
        "/Barcoding/v3/Product2DBarcodes/" + urllib.parse.quote(barcode),
        None,
        headers,
    )

    res = conn.getresponse()
    data = json.loads(res.read())

    if "httpMessage" in data and data["httpMessage"] == "Unauthorized":
        print("Unauthorized! Need to refresh token.")

    return data


def dk_get_part_details(part_no):

    cfg = __get_cfg()

    conn = http.client.HTTPSConnection(API_URL)

    # TODO - escape part_no quotes
    payload = '{"Keywords": "' + part_no + '","RecordCount": "10"}'

    headers = {
        "x-DIGIKEY-client-id": cfg["client-id"],
        "authorization": "Bearer " + cfg["access-token"],
        "content-type": "application/json",
        "accept": "application/json",
    }

    conn.request(
        "POST", "/Search/v3/Products/Keyword", payload.encode("utf-8"), headers
    )

    res = conn.getresponse()

    data = json.loads(res.read().decode("utf-8"))

    if "httpMessage" in data and data["httpMessage"] == "Unauthorized":
        print("Unauthorized! Need to refresh token.")

    return data
