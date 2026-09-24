import argparse
import wordpress
from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth

parser = argparse.ArgumentParser()
parser.add_argument("--wordpress-site", type=str, required=True,
                    help="Specify the WordPress site to use.")
parser.add_argument("--user-name", type=str, required=True,
                    help="Specify the WordPress user to use.")
parser.add_argument("--password-file", type=str, required=True,
                    help="Specify the file containing the WordPress user's password.")
args = parser.parse_args()




try:
    with open(args.password_file, 'r') as credentials:
        site_url = args.wordpress_site
        site_user = args.user_name
        password = credentials.read()
        auth = ApplicationPasswordAuth(
            username=site_user,
            app_password=password
        )
        wp_client = WPClient(
            base_url=site_url,
            auth=auth
        )
        more_users = True
        all_users = []
        page_index = 1
        while more_users:
            users = wp_client.users.list(
                page=page_index
            )
            if len(users) > 0:
                all_users.extend(
                    users
                )
                page_index += 1
            else:
                more_users = False
        print(all_users)


except FileNotFoundError:
    print(f'Comparison file must exist...')
except OSError:
    print(f'incoming file name just exist...')
