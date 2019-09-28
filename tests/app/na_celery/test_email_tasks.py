from bs4 import BeautifulSoup
from flask import current_app

from app.na_celery.email_tasks import send_emails
from app.comms.encryption import decrypt, get_tokens


class WhenProcessingSendEmailsTask:

    def it_calls_send_email_to_task(self, mocker, db, db_session, sample_email, sample_member):
        mock_send_email = mocker.patch('app.na_celery.email_tasks.send_email', return_value=200)
        send_emails(sample_email.id)

        assert mock_send_email.call_args[0][0] == sample_member.email
        assert mock_send_email.call_args[0][1] == 'workshop: test title'
        page = BeautifulSoup(mock_send_email.call_args[0][2], 'html.parser')
        assert 'http://frontend-test/member/unsubscribe' in str(page)

        unsubcode = page.select_one('#unsublink')['href'].split('/')[-1]
        tokens = get_tokens(decrypt(unsubcode, current_app.config['EMAIL_UNSUB_SALT']))
        assert tokens[current_app.config['EMAIL_TOKENS']['member_id']] == str(sample_member.id)

    def it_sends_an_email_to_members_up_to_email_limit(self):
        pass

    def it_does_not_send_an_email_if_not_between_start_and_expiry(self):
        pass

    def it_sends_email_with_correct_template(self):
        pass
