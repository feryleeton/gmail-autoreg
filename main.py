import time

import requests

import helper_funcs
import config

from playwright.sync_api import sync_playwright
from gmail_autoreg import GmailAutoreg


def create_adspwr_user():
    open_url = config.ADSPWR_URL + "/api/v1/user/create"
    group_id = helper_funcs.group_list('Discord')
    ip, port, login, password = helper_funcs.select_proxy()

    print("Using proxy: ", ip, port)

    json_arr = {'group_id': group_id,
                'domain_name': 'discord.com',
                "name": "name_1",
                'user_proxy_config': {"proxy_soft": "other", "proxy_type": "socks5", "proxy_host": ip,
                                      "proxy_port": str(port), "proxy_user": login, "proxy_password": password},
                'fingerprint_config': {"automatic_timezone": 1, "language": ["en-US", "en"], "flash": "block",
                                       "fonts": ["all"], "webrtc": "disabled",
                                       }
                }
    create_resp = requests.post(open_url, json=json_arr).json()
    user_serial = create_resp['data']['serial_number']
    return user_serial


def get_adspwr_browser():
    serial = create_adspwr_user()
    open_url = config.ADSPWR_URL + "/api/v1/browser/start?serial_number=" + str(serial)
    resp = requests.get(open_url).json()
    return resp['data']['ws']['puppeteer']


def create_accounts(num):
    counter = 0
    while counter < num:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(get_adspwr_browser())
            autoreg = GmailAutoreg(browser)
            try:
                print('creating account # ' + str(counter + 1))
                autoreg.create_account()
                print('account #' + str(counter + 1) + ' created !')
                counter = counter + 1
            except Exception as e:
                print('Account creation process filed with error: ' + str(e))
            autoreg.page.close()
            autoreg.context.close()
            autoreg.browser.close()


def main_menu():
    print('1 -- Create accounts')
    print('0 -- Exit')


if __name__ == '__main__':
    while True:
        main_menu()
        option = int(input('Enter your choice: '))

        if option == 0:
            break
        elif option == 1:
            num = int(input('Enter number of accounts: '))
            create_accounts(num)
