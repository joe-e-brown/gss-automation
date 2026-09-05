import argparse
import pandas
from pandasql import sqldf

"""
We're using these CSV columns in the destination, in order:
GSS_NUM,FNAME,LNAME,CITY,STATE,PHONE_NUM,NSS_NUM,EMAIL,user_login,role,display_name
"""
FNAME=2
LNAME=3
CITY=4
STATE=5
PHONE_NUM=6
NSS_NUM=7
EMAIL=8
user_login=9
role=10
display_name=11

parser = argparse.ArgumentParser()
parser.add_argument("--incoming-file-name", type=str, required=True, help="Specify the CSV file that new records shall be selected from.")
parser.add_argument("--comparison-file-name", type=str, required=True, help="Specify the CSV file that new records checked against.")
parser.add_argument("--destination-file-name", type=str, required=True, help="Specify the CSV file that new records will be written to.")
parser.add_argument("--GSS-num-start-range", type=int, required=True, help="A GSS Number will be added to each record. This specifies what the first GSS number will be.")
parser.add_argument("--incoming-first-name-header", type=str, required=True, help="Specify the column that the member's first name will be in.")
parser.add_argument("--incoming-last-name-header", type=str, required=True, help="Specify the column that the member's last name will be in.")
parser.add_argument("--incoming-city", type=str, help="Specify the column that the member's city will be in.")
parser.add_argument("--incoming-state", type=str, help="Specify the column that the member's state will be in.")
parser.add_argument("--incoming-phone", type=str, required=True, help="Specify the column that the member's phone number will be in.")
parser.add_argument("--incoming-nss-number", type=int, required=True, help="Specify the column that the member's NSS number will be in.")
parser.add_argument("--incoming-email", type=str, required=True, help="Specify the column that the member's email will be in.")
parser.add_argument("--incoming-role", type=str, default="subscriber", help="Specify the column that the member's role will be in.")
args = parser.parse_args()

#
#
#
pysqldf = lambda q: sqldf(q, globals())
user_dataframe = None
csv_records = None
incoming_first_name_header = args.incoming_first_name_header
incoming_last_name_header = args.incoming_last_name_header
destination_records = []
try:
    comparison_dataframe=pandas.read_csv(args.comparison_file_name)
    incoming_csv_reader=pandas.read_csv(args.incoming_file_name)
    destination_csv_file=pandas.
    for index, row in incoming_csv_reader.iterrows():
        existing_user = comparison_dataframe.query(
            "FNAME=='{}' and LNAME=='{}'".format(
                row[incoming_first_name_header],
                row[incoming_last_name_header]
            )
        )
        if existing_user.empty:
            print("{} {}: Will need to be imported\n".format(
                row.get(incoming_first_name_header),
                row.get(incoming_last_name_header)
                )
            )

except FileNotFoundError:
    print(f'Comparison file must exist...')
except pandas.errors.EmptyDataError:
    print('The file is empty')
except OSError:
    print(f'incoming file name just exist...')




