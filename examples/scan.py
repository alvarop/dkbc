import argparse
import re
import time
import os
from dkbc.dkbc import DKBC

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

parser.add_argument("--rs", help='Record separator. Default "{RS}"', default="{RS}")
parser.add_argument("--gs", help='Group separator. Default "{GS}"', default="{GS}")
parser.add_argument(
    "--eot", help='End of transmission. Default "{EOT}"', default="{EOT}"
)

args = parser.parse_args()

dkbc = DKBC()


def decode_2d_barcode(barcode, rs_str, gs_str, eot_str):
    iso_iec_15434_start = re.compile(
        "^>?\[\)>({})?[>]?[0-9]{{2}}{}".format(rs_str, gs_str)
    )

    # https://www.eurodatacouncil.org/images/documents/ANS_MH10.8.2%20_CM_20140512.pdf
    ansi_mh10_8_2_item = re.compile("(?P<DI>[0-9]*[A-Z])(?P<value>[A-Za-z0-9\-\.\ ]*)")

    # Check for valid code first
    if not iso_iec_15434_start.match(barcode):
        raise ValueError("Invalid barcode!")

    fields = {}
    sections = barcode.split(gs_str)
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
        # Try to decode barcode to see if it's a valid 2d barcode
        decode_2d_barcode(barcode, gs_str=args.gs, rs_str=args.rs, eot_str=args.eot)

        # Convert escape character strings back into raw format for digikey
        barcode = barcode.replace(args.rs, "\x1e")
        barcode = barcode.replace(args.gs, "\x1d")
        barcode = barcode.replace(args.eot, "\x04")

        digikey_data = dkbc.process_barcode(barcode)
    except ValueError:
        digikey_data = dkbc.process_barcode(barcode)

    if args.debug:
        print(digikey_data)

    new_code = [
        "[)>\x1e06",
        "1P" + digikey_data["ManufacturerPartNumber"],
        "P" + digikey_data["DigiKeyPartNumber"],
    ]

    # Add GS delimiters and EOT at the end
    reduced_barcode = "\x1d".join(new_code) + "\x04"

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
