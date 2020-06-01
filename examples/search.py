import argparse
import re
import time
import os
import sys
from dkbc.dkbc import DKBC
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("--outfile", help="CSV output file")
parser.add_argument("--batch", action="store_true", help="Batch scan")
parser.add_argument("--debug", action="store_true", help="Debug mode")
args = parser.parse_args()

dkbc = DKBC()

scanning = True

while scanning:
    if args.batch:
        scanning = True
    else:
        scanning = False

    part_no = input("Enter Part Number: ")

    data = dkbc.get_part_details(part_no)

    if args.debug:
        pprint(data)

    if "HttpStatusCode" in data and data["HttpStatusCode"] == 404:
        print(data["Message"])
        print(data["Details"])
        continue

    if len(data["Products"]) == 0:
        print("Part not found...")
        sys.exit(-1)

    print(len(data["Products"]), "products found")
    
    products = []
    for product in data["Products"]:
        if product["MinimumOrderQuantity"] > 1:
            continue

        if "Digi-Reel" in product["Packaging"]["Value"]:
            continue

        products.append(product)
    
    for product in products:
        print("\t".join([product["ManufacturerPartNumber"], product["DigiKeyPartNumber"], product["ProductDescription"]]))

    details = data["Products"][0]

    print(details["ManufacturerPartNumber"] + " " + details["ProductDescription"])

    if args.outfile:
        new_code = [
            "[)>\u001e06",
            "P" + details["DigiKeyPartNumber"],
            "1P" + details["ManufacturerPartNumber"],
        ]

        # Add GS delimiters and EOT at the end
        reduced_barcode = "\u001d".join(new_code) + "\u0004"

        new_file = True

        if os.path.isfile(args.outfile):
            new_file = False

        with open(args.outfile, "a") as outfile:
            if new_file:
                outfile.write("MPN,DESCRIPTION,BARCODE\n")
            outfile.write(
                ",".join(
                    [
                        details["ManufacturerPartNumber"],
                        details["ProductDescription"],
                        reduced_barcode,
                    ]
                )
                + "\n"
            )
