import http.client
import yaml
import json
import requests
import re
import os
import time
import urllib
from pprint import pprint

DEFAULT_API_URL = "api.digikey.com"


class DKBC:
    def __init__(self, api_url=DEFAULT_API_URL, cfg_path="config.yml", debug=False):
        self.cfg = None
        self.cfg_path = cfg_path
        self.api_url = api_url
        self.debug = debug
        self.__update_config()

    def __update_config(self):
        if self.cfg is None:
            if os.path.isfile(self.cfg_path):
                with open(self.cfg_path, "r") as ymlfile:
                    self.cfg = yaml.safe_load(ymlfile)
            else:
                raise FileNotFoundError('Uh oh!! "{}" not found'.format(self.cfg_path))

        if int(self.cfg["token-expiration"]) < time.time():
            print("Token has expired, refreshing")
            self.__refresh_token()

        return self.cfg

    def __refresh_token(self):
        # https://api-portal.digikey.com/app_overview

        post_request = {
            "refresh_token": self.cfg["refresh-token"],
            "client_id": self.cfg["client-id"],
            "client_secret": self.cfg["client-secret"],
            "grant_type": "refresh_token",
        }

        # code  The authorization code returned from the initial request (See above example).
        # client_id This is the client id assigned to the application that you generated within the API Portal.
        # client_secret This is the client secret assigned to the application that you generated within the API Portal.
        # redirect_uri  This URI must match the redirect URI that you defined while creating your application within the API Portal.
        # grant_type    As defined in the OAuth 2.0 specification, this field must contain a value of authorization_code.

        request_url = "https://" + self.api_url + "/v1/oauth2/token"

        r = requests.post(request_url, data=post_request)
        response = r.json()

        if self.debug:
            print("Making request to")
            print(r.status_code)
            print(response)

        if r.status_code == 200:
            with open("old_config.yml", "w") as outfile:
                yaml.dump(self.cfg, outfile, default_flow_style=False)

            self.cfg["refresh-token"] = response["refresh_token"]
            self.cfg["access-token"] = response["access_token"]
            self.cfg["token-expiration"] = int(time.time()) + int(
                response["expires_in"]
            )
            with open(self.cfg_path, "w") as outfile:
                yaml.dump(self.cfg, outfile, default_flow_style=False)
        else:
            print("ERROR")

    def process_barcode(self, barcode):
        barcode_1d_re = re.compile("^[0-9]+$")

        if barcode_1d_re.match(barcode):
            return self.process_1d_barcode(barcode)
        else:
            return self.process_2d_barcode(barcode)

    def process_1d_barcode(self, barcode):

        self.__update_config()

        conn = http.client.HTTPSConnection(self.api_url)

        headers = {
            "x-DIGIKEY-client-id": self.cfg["client-id"],
            "authorization": "Bearer " + self.cfg["access-token"],
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

    def process_2d_barcode(self, barcode):

        self.__update_config()

        conn = http.client.HTTPSConnection(self.api_url)

        headers = {
            "x-DIGIKEY-client-id": self.cfg["client-id"],
            "authorization": "Bearer " + self.cfg["access-token"],
            "content-type": "application/json",
            "accept": "application/json",
        }

        conn.request(
            "GET",
            "/Barcoding/v3/Product2DBarcodes/" + urllib.parse.quote(barcode, safe=''),
            None,
            headers,
        )

        res = conn.getresponse()
        data = json.loads(res.read())

        if "httpMessage" in data and data["httpMessage"] == "Unauthorized":
            print("Unauthorized! Need to refresh token.")

        return data

    def get_part_details(self, part_no):

        self.__update_config()

        conn = http.client.HTTPSConnection(self.api_url)

        # TODO - escape part_no quotes
        payload = '{"Keywords": "' + part_no + '","RecordCount": "50"}'

        headers = {
            "x-DIGIKEY-client-id": self.cfg["client-id"],
            "authorization": "Bearer " + self.cfg["access-token"],
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
