import argparse
import pandas
from pandas import DataFrame
from pandasql import sqldf
import pyap
from dataclasses import dataclass
from nameparser import parse as parse_name

"""
We're using these CSV columns in the destination, in order:
GSS_NUM,FNAME,LNAME,CITY,STATE,PHONE_NUM,NSS_NUM,EMAIL,user_login,role,display_name
"""
destination_column_names = [
    "GSS_NUM",
    "FNAME",
    "MNAME",
    "LNAME",
    "CITY",
    "STATE",
    "PHONE_NUM",
    "NSS_NUM",
    "EMAIL",
    "user_login",
    "role",
    "display_name"
]

arg_parse_args = [
    {
        "name_or_flags": "--incoming-file-name",
        "type": str,
        "required": True,
        "help": "Specify the CSV file that new records shall be selected from."
    },
    {
        "name_or_flags": "--comparison-file-name",
        "type": str,
        "required": True,
        "help": "Specify the CSV file that new records checked against."
    },
    {
        "name_or_flags": "--destination-file-name",
        "type": str,
        "required": True,
        "help": "Specify the CSV file that new records will be written to."
    },
    {
        "name_or_flags": "--write-new-truth-to",
        "type": str,
        "required": True,
        "help": "A CSV to write your consolidate truth to."
    },
    {
        "name_or_flags": "--GSS-num-start-range",
        "type": int,
        "required": True,
        "help": "A GSS Number will be added to each record. This specifies what the first GSS number will be."
    },
    {
        "name_or_flags": "--incoming-full-name-header",
        "type": str,
        "required": False,
        "help": "Specify the column header if the member's full name is being passed in one string."
    },
    {
        "name_or_flags": "--incoming-first-name-header",
        "type": str,
        "required": False,
        "help": "Specify the column that the member's first name will be in."
    },
    {
        "name_or_flags": "--incoming-middle-name-header",
        "type": str,
        "required": False,
        "help": "Specify the column that the member's middle name will be in."
    },
    {
        "name_or_flags": "--incoming-last-name-header",
        "type": str,
        "required": False,
        "help": "Specify the column that the member's last name will be in."
    },
    {
        "name_or_flags": "--incoming-city",
        "type": str,
        "required": False,
        "help": "Specify the column that the member's city will be in."
    },
    {
        "name_or_flags": "--incoming-state",
        "type": str,
        "required": False,
        "help": "Specify the column that the member's state will be in."
    },
    {
        "name_or_flags": "--incoming-address",
        "type": str,
        "required": False,
        "help": "Specify the column the member's address will be in.\nNote this overrides --incoming-city and --incoming-state arguments"
    },
    {
        "name_or_flags": "--incoming-phone",
        "type": str,
        "required": False,
        "help": "Specify the column that the member's phone number will be in."
    },
    {
        "name_or_flags": "--incoming-nss-number",
        "type": str,
        "required": True,
        "help": "Specify the column that the member's NSS number will be in."
    },
    {
        "name_or_flags": "--incoming-email",
        "type": str,
        "required": True,
        "help": "Specify the column that the member's email will be in."
    },
    {
        "name_or_flags": "--incoming-role",
        "type": str,
        "default": "role",
        "required": False,
        "help": "Specify the column that the member's role will be in."
    }
]

parser = argparse.ArgumentParser()
for argument in arg_parse_args:
    parser.add_argument(
        argument.get("name_or_flags"),
        type=argument.get("type"),
        default=argument.get("default", None),
        required=argument.get("required"),
        help=argument.get("help")
    )

args = parser.parse_args()

@dataclass
class Address:
    city: str
    region1: str
#
#
#
pysqldf = lambda q: sqldf(q, globals())
user_dataframe = None
csv_records = None
incoming_first_name_header = args.incoming_first_name_header
incoming_middle_name_header = args.incoming_middle_name_header
incoming_last_name_header = args.incoming_last_name_header
destination_records = []
gss_number = args.GSS_num_start_range
try:

    comparison_dataframe = pandas.read_csv(args.comparison_file_name).sort_values(by=destination_column_names[0])
    incoming_dataframe = pandas.read_csv(args.incoming_file_name)

    # destination_dataframe = DataFrame(
    #     columns=destination_column_names
    # )
    for index, row in incoming_dataframe.iterrows():
        incoming_user_full_name = parse_name(row[args.incoming_full_name_header]) if args.incoming_full_name_header else parse_name(
            "{} {} {}".format(
                row[incoming_first_name_header],
                row[incoming_middle_name_header],
                row[incoming_last_name_header]
            )
        )
        existing_user = comparison_dataframe.query(
            "FNAME=='{}' and LNAME=='{}'".format(
                incoming_user_full_name.given,
                incoming_user_full_name.family
                # row[incoming_first_name_header],
                # row[incoming_last_name_header]
            )
        )
        if existing_user.empty:
            try:
                addresses = pyap.parse(row[args.incoming_address], country="US")
            except KeyError as e:
                addresses = [
                    Address(
                        city=row[args.incoming_city],
                        region1=row[args.incoming_state]
                    )
                ]
            city = addresses[0].city
            state = addresses[0].region1
            destination_records.append(
                [
                    gss_number,
                    row[incoming_first_name_header],
                    row[incoming_middle_name_header],
                    row[incoming_last_name_header],
                    city,
                    state,
                    row[args.incoming_phone] if args.incoming_pone else "",
                    row[args.incoming_nss_number],
                    row[args.incoming_email],
                    f"{row[incoming_first_name_header]}.{row[incoming_last_name_header]}".lower().replace(" ", ""),
                    row[args.incoming_role] if args.incoming_role in incoming_dataframe.columns else "subscriber",
                    f"{row[incoming_first_name_header]} {row[incoming_last_name_header]}"
                ]
            )
            gss_number += 1
    destination_dataframe = DataFrame(
        columns=destination_column_names,
        data=destination_records
    )
    print("Entries to be imported:\n")
    destination_dataframe.to_csv(
        args.destination_file_name,
        index=False,
        encoding='utf-8',
        lineterminator="\n"
    )
    if args.write_new_truth_to is not None:
        consolidated_truth_dataframe = pandas.concat(
            [
                comparison_dataframe,
                destination_dataframe
            ]
        )
        consolidated_truth_dataframe.to_csv(
            args.write_new_truth_to,
            index=False
        )




except FileNotFoundError:
    print(f'Comparison file must exist...')
except pandas.errors.EmptyDataError:
    print('The file is empty')
except OSError:
    print(f'incoming file name just exist...')
