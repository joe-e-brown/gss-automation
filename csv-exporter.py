import argparse
import pandas
from nameparser._config_shim import Constants, CONSTANTS
from pandas import DataFrame
from pandasql import sqldf
import pyap
from dataclasses import dataclass
from nameparser import HumanName
from sqlalchemy.engine import row
import math

class GssName(HumanName):
    def __init__(
        self,
        full_name: str = "",
        constants: Constants | None = CONSTANTS,
        string_format: str | None = None,
        initials_format: str | None = None,
        initials_delimiter: str | None = None,
        initials_separator: str | None = None,
        suffix_delimiter: str | None = None,
        first: str | list[str] | None = None,
        middle: str | list[str] | None = None,
        last: str | list[str] | None = None,
        title: str | list[str] | None = None,
        suffix: str | list[str] | None = None,
        nickname: str | list[str] | None = None,
        maiden: str | list[str] | None = None,
        nss_number: str | None = None,
        email_address: str | None=None
    ):
        super().__init__(
            full_name,
            constants,
            string_format,
            initials_format,
            initials_delimiter,
            initials_separator,
            suffix_delimiter,
            first,
            middle,
            last,
            title,
            suffix,
            nickname,
            maiden,
        )
        self.nss_number = nss_number
        self.email = email_address

def _check_for_user_in_consolidated_truth(
        candidate: GssName,
        reference_data_frame: DataFrame
) -> DataFrame:
    """
    This will check against three member attributes in this sequence:
    - email
    - nss number
    - first and last name
    :param candidate:
    :param reference_data_frame:
    :return: retrieved existing user DataFrame
    """
    email_query = "EMAIL=='{}'".format(
        candidate.email
    )
    nss_number_query = "NSS_NUM=='{}'".format(
        candidate.nss_number
    )
    first_last_name_query = "FNAME=='{}' and LNAME=='{}'".format(
        candidate.first,
        candidate.last
    )
    query_list=[
        email_query,
        nss_number_query,
        first_last_name_query
    ]

    not_found = True
    query_index = 0
    matching_user = None
    not_found = True
    while not_found:
        matching_user = reference_data_frame.query(query_list[query_index])
        query_index+=1
        not_found = matching_user.empty and query_index < len(query_list)
    return matching_user

def _get_city_state(location: str) -> tuple[str,str]:
    # This function is called when city & state aren't passed in their own columns.
    """
    :param location: contains information about an address
    :return: city & state strings
    Scenario 1: location is an empty string
    Scenario 2: location contains complete address information
    Scenario 3: location contains a city & state
    Scenario 4: location only contains a city name
    """
    # Actually have to check if location is float NaN
    if isinstance(location, float) and math.isnan(location):
        return "",""
    # Scenario 1
    if len(location)==0:
        return "",""
    else:
        try:
            # Scenario 2:
            addresses = pyap.parse(row[args.incoming_address], country="US")
            return addresses[0].city or "", addresses[0].region1 or ""

        except Exception as e:
            # Scenario 3
            lex_array = location.split(' ')
            if len(lex_array) > 2:
                state = lex_array[len(lex_array)-1]
                city = " ".join(lex_array[0:len(lex_array)-2])
                return city, state
            if len(lex_array)==2:
                return lex_array[0],lex_array[1]
            if len(lex_array)==1:
                return lex_array[0],""

if __name__ == "__main__":
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

        for index, row in incoming_dataframe.iterrows():
            incoming_user_full_name = GssName(
                row[args.incoming_full_name_header],
                email_address=row[args.incoming_email],
                nss_number=row[args.incoming_nss_number]
            )\
            if args.incoming_full_name_header else GssName(
                first=row[incoming_first_name_header],
                middle=row[incoming_middle_name_header],
                last=row[incoming_last_name_header],
                email_address=row[args.incoming_email],
                nss_number=row[args.incoming_nss_number]
            )
            existing_user = _check_for_user_in_consolidated_truth(
                incoming_user_full_name,
                comparison_dataframe
            )

            if existing_user.empty:
                # Parse city & State
                incoming_location = row[args.incoming_address] if args.incoming_address else f"{row[args.incoming_city]} {row[args.incoming_state]}"

                city, state = _get_city_state(incoming_location)
                destination_records.append(
                    [
                        gss_number,
                        incoming_user_full_name.first,
                        incoming_user_full_name.middle,
                        incoming_user_full_name.last,
                        city,
                        state,
                        row[args.incoming_phone] if args.incoming_phone else "",
                        row[args.incoming_nss_number],
                        row[args.incoming_email],
                        f"{incoming_user_full_name.first}.{incoming_user_full_name.last}".lower().replace(" ",""),
                        row[args.incoming_role] if args.incoming_role in incoming_dataframe.columns else "subscriber",
                        f"{incoming_user_full_name.first} {incoming_user_full_name.last}"
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
