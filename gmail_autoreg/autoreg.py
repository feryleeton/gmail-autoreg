import random
import string
import time
import csv
from datetime import datetime
from playwright_stealth import stealth_sync

import config
import helper_funcs
from faker import Faker
from smsactivate.api import SMSActivateAPI


def generate_fake_data():
    fake = Faker()
    data = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'password': fake.password(),
        'day': random.randint(1, 28),
        'month': random.randint(1, 12),
        'year': random.randint(1970, 2000),
        'gender': random.randint(1, 3)
    }
    return data


def wait_for_code(activation_id):
    sa = SMSActivateAPI(config.SMSActivateAPIKey)
    counter = 0
    while True:
        status = sa.getStatus(id=activation_id)
        try:
            resp = sa.activationStatus(status)
            # resp = {'status': 'STATUS_OK:983904', 'message': None}
            if resp['status'].split(':')[0] == 'STATUS_OK':
                code = resp['status'].split(':')[-1]
                return code
            print('Waiting for code ...')
            counter = counter + 1
            if counter >= 12:
                sa.setStatus(id=activation_id, status=8)
                raise Exception('SMS-ACTIVATE sms not found after 120 sec: ' + str(status))
        except Exception as e:
            print(status)
            # canceling activation
            sa.setStatus(id=activation_id, status=8)
            raise Exception('SMS-ACTIVATE service error: ' + str(status))
        time.sleep(10)


def get_phone():
    sa = SMSActivateAPI(config.SMSActivateAPIKey)
    resp = sa.getNumber(service='go', country=str(config.AVAILABLE_COUNTRIES[config.COUNTRY][0]), verification="false")
    print("RESP: ", resp)
    try:
        phone_num = resp['phone']
        activation_id = resp['activation_id']
        return phone_num, activation_id
    except Exception as e:
        raise Exception('SMS-ACTIVATE service error: ' + str(resp))


def save_account_data(login, password):
    with open('gmail_accounts.csv', mode='a', newline='') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([login, password])


class GmailAutoreg:
    def __init__(self, browser):
        self.browser = browser
        self.context = browser.contexts[0]
        self.page = self.context.new_page()
        stealth_sync(self.page)

    def next_step(self):
        self.page.locator('button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.qfvgSe.qIypjc.TrZEUc.lw1w4b').click()
        time.sleep(3)

    def unfocus(self):
        body = self.page.query_selector("body")
        body.click()
        time.sleep(1)

    def accept_privacy_policy(self):
        self.unfocus()
        for i in range(5):
            self.page.keyboard.press("Tab", delay=300)
        time.sleep(1)
        self.next_step()

    def generate_unique_email_addr(self):
        while True:
            # generating fake user data
            fake_data = generate_fake_data()

            self.page.fill('input[name=firstName]', fake_data['first_name'])
            self.page.fill('input[name=lastName]', fake_data['last_name'])

            # email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randrange(8, 16)))
            email = str(fake_data['first_name']).lower() + '.' + str(fake_data['last_name']).lower() + str(fake_data['year'])
            self.page.fill('input[name=Username]', email)

            self.unfocus()

            error = self.page.query_selector('.o6cuMc')

            if not error:
                break
        return email, fake_data['password']

    def fill_main_acc_data(self):
        email, password = self.generate_unique_email_addr()

        self.page.fill('input[name=Passwd]', password)
        self.page.fill('input[name=ConfirmPasswd]', password)

        return str(email) + '@gmail.com', password

    def fill_phone_data(self):
        sa = SMSActivateAPI(config.SMSActivateAPIKey)
        self.page.query_selector('div[role=combobox]').click()
        time.sleep(1)
        self.page.query_selector('li[data-value=' + str(config.AVAILABLE_COUNTRIES[config.COUNTRY][1]) + ']').click()
        time.sleep(1)
        while True:
            phone_num, activation_id = get_phone()
            self.page.fill('input[type=tel]', str(phone_num))
            self.next_step()
            time.sleep(2)

            error = self.page.query_selector('div[role=combobox]')
            print('combobox: ', error)
            if not error:
                print('No error')
                break
            else:
                print('Got error, canceling...')
                # canceling activation
                sa.setStatus(id=activation_id, status=8)
        return activation_id, phone_num

    def fill_confirmation_code(self, code):
        self.page.fill('input[type=tel]', str(code))
        time.sleep(2)

    def fill_secondary_acc_data(self):
        fake_data = generate_fake_data()
        self.page.fill('input[name=day]', str(fake_data['day']))
        self.page.select_option('select#month', value=str(fake_data['month']))
        self.page.fill('input[name=year]', str(fake_data['year']))
        self.page.select_option('select#gender', value=str(fake_data['gender']))

    def proceed_phone_confirmation(self):
        activation_id, phone_num = self.fill_phone_data()
        # self.next_step()

        code = wait_for_code(activation_id)
        self.fill_confirmation_code(code)
        self.next_step()

    def skip_other_services(self):
        self.unfocus()
        for button in range(3):
            self.page.keyboard.press("Tab", delay=100)
        time.sleep(1)
        self.page.keyboard.press("Enter", delay=100)

    def setup_forwarding(self, forward_to):
        self.page.goto(config.FORWARDING_SETUP_LINK)
        for attempt in range(12):
            time.sleep(5)
            try:
                self.page.query_selector('input[act=add]').click()
                start_datetime = datetime.now()
                break
            except Exception as e:
                if attempt == 6:
                    raise Exception('Timeout error during forwarding setup: ' + str(e))
                else:
                    print('Waiting for page load...')

        time.sleep(1)
        frame = self.page.locator('.PN')
        frame.locator('input').fill(str(forward_to))
        time.sleep(1)

        with self.page.context.expect_page() as window:
            time.sleep(1)
            self.page.query_selector('button[name=next]').click()

        time.sleep(5)
        new_window = window.value
        new_window.wait_for_load_state()
        new_window.query_selector('input[type=submit]').click()
        time.sleep(1)
        self.page.query_selector('button[name=ok]').click()

        code = self.get_fwd_verif_code(start_datetime)
        self.page.query_selector('input[act=verifyText]').fill(str(code))
        self.page.query_selector('input[act=verify]').click()

        time.sleep(1)

        check = self.page.query_selector_all('input[name=sx_em]')
        check[-1].click()

        time.sleep(1)

        imap = self.page.query_selector_all('input[name=bx_ie]')
        imap[0].click()

        time.sleep(1)

        self.page.query_selector('button[guidedhelpid=save_changes_button]').click()

    def get_fwd_verif_code(self, start_datetime):
        code = None
        while not code:
            print('Waiting for fwd confirmation code...')
            time.sleep(10)
            code = helper_funcs.get_emails('forwarding-noreply@google.com', config.FROWARD_TO, config.FROWARD_TO,
                                           config.FORWARD_EMAIL_PASSWORD, start_datetime)
        print('Got fwd confirmation code: ' + str(code))
        return code

    def create_account(self):
        # redirecting to page
        self.page.goto(config.GMAIL_CREATE_ACCOUNT_LINK)

        # filling basic data for account creation
        email, password = self.fill_main_acc_data()
        self.next_step()

        # phone confirmation
        self.proceed_phone_confirmation()

        # filling secondary data
        self.fill_secondary_acc_data()
        self.next_step()

        self.skip_other_services()
        self.accept_privacy_policy()

        # save acc data
        save_account_data(email, password)

        self.setup_forwarding(config.FROWARD_TO)

        time.sleep(1)
