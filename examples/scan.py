import argparse
import re
import time
import os
from dkbc.dkbc import DKBC


iso_iec_15434_start = re.compile("^>?\[\)>(\{RS\})?[>]?[0-9]{2}{GS}")
# https://www.eurodatacouncil.org/images/documents/ANS_MH10.8.2%20_CM_20140512.pdf
ansi_mh10_8_2_item = re.compile("(?P<DI>[0-9]*[A-Z])(?P<value>[A-Za-z0-9\-\.\ ]*)")

known_dis = {
    "K": "Customer PO Number",
    "1K": "Supplier Order Number",
    "10K": "Invoice Number",
    "P": "Part No.",
    "1P": "Supplier Part Number",
    "Q": "Quantity",
    "4L": "Country of Origin",
}


parser = argparse.ArgumentParser()
parser.add_argument("--outfile", help="CSV output file")
parser.add_argument("--batch", action="store_true", help="Batch scan")
parser.add_argument("--debug", action="store_true", help="Debug mode")
args = parser.parse_args()

dkbc = DKBC() 

def decode_barcode(barcode):
    # Check for valid code first
    if not iso_iec_15434_start.match(barcode):
        raise ValueError("Invalid barcode!")

    fields = {}
    sections = barcode.split("{GS}")
    for section in sections[1:]:
        match = ansi_mh10_8_2_item.match(section)
        if match:
            di = match.group("DI")
            value = match.group("value")

            if di in known_dis:
                fields[known_dis[di]] = value
            elif args.debug:
                print("NEW DI!", di, value)
        elif args.debug:
            print("Invalid section", section)

    return fields


scanning = True

while scanning:
    if args.batch:
        scanning = True
    else:
        scanning = False

    barcode = input("Scan barcode:")

    try:
        fields = decode_barcode(barcode)

        # TODO - use other digikey api when scanning non-dk barcodes
        barcode = barcode.replace("{RS}", "\u241e")
        barcode = barcode.replace("{GS}", "\u241d")
        barcode = barcode.replace("{EOT}", "\x04")
        digikey_data = dkbc.process_barcode(barcode)
    except ValueError:
        fields = None
        simple_code = None
        digikey_data = dkbc.process_barcode(barcode)

    new_code = [
        "[)>\u001e06",
        "1P" + digikey_data["ManufacturerPartNumber"],
        "P" + digikey_data["DigiKeyPartNumber"],
    ]

    # Add GS delimiters and EOT at the end
    reduced_barcode = "\u001d".join(new_code) + "\u0004"

    if args.debug:
        print(digikey_data)
        if fields:
            print(fields)

    if args.outfile:
        new_file = True

        if os.path.isfile(args.outfile):
            new_file = False

        with open(args.outfile, "a") as outfile:
            if new_file:
                outfile.write("MPN,DESCRIPTION,BARCODE\n")
            outfile.write(
                ",".join(
                    [
                        digikey_data["ManufacturerPartNumber"],
                        digikey_data["ProductDescription"],
                        reduced_barcode,
                    ]
                )
                + "\n"
            )

    if "ProductDescription" in digikey_data:
        description = digikey_data["ProductDescription"]
    else:
        description = ""

    print(digikey_data["ManufacturerPartNumber"] + " " + description)
