import mysql.connector

# APP_SETTINGS

COUNTRY = 'Russia'

FROWARD_TO = 'contact.loboda.pavel@gmail.com'
FORWARD_EMAIL_PASSWORD = 'jntyylzrfknldqfn'

# APP_DATA

GMAIL_CREATE_ACCOUNT_LINK = 'https://accounts.google.com/signup/v2/webcreateaccount?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&flowName=GlifWebSignIn&flowEntry=SignUp'
FORWARDING_SETUP_LINK = 'https://mail.google.com/mail/u/0/#settings/fwdandpop'

AVAILABLE_COUNTRIES = {
    'Russia': ['0', 'ru'],
    'Ukraine': ['1', 'ua'],
    'Kazakhstan': ['2', 'kz']
}

# API_TOKENS

SMSActivateAPIKey = '7c180eb5c5921b816e2A5dfeeAdffb77'

# DATABASE

ENDPOINT_WRITER = "main-1.cluster-c5jdhdc8klqu.eu-central-1.rds.amazonaws.com"
ENDPOINT_READER = "main-1.cluster-ro-c5jdhdc8klqu.eu-central-1.rds.amazonaws.com"
PORT = "3306"
USER = "discord"
REGION = "eu-central-1"
DBNAME = "discord"
PASS = "BMvtJbek9ScKJb"

conn_writer = mysql.connector.connect(host=ENDPOINT_WRITER, user=USER, passwd=PASS, port=PORT, database=DBNAME)
cur_writer = conn_writer.cursor(buffered=True)

conn_reader = mysql.connector.connect(host=ENDPOINT_READER, user=USER, passwd=PASS, port=PORT, database=DBNAME)
cur_reader = conn_writer.cursor(buffered=True)

# ADS_POWER

ADSPWR_URL = 'http://local.adspower.com:50325'