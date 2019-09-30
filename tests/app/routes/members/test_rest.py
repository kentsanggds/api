from flask import json, url_for
from tests.conftest import create_authorization_header

from app.comms.encryption import encrypt
from app.models import Member


class WhenPostingMembers:

    def it_unsubscribes_member(self, app, client, db_session, sample_member):
        unsubcode = encrypt(
            "{}={}".format(app.config['EMAIL_TOKENS']['member_id'], str(sample_member.id)),
            app.config['EMAIL_UNSUB_SALT']
        )

        response = client.post(
            url_for('members.unsubscribe_member', unsubcode=unsubcode),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert not sample_member.active
        assert response.json == {'message': '{} unsubscribed'.format(sample_member.name)}

    def it_imports_members(self, client, db, db_session, sample_marketing):
        data = [
            {
                "id": "1",
                "Name": "Test member",
                "EmailAdd": "test@example.com",
                "Active": "y",
                "CreationDate": "2019-08-01",
                "Marketing": "1",
                "IsMember": "n",
                "LastUpdated": "2019-08-10 10:00:00"
            },
            {
                "id": "2",
                "Name": "Test member 2",
                "EmailAdd": "test2@example.com",
                "Active": "y",
                "CreationDate": "2019-08-02",
                "Marketing": "1",
                "IsMember": "n",
                "LastUpdated": "2019-08-11 10:00:00"
            },
        ]
        response = client.post(
            url_for('members.import_members'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        members = Member.query.all()

        assert len(members) == 2
        assert members[0].old_id == int(data[0]['id'])
        assert members[0].name == data[0]['Name']

    def it_doesnt_import_exising_members(self, client, db_session, sample_marketing, sample_member):
        data = [
            {
                "id": "1",
                "Name": "Test member",
                "EmailAdd": "test@example.com",
                "Active": "y",
                "CreationDate": "2019-08-01",
                "Marketing": "1",
                "IsMember": "n",
                "LastUpdated": "2019-08-10 10:00:00"
            },
            {
                "id": "2",
                "Name": "Test member 2",
                "EmailAdd": "test2@example.com",
                "Active": "y",
                "CreationDate": "2019-08-02",
                "Marketing": "1",
                "IsMember": "n",
                "LastUpdated": "2019-08-11 10:00:00"
            },
        ]
        response = client.post(
            url_for('members.import_members'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201
        assert response.json.get('errors') == ['member already exists: 1']

        members = Member.query.all()

        assert len(members) == 2

    def it_doesnt_import_members_with_invalid_marketing(self, client, db_session, sample_marketing, sample_member):
        data = [
            {
                "id": "2",
                "Name": "Test member 2",
                "EmailAdd": "test2@example.com",
                "Active": "y",
                "CreationDate": "2019-08-02",
                "Marketing": "2",
                "IsMember": "n",
                "LastUpdated": "2019-08-11 10:00:00"
            },
            {
                "id": "3",
                "Name": "Test member 3",
                "EmailAdd": "test3@example.com",
                "Active": "y",
                "CreationDate": "2019-08-02",
                "Marketing": "1",
                "IsMember": "n",
                "LastUpdated": "2019-08-11 10:00:00"
            },
        ]
        response = client.post(
            url_for('members.import_members'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201
        assert response.json.get('errors') == ['Cannot find marketing: 2']

        members = Member.query.all()

        assert len(members) == 2
