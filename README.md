# GSS New User Onboarding CSV Parser
## Theory of Operation
The purpose of this utility is to ease onboarding of new GSS members to the GSS WordPress platform.
This utility:
- Receives a CSV containing meeting attendance,
- Receives header information about the incoming meeting attendance CSV,
- Receives a CSV containing a consolidated truth,
- Receives an argument for where to write the new members delta CSV,
- Receives an argument for where the new consolidated truth shall be written,
- Determines which attendees are not found in the consolidated truth,
- Writes a CSV containing members to be onboarded,
- Writes a new consolidated truth.

 ## CLI Arguments

| Description                   | Required                                                                                                               | Required?                                              |
|-------------------------------|------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| --incoming-file-name          | Specify the CSV file that new records shall be selected from.                                                          | T                                                      |
| --comparison-file-name        | Specify the CSV file that new records checked against.                                                                 | T                                                      |
| --destination-file-name       | Specify the CSV file that new records will be written to.                                                              | T                                                      |
| --write-new-truth-to          | A CSV to write your consolidate truth to.                                                                              | T                                                      |
| --GSS-num-start-range         | A GSS Number will be added to each record. This specifies what the first GSS number will be.                           | T                                                      |
| --incoming-full-name-header   | Specify the column header if the member's full name is being passed in one string.                                     | Overrides --incoming-[first\|middle\|last]-name-header |
| --incoming-first-name-header  | Specify the column that the member's first name will be in.                                                            | F                                                      |
| --incoming-middle-name-header | Specify the column that the member's middle name will be in.                                                           | F                                                      |
| --incoming-last-name-header   | Specify the column that the member's last name will be in.                                                             | T                                                      |
| --incoming-city               | Specify the column that the member's city will be in.                                                                  | F                                                      |
| --incoming-state              | Specify the column that the member's state will be in.                                                                 | F                                                      |
| --incoming-address            | Specify the column the member's address will be in. Note this overrides --incoming-city and --incoming-state arguments | F                                                      |
| --incoming-phone              | Specify the column that the member's phone number will be in.                                                          | T                                                      |
| --incoming-nss-number         | Specify the column that the member's NSS number will be in, must be NSS number or "associate"                          | T                                                      |
| --incoming-email              | Specify the column that the member's email will be in.                                                                 | T                                                      |
| --incoming-role               | Specify the column that the member's role will be in                                                                   | F                                                      |

## Todo

- Refactor checking attendance list to:
  - Check first against email
  - Check secondly against name
- Add CLI Arguments:
  - To customize delta & consolidated truth CSV headers
