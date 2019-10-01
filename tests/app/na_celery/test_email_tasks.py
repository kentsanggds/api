from bs4 import BeautifulSoup
from flask import current_app

from app.na_celery.email_tasks import send_emails
from app.comms.encryption import decrypt, get_tokens

from tests.db import create_member


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

    def it_only_sends_to_3_emails_if_not_live_environment(self, mocker, db, db_session, sample_email, sample_member):
        member_1 = create_member(name='Test 1', email='test1@example.com')
        member_2 = create_member(name='Test 2', email='test2@example.com')
        member_3 = create_member(name='Test 3', email='test3@example.com')

        mock_send_email = mocker.patch('app.na_celery.email_tasks.send_email', return_value=200)
        send_emails(sample_email.id)

        assert mock_send_email.call_count == 3
        assert mock_send_email.call_args_list[0][0][0] == sample_member.email
        assert mock_send_email.call_args_list[1][0][0] == member_1.email
        assert mock_send_email.call_args_list[2][0][0] == member_2.email

    def it_sends_an_email_to_members_up_to_email_limit(self):
        pass

    def it_does_not_send_an_email_if_not_between_start_and_expiry(self):
        pass

    def it_sends_email_with_correct_template(self):
        pass
