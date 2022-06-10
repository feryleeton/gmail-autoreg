import config
import requests
from imap_tools import MailBox, AND
import pytz
import re

utc = pytz.UTC


def group_list(group_name):
    open_url = config.ADSPWR_URL + "/api/v1/group/list?page_size=1000000&group_name=" + group_name
    resp = requests.get(open_url).json()
    for gr in resp['data']['list']:
        if group_name == gr['group_name']:
            return gr['group_id']
    return False


def get_random_proxy():
    query = ("SELECT *  FROM proxies WHERE active = 1 ORDER BY RAND()")
    config.cur_reader.execute(query)
    proxy = config.cur_reader.fetchone()
    return proxy


def select_proxy(ip=''):
    if ip:
        query = ("SELECT *  FROM proxies WHERE ip = %s AND active = 1")
        config.cur_reader.execute(query, [ip])
        proxy = config.cur_reader.fetchone()
        if proxy is None:
            proxy = get_random_proxy()

    else:
        proxy = get_random_proxy()
    return proxy[0], proxy[1], proxy[2], proxy[3]


def detect_imap_server_by_login(email_address):
    if 'rambler.ru' in email_address:
        imap_server = 'imap.rambler.ru'
    elif 'gmail.com' in email_address:
        imap_server = 'imap.gmail.com'
    elif 'firstmail.ru' in email_address:
        imap_server = 'imap.firstmail.ru'
    elif 'mail.ru' in email_address or 'inbox.ru' in email_address or 'bk.ru' in email_address:
        imap_server = 'imap.mail.ru'
    else:
        imap_server = 'imap.smartgridinsights.com'

    return imap_server


def get_emails(filter_from, filter_to, login, password, start_datetime):

    imap_server = detect_imap_server_by_login(login)

    with MailBox(imap_server).login(login, password) as mailbox:

        code = None

        for msg in mailbox.fetch(reverse=True, limit=10):
            if msg.from_ == filter_from and msg.to[0] == filter_to:
                if msg.date.replace(tzinfo=utc) > start_datetime.replace(tzinfo=utc):
                    print(msg.text)
                    # code = msg.text.split(': ')[1].split("\r\n\r\n")[0]
                    code = re.search(':\s\d+', msg.text).group().replace(': ', '')
                    print(code)
                    return code
            else:
                pass

        return code
