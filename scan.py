import re
import time
from dkbc import dk_process_barcode

DEBUG = False

iso_iec_15434_start = re.compile("^>?\[\)>(\{RS\})?[>]?[0-9]{2}{GS}")
# https://www.eurodatacouncil.org/images/documents/ANS_MH10.8.2%20_CM_20140512.pdf
ansi_mh10_8_2_item = re.compile("(?P<DI>[0-9]*[A-Z])(?P<value>[A-Za-z0-9\-\.]*)")

known_dis = {
    "K": "Customer PO Number",
    "1K": "Supplier Order Number",
    "10K": "Invoice Number",
    "P": "Part No.",
    "1P": "Supplier Part Number",
    "Q": "Quantity",
    "4L": "Country of Origin",
}

reduced_dis = ["P", "1P"]

def decode_barcode(barcode):
    # Check for valid code first
    if not iso_iec_15434_start.match(barcode):
        raise ValueError("Invalid barcode!")

    new_code = ['[)>\u001e06']
    fields = {}
    sections = barcode.split("{GS}")
    for section in sections[1:]:
        match = ansi_mh10_8_2_item.match(section)
        if match:
            di = match.group("DI")
            value = match.group("value")
            if di in reduced_dis:
                new_code.append(di + value)

            if di in known_dis:
                fields[known_dis[di]] = value
            elif DEBUG:
                print("NEW DI!", di, value)
        elif DEBUG:
            print("Invalid section", section)

    reduced_barcode = '\u001d'.join(new_code)

    return fields, reduced_barcode

barcode = input("Scan barcode:")

fields, simple_code = decode_barcode(barcode)


barcode = barcode.replace("{RS}", "\u241e")
barcode = barcode.replace("{GS}", "\u241d")
barcode = barcode.replace("{EOT}", "\x04")

# TODO - use other digikey api when scanning non-dk barcodes

digikey_data = dk_process_barcode(barcode)

if DEBUG:
    print(fields)
    print(digikey_data)

print(','.join([fields['Supplier Part Number'], digikey_data['Description'], simple_code]))
