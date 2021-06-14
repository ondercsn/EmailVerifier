import email, imaplib, re, sys
from lxml import html
from bs4 import BeautifulSoup as bs

from inboxes import inbox_directories


class EmailVerifier:
    imap = None

    def login(self, emailaddress, password):
        try:
            resp, data = self.imap.login(emailaddress, password)
            if resp == 'OK':
                return True
        except Exception as err:
            print('couldnt login to email server : %s ' % err)
            return False

        return False


    def parse_mailbox(self, data):
        flags, b, c = data.partition(' ')
        separator, b, name = c.partition(' ')
        return (flags, separator.replace('"', ''), name.replace('"', ''))


    def fetch_directories(self):
        resp, data = self.imap.list('""', '*')
        if resp == 'OK':
            for mbox in data:
                flags, separator, name = self.parse_mailbox(bytes.decode(mbox))
                fmt = '{0}    : [Flags = {1}; Separator = {2}'
                print(fmt.format(name, flags, separator))


    def get_mails(self, emailaddress, password, host, port=993, inbox_name=None):
        result = []
        self.imap = imaplib.IMAP4_SSL(host, port)

        if self.login(emailaddress, password):
            if not inbox_name:
                inbox_name = inbox_directories[host]

            self.imap.select(inbox_name)

            resp, data = self.imap.uid('search', None, "ALL")  # self.imap.search(None, '(ALL)') #

            if resp == 'OK':
                for num in data[0].split():

                    response1, data = self.imap.uid('fetch', num, '(RFC822)')

                    if response1 == 'OK':
                        raw_email = data[0][1]
                        raw_email_string = raw_email.decode('utf-8')
                        email_message_str = email.message_from_string(raw_email_string)
                        email_message_raw = email.message_from_bytes(data[0][1])

                        subject = str(
                            email.header.make_header(email.header.decode_header(email_message_raw['Subject']))
                        )

                        _response = {}
                        _response['email_body_string'] = email_message_str

                        email_from = str(
                            email.header.make_header(email.header.decode_header(email_message_raw['From'])))
                        name, email_addr = email_from.split('<')

                        body = None
                        for part in email_message_str.walk():
                            part.get_content_type()
                            body = part.get_payload(decode=True)

                        _response['message'] = body
                        _response["subject"] = subject
                        _response["from_mail"] = email_addr.replace(">", "")
                        _response["from_name"] = name

                        result.append(_response)
        return result


    def get_verification_link(self, emailaddress, password, host, port):
        resp = self.get_mails(emailaddress, password, host, port)
        link = self.parse_instagram_verification_link(resp)
        return link


    def check_if_email_is_alive(self, email):
        self.imap = imaplib.IMAP4_SSL(email.imap_address, email.imap_port)
        if self.login(email.address, email.password):
            return True
        else:
            return False
