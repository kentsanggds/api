import copy
from datetime import timedelta
import pytest
from flask import json, url_for
from mock import Mock, call

from freezegun import freeze_time
from sqlalchemy.orm.exc import NoResultFound

from app.models import Event, EventDate

from tests.conftest import create_authorization_header
from tests.db import create_event, create_event_date, create_event_type, create_speaker

base64img = (
    'iVBORw0KGgoAAAANSUhEUgAAADgAAAAsCAYAAAAwwXuTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAEMElEQVRoge2ZTUxcVRTH'
    '/+fed9+bDxFEQUCmDLWbtibWDE2MCYGa6rabykITA7pV6aruNGlcGFe6c2ui7k1cmZp0YGdR2pjqoklBpkCVykem8/'
    'HeffceF8MgIC3YvDczNP0ls5l3cuf8cuee++65wGMe09LQQQP5xkkXJ4rpjYU40zkY7UcA/NZWopM3gv1iHyg4M5NTuRPrPf5'
    '6cJ4ETgsHg1ZHludDIxQQBphLpOiasfTrtVvPXB4a+nnPzO4rWFnOjroJO25CfkF5UAgBrTm+rP8nyiHAAzgALNNsCHzjdXZdI'
    'dop+h/BmzePeYPd+lXW9pIj4eqAwa3jtSeuV9PQhvKqKC7S4Hy1/myHIHNfSq84nyqXR7Tf+mK7cdMEU6G89O2HlLldAQCxPSD'
    '4U55TaRoJqodPDgCCEkOmaMR38HH9uy3B4tLAceViUt8zzckuInTJwE3QmerikbPApuDaXLbDk3yBCMnDOHPbYQYISEiJC7x6t'
    'F0AQNrzn1dpejnwD7ndJoHPcBKc0WX/uACAkOUr7Ntm5xUp2mdYQR8RAPBa5vqjMnvbceTmGoxajqj2aTah2bVNRAIB1pBmrm3'
    'AzfaMXNBNEqQU3wp2Jo2lWVKbok0yjWUGjWGjeuevyM6Fd2HxgbW4Kh1qiqgT07gEAEQwwO08M6bDu9lhhnnbcWiIBNCod9y4B'
    'HdABAvM55kxFa5khtmIcaVsDhS/aEME6xCBgcIUgCm9lBlmBxNKUQ4UfSWvE/0aPCCqrzDtdhfeCUO8pzX94qp/jz1R0jTBOqq'
    '7MO12L0xUfXq/WsWsktEWoqYL1kn2FaaSvYXxUlVOWkNhVJINXYMPggGqLg+MSrJvMlhGVXhaQlCvDJzRlicSyr5YKzjRjd00Q'
    'WbI8E7/MEkxIaU9BQkEQfSVtOGCvJDps2l6w6ziNSFtRiiObYsAGihYWhnoVYbHNPF5pfhJ6zMMA2HMx7S4BLeyvvdXtsexdgz'
    'WjqkU2sIKIyjH9Kt7EL0gA5aRKC4f61LQ47DmnJdCm26wWB0CAP9O//UoR+TaPqbdJJLN7q/GMoNCsgPACar7RseOAGq9iyhhR'
    'ss0jgUAaI3FVuihRI3rUU1QWL6kYniTbyauR/Cr+FIAgEp5v4dVKsRxXGkGShECjT88Nl8JAKDOWxvG4HNmVB6FvyolBIyhr6l'
    'vqbx1XEo8t3BZB/hCPRFxxWkwtSs0zid7wu+BXedB91nznSlx3k0fzml00wTjU75QFBeJlsrAHje8PJdN6Db7mZI8AsTXK4kSI'
    'QBH0f43vHWYc8pfXRl1gLcE8UukAF1uPVGVItgKw0oqGiM/8bqe/nHfO/rtzMzk1Kmjd8+SNKd1hV4nQKIVPAlgwKgk/6DL8qp'
    'nwp+of/Hv+4QejLW5bEeHsLQRXZoPTTuAdSv4qcH59f1i/wGycsTRKGME7gAAAABJRU5ErkJggg=='
)


@pytest.fixture
def sample_data(sample_speaker):
    create_event_type(old_id=2, event_type='excursion')

    data = [
        {
            "id": "1",
            "BookingCode": "",
            "MemberPay": "0",
            "Approved": "y",
            "Type": "1",
            "Title": "Philosophy of Economics",
            "SubTitle": "",
            "Description": "How Plato and Confucius can help understand economic development",
            "venue": "1",
            "Speaker": sample_speaker.name,
            "MultiDayFee": "10",
            "MultiDayConcFee": "8",
            "StartDate": "2004-09-20 19:30:00",
            "StartDate2": "2004-09-21 19:30:00",
            "StartDate3": "2004-09-22 19:30:00",
            "StartDate4": "2004-09-23 19:30:00",
            "EndDate": "0000-00-00 00:00:00",
            "Duration": "0",
            "Fee": "4",
            "ConcFee": "2",
            "Pub-First-Number": "3",
            "Mem-SignOn-Number": "12",
            "ImageFilename": "2004/Economics.jpg",
            "WebLink": "",
            "LinkText": None,
            "MembersOnly": "n",
            "RegisterStartOnly": "0",
            "SoldOut": None
        },
        {
            "id": "2",
            "BookingCode": "",
            "MemberPay": "0",
            "Approved": "y",
            "Type": "2",
            "Title": "Study Philosophy",
            "SubTitle": "",
            "Description": "16-week course introducing the major systems of thoughts from the East and West",
            "venue": "1",
            "Speaker": sample_speaker.name,
            "MultiDayFee": None,
            "MultiDayConcFee": "0",
            "StartDate": "2004-09-29 19:30:00",
            "StartDate2": "0000-00-00 00:00:00",
            "StartDate3": "0000-00-00 00:00:00",
            "StartDate4": "0000-00-00 00:00:00",
            "EndDate": "0000-00-00 00:00:00",
            "Duration": "0",
            "Fee": "96",
            "ConcFee": "64",
            "Pub-First-Number": "1",
            "Mem-SignOn-Number": "0",
            "ImageFilename": "2004/WinterCourse.jpg",
            "WebLink": "",
            "LinkText": "",
            "MembersOnly": "n",
            "RegisterStartOnly": "0",
            "SoldOut": None
        },
    ]

    return data


@pytest.fixture
def sample_req_event_data(db_session, sample_event_type, sample_venue, sample_speaker):
    return {
        'event_type': sample_event_type,
        'venue': sample_venue,
        'speaker': sample_speaker,
    }


@pytest.fixture
def sample_req_event_data_with_event(db_session, sample_req_event_data, sample_event, sample_event_date):
    data = {
        "event_type_id": sample_req_event_data['event_type'].id,
        "title": "Test title new",
        "sub_title": "Test sub title",
        "description": "Test description",
        "image_filename": "2019/test_img.png",
        "event_dates": [
            {
                "event_date": str(sample_event.event_dates[0].event_datetime),
                "speakers": [
                    {"speaker_id": sample_req_event_data['speaker'].id}
                ]
            },
        ],
        "venue_id": sample_req_event_data['venue'].id,
        "fee": 15,
        "conc_fee": 12,
    }

    sample_event_date.speakers = [sample_req_event_data['speaker']]
    sample_req_event_data['event'] = sample_event
    sample_req_event_data['data'] = data

    return sample_req_event_data


@pytest.fixture
def mock_paypal(mocker):
    return mocker.patch("app.routes.events.rest.PayPal.create_update_paypal_button", return_value='test booking code')


class WhenGettingEvents:

    def it_returns_all_events(self, client, sample_event, db_session):
        response = client.get(
            url_for('events.get_events'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert len(data) == 1

    @freeze_time("2018-01-10T19:00:00")
    def it_returns_all_future_events(self, client, sample_event_with_dates, sample_event_type, db_session):
        event_1 = create_event(
            title='future event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        event_2 = create_event(
            title='future event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_future_events'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert Event.query.count() == 3
        assert len(data) == 2
        assert data[0]['id'] == str(event_1.id)
        assert data[1]['id'] == str(event_2.id)

    @freeze_time("2018-01-10T19:00:00")
    def it_returns_past_year_events(self, client, sample_event_with_dates, sample_event_type, db_session):
        create_event(
            title='future event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        create_event(
            title='way past year event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2016-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_past_year_events'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert Event.query.count() == 3
        assert len(data) == 1
        assert data[0]['id'] == str(sample_event_with_dates.id)

    def it_returns_events_in_year(self, client, sample_event_with_dates, sample_event_type, db_session):
        event_2 = create_event(
            title='2018 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        create_event(
            title='way past year event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2016-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_events_in_year', year=2018),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert Event.query.count() == 3
        assert len(data) == 2
        assert data[0]['id'] == str(sample_event_with_dates.id)
        assert data[1]['id'] == str(event_2.id)

    def it_returns_limited_events(self, client, sample_event_with_dates, sample_event_type, db_session):
        event_2 = create_event(
            title='2018 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        create_event(
            title='beyond limit',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2016-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_limited_events', limit=2),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))

        assert Event.query.count() == 3
        assert len(data) == 2
        assert data[0]['id'] == str(event_2.id)
        assert data[1]['id'] == str(sample_event_with_dates.id)

    def it_raises_400_returns_limited_events_more_than_events_max(
        self, client, sample_event_with_dates, sample_event_type, db_session
    ):
        create_event(
            title='2018 event',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2018-01-20T19:00:00')]
        )
        create_event(
            title='beyond limit',
            event_type_id=sample_event_type.id,
            event_dates=[create_event_date(event_datetime='2016-01-25T19:00:00')]
        )

        response = client.get(
            url_for('events.get_limited_events', limit=3),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400

        data = json.loads(response.get_data(as_text=True))

        assert Event.query.count() == 3
        assert len(data) == 2
        assert data['message'] == '3 is greater than events max'

    def it_returns_all_events_with_event_dates(self, client, sample_speaker, sample_event_type, db_session):
        event_date_1 = create_event_date(event_datetime="2018-01-03")
        event_date_earliest = create_event_date(event_datetime="2018-01-01")
        event_date_2 = create_event_date(event_datetime="2018-01-02")

        create_event(event_type_id=sample_event_type.id, event_dates=[event_date_1, event_date_2])
        create_event(event_type_id=sample_event_type.id, event_dates=[event_date_2])
        create_event(event_type_id=sample_event_type.id, event_dates=[event_date_earliest])

        response = client.get(
            url_for('events.get_events'),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        data = json.loads(response.get_data(as_text=True))
        assert len(data) == 3
        assert data[0]['event_dates'][0]['event_datetime'] == str(event_date_earliest.event_datetime)[0:-3]


class WhenPostingExtractSpeakers:

    def it_extracts_unique_speakers_from_events_json(self, client, db_session, sample_data):
        event = copy.deepcopy(sample_data[0])
        event['Speaker'] = 'Gary Blue'
        sample_data.append(event)

        response = client.post(
            url_for('events.extract_speakers'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))
        data_speakers = set([d['Speaker'] for d in sample_data])

        assert len(json_resp) == len(data_speakers)
        assert set([s['name'] for s in json_resp]) == data_speakers


class WhenPostingImportEvents(object):

    @pytest.fixture
    def mock_storage(self, mocker):
        mock_storage = mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mock_storage_blob_exists = mocker.patch("app.storage.utils.Storage.blob_exists")
        yield
        mock_storage.assert_called_with('test-store')
        mock_storage_blob_exists.assert_called_with('2004/WinterCourse.jpg')

    @pytest.fixture
    def mock_storage_not_exists(self, mocker):
        mock_storage = mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mock_storage_blob_exists = mocker.patch("app.storage.utils.Storage.blob_exists", return_value=False)
        mock_storage_blob_upload = mocker.patch("app.storage.utils.Storage.upload_blob")
        yield
        mock_storage.assert_called_with('test-store')
        mock_storage_blob_exists.assert_called_with('2004/Economics.jpg')
        mock_storage_blob_upload.assert_called_with('./data/events/2004/Economics.jpg', '2004/Economics.jpg')

    def it_creates_events_for_imported_events(
        self, client, db_session, sample_event_type, sample_venue, sample_speaker, sample_data,
        mock_storage
    ):
        response = client.post(
            url_for('events.import_events'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_events = json.loads(response.get_data(as_text=True))['events']
        assert len(json_events) == len(sample_data)
        for i in range(0, len(sample_data) - 1):
            assert json_events[i]["old_id"] == int(sample_data[i]["id"])
            assert json_events[i]["title"] == sample_data[i]["Title"]
            assert json_events[i]["fee"] == int(sample_data[i]["Fee"])
            assert json_events[i]["conc_fee"] == int(sample_data[i]["ConcFee"])
            assert json_events[i]["multi_day_fee"] == int(sample_data[i]["MultiDayFee"])
            assert json_events[i]["multi_day_conc_fee"] == int(sample_data[i]["MultiDayConcFee"])
            assert json_events[i]["venue"]['name'] == sample_venue.name
            assert json_events[i]["venue"]['directions'] == sample_venue.directions

    def it_creates_multiple_speakers_for_imported_events_with_multiple_speakers(
        self, client, db_session, sample_event_type, sample_venue, sample_speaker, sample_data, mock_storage
    ):
        speaker_1 = create_speaker(name='John Smith')
        sample_data[0]['Speaker'] = "{} and {}".format(sample_speaker.name, speaker_1.name)
        sample_data[1]['Speaker'] = sample_speaker.name + " & " + speaker_1.name
        response = client.post(
            url_for('events.import_events'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_events = json.loads(response.get_data(as_text=True))['events']
        assert len(json_events) == len(sample_data)
        for i in range(0, len(sample_data) - 1):
            assert json_events[i]["old_id"] == int(sample_data[i]["id"])
            assert json_events[i]["title"] == sample_data[i]["Title"]
        assert json_events[0]["event_dates"][0]["speakers"] == [
            sample_speaker.serialize(), speaker_1.serialize()]
        assert len(json_events[0]["event_dates"]) == 4
        assert json_events[0]["event_dates"][0]['event_datetime'] == "2004-09-20 19:30"
        assert json_events[0]["event_dates"][1]['event_datetime'] == "2004-09-21 19:30"
        assert json_events[0]["event_dates"][2]['event_datetime'] == "2004-09-22 19:30"
        assert json_events[0]["event_dates"][3]['event_datetime'] == "2004-09-23 19:30"
        assert json_events[1]["event_dates"][0]["speakers"] == [
            sample_speaker.serialize(), speaker_1.serialize()]

    def it_ignores_existing_events_for_imported_events(
        self, client, db_session, sample_event_type, sample_venue, sample_speaker, sample_event, sample_data,
        mock_storage
    ):
        response = client.post(
            url_for('events.import_events'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_resp = json.loads(response.get_data(as_text=True))
        # should ignore the first data element but create the second one
        assert len(json_resp['events']) == len(sample_data) - 1
        assert json_resp['events'][0]['title'] == sample_data[1]['Title']
        assert str(json_resp['events'][0]['old_id']) == sample_data[1]['id']

    @pytest.mark.parametrize('field,desc', [
        ('Type', 'event type'),
        ('Speaker', 'speaker'),
        ('venue', 'venue')
    ])
    def it_adds_errors_to_list_for_a_non_existant_field(
        self, client, db_session, sample_event_type, sample_venue, sample_speaker, sample_data, field, desc,
        mock_storage_not_exists
    ):
        sample_data[1][field] = "0"
        response = client.post(
            url_for('events.import_events'),
            data=json.dumps(sample_data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_resp = json.loads(response.get_data(as_text=True))
        assert len(json_resp['events']) == 1
        assert len(json_resp['errors']) == 1
        assert str(json_resp['events'][0]["old_id"]) == str(sample_data[0]["id"])
        assert json_resp['errors'][0] == "{} {} not found: 0".format(sample_data[1]["id"], desc)


class WhenPostingCreatingAnEvent:
    @pytest.fixture
    def mock_storage_without_asserts(self, mocker):
        mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mocker.patch("app.storage.utils.Storage.upload_blob_from_base64string")

    @pytest.fixture
    def mock_storage(self, mocker):
        mock_storage = mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mock_storage_blob_upload = mocker.patch("app.storage.utils.Storage.upload_blob_from_base64string")
        yield
        mock_storage.assert_called_with('test-store')
        for event in Event.query.all():
            if event.image_filename:
                mock_storage_blob_upload.assert_called_with(
                    'test_img.png', '2019/{}'.format(str(event.id)), base64img)

    @freeze_time("2019-02-10T19:00:00")
    def it_creates_an_event_via_rest(
        self, mocker, client, db_session, sample_req_event_data, mock_storage_without_asserts, mock_paypal
    ):
        mocker.patch("app.storage.utils.Storage.blob_exists", return_value=True)

        speaker = create_speaker(name='Fred White')

        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "2019/test_img.png",
            "event_dates": [
                {
                    "event_date": "2019-03-01 19:00",
                    "end_time": "21:00",
                    "speakers": [
                        {"speaker_id": sample_req_event_data['speaker'].id}
                    ]
                },
                {
                    "event_date": "2019-03-02 19:00:00",
                    "end_time": "21:00",
                    "speakers": [
                        {"speaker_id": sample_req_event_data['speaker'].id},
                        {"speaker_id": speaker.id}
                    ]
                }
            ],
            "venue_id": sample_req_event_data['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }

        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 201

        json_events = json.loads(response.get_data(as_text=True))

        assert mock_paypal.call_args == call(
            json_events['id'],
            data['title'],
            data['fee'],
            data['conc_fee'],
            None,
            None,
            False
        )
        assert json_events["title"] == data["title"]
        assert json_events["booking_code"] == 'test booking code'
        assert len(json_events["event_dates"]) == 2
        assert len(json_events["event_dates"][0]["speakers"]) == 1
        assert len(json_events["event_dates"][1]["speakers"]) == 2
        assert json_events["event_dates"][0]["end_time"] == '21:00'
        assert json_events["event_dates"][1]["end_time"] == '21:00'
        assert json_events["event_dates"][0]["speakers"][0]['id'] == sample_req_event_data['speaker'].serialize()['id']
        assert json_events["event_dates"][1]["speakers"][0]['id'] == sample_req_event_data['speaker'].serialize()['id']
        assert json_events["event_dates"][1]["speakers"][1]['id'] == speaker.serialize()['id']

        event = Event.query.one()
        assert event.event_dates[0].end_time.strftime('%H:%M') == '21:00'
        assert event.event_dates[1].end_time.strftime('%H:%M') == '21:00'

    def it_creates_an_event_without_speakers_via_rest(
        self, mocker, client, db_session, sample_req_event_data, mock_storage_without_asserts, mock_paypal
    ):
        mocker.patch("app.storage.utils.Storage.blob_exists", return_value=True)
        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "test_img.png",
            "event_dates": [
                {
                    "event_date": "2019-03-01 19:00:00",
                },
                {
                    "event_date": "2019-03-02 19:00:00",
                }
            ],
            "venue_id": sample_req_event_data['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }

        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 201

        json_events = json.loads(response.get_data(as_text=True))
        assert json_events["title"] == data["title"]
        assert len(json_events["event_dates"]) == 2
        assert len(json_events["event_dates"][0]["speakers"]) == 0
        assert len(json_events["event_dates"][1]["speakers"]) == 0

    def it_raises_400_when_missing_required_fields(self, client):
        response = client.post(
            url_for('events.create_event'),
            data='{}',
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400

        data = json.loads(response.get_data(as_text=True))['errors']

        assert len(data) == 5
        assert data == [
            {"message": "event_type_id is a required property", "error": "ValidationError"},
            {"message": "title is a required property", "error": "ValidationError"},
            {"message": "description is a required property", "error": "ValidationError"},
            {"message": "event_dates is a required property", "error": "ValidationError"},
            {"message": "venue_id is a required property", "error": "ValidationError"}
        ]

    def it_raises_400_when_missing_event_date(self, client, db_session, sample_req_event_data):
        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "test_img.png",
            "event_dates": [],
            "venue_id": sample_req_event_data['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }
        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400

        data = json.loads(response.get_data(as_text=True))['errors']

        assert len(data) == 1
        assert data == [
            {"message": "event_dates [] is too short", "error": "ValidationError"},
        ]

    def it_raises_400_when_supply_invalid_event_type_id(self, client, sample_req_event_data, sample_uuid):
        data = {
            "event_type_id": sample_uuid,
            "title": "Test title",
            "description": "Test description",
            "event_dates": [{"event_date": "2019-03-01 19:00:00"}],
            "venue_id": sample_req_event_data['venue'].id,
        }

        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))

        assert data == {"message": "event type not found: {}".format(sample_uuid), "result": "error"}

    def it_raises_400_when_supply_invalid_venue_id(self, client, sample_req_event_data, sample_uuid):
        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "description": "Test description",
            "event_dates": [{"event_date": "2019-03-01 19:00:00"}],
            "venue_id": sample_uuid,
        }

        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))

        assert data == {"message": "venue not found: {}".format(sample_uuid), "result": "error"}

    @freeze_time("2019-03-01T23:10:00")
    def it_stores_the_image_in_google_store(
        self, client, db_session, sample_req_event_data, mock_storage
    ):
        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "description": "Test description",
            "image_filename": "test_img.png",
            "image_data": base64img,
            "event_dates": [
                {
                    "event_date": "2019-03-01 19:00:00",
                },
            ],
            "venue_id": sample_req_event_data['venue'].id,
        }

        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 201
        data = json.loads(response.get_data(as_text=True))
        assert data['image_filename'] == '2019/{}'.format(data['id'])

    def it_does_not_create_a_booking_code_without_fee(
        self, client, db_session, sample_req_event_data, mock_storage
    ):
        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "description": "Test description",
            "event_dates": [
                {
                    "event_date": "2019-03-01 19:00:00",
                },
            ],
            "venue_id": sample_req_event_data['venue'].id,
        }

        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 201
        data = json.loads(response.get_data(as_text=True))
        assert data["booking_code"] == ''

    def it_raises_400_if_image_filename_not_found(
        self, mocker, client, db_session, sample_req_event_data
    ):
        mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mocker.patch("app.storage.utils.Storage.blob_exists", return_value=False)
        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "description": "Test description",
            "image_filename": "test_img.png",
            "event_dates": [
                {
                    "event_date": "2019-03-01 19:00:00",
                },
            ],
            "venue_id": sample_req_event_data['venue'].id,
        }

        response = client.post(
            url_for('events.create_event'),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))

        assert data == {"message": "test_img.png does not exist", "result": "error"}


class WhenDeletingEvent:

    def it_deletes_an_event(self, client, sample_event, db_session):
        response = client.delete(
            url_for('events.delete_event', event_id=sample_event.id),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))

        assert data['message'] == "{} deleted".format(sample_event.id)
        assert Event.query.count() == 0

    def it_raises_500_if_deletion_fails_on_event(self, client, mocker, sample_event, db_session):
        mocker.patch("app.routes.events.rest.dao_delete_event")
        response = client.delete(
            url_for('events.delete_event', event_id=sample_event.id),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 500
        data = json.loads(response.get_data(as_text=True))

        assert data['message'] == '{} was not deleted'.format(sample_event.id)


class WhenPostingUpdatingAnEvent:

    @pytest.fixture
    def mock_storage(self, mocker):
        mock_storage = mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mock_storage_blob_exists = mocker.patch("app.storage.utils.Storage.blob_exists")
        yield
        mock_storage.assert_called_with('test-store')
        mock_storage_blob_exists.assert_called_with('2019/test_img.png')

    @pytest.fixture
    def mock_storage_not_exist(self, mocker):
        mock_storage = mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mock_storage_blob_exists = mocker.patch("app.storage.utils.Storage.blob_exists", return_value=False)
        yield
        mock_storage.assert_called_with('test-store')
        mock_storage_blob_exists.assert_called_with('2019/test_img.png')

    @pytest.fixture
    def mock_storage_upload(self, mocker):
        mock_storage = mocker.patch("app.storage.utils.Storage.__init__", return_value=None)
        mock_storage_blob_upload = mocker.patch("app.storage.utils.Storage.upload_blob_from_base64string")
        yield
        mock_storage.assert_called_with('test-store')
        for event in Event.query.all():
            if event.image_filename:
                mock_storage_blob_upload.assert_called_with(
                    'test_img.png', '2018/{}'.format(str(event.id)), base64img)

    def it_updates_an_event_via_rest(
        self, mocker, client, db_session, sample_req_event_data_with_event, mock_storage, mock_paypal
    ):
        data = {
            "event_type_id": sample_req_event_data_with_event['event_type'].id,
            "title": "Test title new",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "2019/test_img.png",
            "event_dates": [
                {
                    "event_date": "2019-02-10 19:00:00",
                    "speakers": [
                        {"speaker_id": sample_req_event_data_with_event['speaker'].id}
                    ]
                },
            ],
            "venue_id": sample_req_event_data_with_event['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }

        old_event_date_id = sample_req_event_data_with_event['event'].event_dates[0].id

        response = client.post(
            url_for('events.update_event', event_id=sample_req_event_data_with_event['event'].id),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 200

        json_events = json.loads(response.get_data(as_text=True))
        assert json_events["title"] == data["title"]
        assert json_events["image_filename"] == data["image_filename"]
        assert len(json_events["event_dates"]) == 1
        assert len(json_events["event_dates"][0]["speakers"]) == 1
        assert json_events["event_dates"][0]["speakers"][0]['id'] == (
            sample_req_event_data_with_event['speaker'].serialize()['id'])

        event_dates = EventDate.query.all()

        assert len(event_dates) == 1
        # use existing event date
        assert event_dates[0].id != old_event_date_id

    def it_updates_an_event_remove_speakers_via_rest(
        self, mocker, client, db_session, sample_req_event_data_with_event, mock_storage, mock_paypal
    ):
        data = {
            "event_type_id": sample_req_event_data_with_event['event_type'].id,
            "title": "Test title new",
            "sub_title": "Test sub title new",
            "description": "Test description new",
            "image_filename": "2019/test_img.png",
            "event_dates": [
                {
                    "event_date": str(sample_req_event_data_with_event['event'].event_dates[0].event_datetime),
                    "speakers": []
                },
            ],
            "venue_id": sample_req_event_data_with_event['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }

        old_event_date_id = sample_req_event_data_with_event['event'].event_dates[0].id

        response = client.post(
            url_for('events.update_event', event_id=sample_req_event_data_with_event['event'].id),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 200

        json_events = json.loads(response.get_data(as_text=True))
        assert json_events["title"] == data["title"]
        assert json_events["sub_title"] == data["sub_title"]
        assert json_events["description"] == data["description"]
        assert json_events["image_filename"] == data["image_filename"]
        assert len(json_events["event_dates"]) == 1
        assert len(json_events["event_dates"][0]["speakers"]) == 0

        event_dates = EventDate.query.all()

        assert len(event_dates) == 1
        assert event_dates[0].speakers == []
        # use existing event date
        assert event_dates[0].id == old_event_date_id

    def it_updates_an_event_remove_a_speaker_via_rest(
        self, mocker, client, db_session, mock_storage, mock_paypal
    ):
        speakers = [
            create_speaker(name='John Red'),
            create_speaker(name='Jane White')
        ]
        event_dates = [
            create_event_date(
                event_datetime='2019-02-01 19:00',
                speakers=speakers
            ),
            create_event_date(
                event_datetime='2019-02-02 19:00',
                speakers=speakers
            )
        ]
        event = create_event(
            event_dates=event_dates,
        )

        data = {
            "event_type_id": str(event.event_type_id),
            "title": "Test title new",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "2019/test_img.png",
            "event_dates": [
                {
                    "event_date": "2019-02-01 19:00:00",
                    "speakers": [
                        {"speaker_id": str(event.event_dates[0].speakers[1].id)},
                    ]
                },
                {
                    "event_date": "2019-02-02 19:00:00",
                    "speakers": [
                        {"speaker_id": str(event.event_dates[1].speakers[0].id)},
                        {"speaker_id": str(event.event_dates[1].speakers[1].id)},
                    ]
                },
            ],
            "venue_id": str(event.venue_id),
            "fee": 15,
            "conc_fee": 12,
        }

        old_event_date_id = event.event_dates[0].id

        response = client.post(
            url_for('events.update_event', event_id=event.id),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 200

        json_events = json.loads(response.get_data(as_text=True))

        assert json_events["title"] == data["title"]
        assert json_events["image_filename"] == data["image_filename"]
        assert len(json_events["event_dates"]) == 2
        assert len(json_events["event_dates"][0]["speakers"]) == 1
        assert len(json_events["event_dates"][1]["speakers"]) == 2

        event_dates = EventDate.query.all()

        assert len(event_dates) == 2
        assert event_dates[0].speakers[0].id == event.event_dates[0].speakers[0].id
        # use existing event date
        assert event_dates[0].id == old_event_date_id

    def it_updates_an_event_add_speakers_via_rest(
        self, mocker, client, db_session, sample_req_event_data_with_event, mock_storage_upload, mock_paypal
    ):
        speaker = create_speaker(name='Julie White')

        data = {
            "event_type_id": sample_req_event_data_with_event['event_type'].id,
            "title": "Test title new",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "test_img.png",
            "image_data": base64img,
            "event_dates": [
                {
                    "event_date": str(sample_req_event_data_with_event['event'].event_dates[0].event_datetime),
                    "speakers": [
                        {"speaker_id": sample_req_event_data_with_event['speaker'].id},
                        {"speaker_id": speaker.id}
                    ]
                },
            ],
            "venue_id": sample_req_event_data_with_event['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }

        old_event_date_id = sample_req_event_data_with_event['event'].event_dates[0].id

        response = client.post(
            url_for('events.update_event', event_id=sample_req_event_data_with_event['event'].id),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 200

        json_events = json.loads(response.get_data(as_text=True))
        assert json_events["title"] == data["title"]
        assert json_events["image_filename"] == data["image_filename"]
        assert len(json_events["event_dates"]) == 1
        assert len(json_events["event_dates"][0]["speakers"]) == 2

        event_dates = EventDate.query.all()

        assert len(event_dates) == 1
        assert len(event_dates[0].speakers) == 2
        # use existing event date
        assert event_dates[0].id == old_event_date_id

    def it_updates_an_event_add_event_dates_via_rest(
        self, mocker, client, db_session, sample_req_event_data_with_event, mock_storage_upload, mock_paypal
    ):
        data = {
            "event_type_id": sample_req_event_data_with_event['event_type'].id,
            "title": "Test title new",
            "sub_title": "Test sub title",
            "description": "Test description",
            "image_filename": "test_img.png",
            "image_data": base64img,
            "event_dates": [
                {
                    "event_date": str(sample_req_event_data_with_event['event'].event_dates[0].event_datetime),
                    "speakers": [
                        {"speaker_id": sample_req_event_data_with_event['speaker'].id}
                    ]
                },
                {
                    "event_date": str(
                        sample_req_event_data_with_event['event'].event_dates[0].event_datetime + timedelta(days=1)
                    ),
                    "speakers": [
                        {"speaker_id": sample_req_event_data_with_event['speaker'].id}
                    ]
                },
            ],
            "venue_id": sample_req_event_data_with_event['venue'].id,
            "fee": 15,
            "conc_fee": 12,
        }

        old_event_date_id = sample_req_event_data_with_event['event'].event_dates[0].id

        response = client.post(
            url_for('events.update_event', event_id=sample_req_event_data_with_event['event'].id),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 200

        json_events = json.loads(response.get_data(as_text=True))
        assert json_events["title"] == data["title"]
        assert json_events["image_filename"] == data["image_filename"]
        assert len(json_events["event_dates"]) == 2
        assert len(json_events["event_dates"][0]["speakers"]) == 1

        event_dates = EventDate.query.all()

        assert len(event_dates) == 2
        assert len(event_dates[0].speakers) == 1
        # use existing event date
        assert event_dates[0].id == old_event_date_id

    def it_updates_an_event_adding_booking_code_if_no_fee_before_via_rest(
        self, mocker, client, db_session, sample_req_event_data, mock_storage_upload, mock_paypal
    ):
        event = create_event(
            event_type_id=sample_req_event_data['event_type'].id,
            event_dates=[
                create_event_date(
                    event_datetime='2018-01-20T19:00:00',
                    speakers=[
                        sample_req_event_data['speaker']
                    ]
                )
            ],
            fee=None,
            conc_fee=None,
            venue_id=sample_req_event_data['venue'].id
        )

        data = {
            "event_type_id": sample_req_event_data['event_type'].id,
            "title": "Test title",
            "sub_title": "Test sub title",
            "description": "Test description",
            "event_dates": [
                {
                    "event_date": str(event.event_dates[0].event_datetime),
                    "speakers": [
                        {"speaker_id": sample_req_event_data['speaker'].id}
                    ]
                },
            ],
            "venue_id": sample_req_event_data['venue'].id,
            "fee": 15,
            "conc_fee": 12,
            "booking_code": "test booking"
        }

        response = client.post(
            url_for('events.update_event', event_id=event.id),
            data=json.dumps(data),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 200

        json_events = json.loads(response.get_data(as_text=True))
        assert json_events["title"] == data["title"]
        assert json_events['booking_code'] == "test booking code"
        assert mock_paypal.call_args == call(
            event.id, u'Test title', 15, 12, None, None, False, booking_code='test booking')

    def it_raises_error_if_file_not_found(
        self, mocker, client, db_session, sample_req_event_data_with_event, mock_storage_not_exist
    ):
        response = client.post(
            url_for('events.update_event', event_id=sample_req_event_data_with_event['event'].id),
            data=json.dumps(sample_req_event_data_with_event['data']),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['message'] == '2019/test_img.png does not exist'

    def it_raises_error_if_event_not_updated(
        self, mocker, client, db_session, sample_req_event_data_with_event, mock_storage, mock_paypal
    ):
        mocker.patch('app.routes.events.rest.dao_update_event', return_value=False)

        response = client.post(
            url_for('events.update_event', event_id=sample_req_event_data_with_event['event'].id),
            data=json.dumps(sample_req_event_data_with_event['data']),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['message'] == '{} did not update'.format(sample_req_event_data_with_event['event'].id)

    def it_raises_error_if_event_not_found(
        self, mocker, client, db_session, sample_req_event_data_with_event, sample_uuid
    ):
        mocker.patch('app.routes.events.rest.dao_get_event_by_id', side_effect=NoResultFound())

        response = client.post(
            url_for('events.update_event', event_id=sample_uuid),
            data=json.dumps(sample_req_event_data_with_event['data']),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )

        assert response.status_code == 400

        json_resp = json.loads(response.get_data(as_text=True))

        assert json_resp['message'] == 'event not found: {}'.format(sample_uuid)


class WhenTestingPaypal:

    def it_creates_a_paypal_button_in_preview(self, mocker, client, sample_uuid, mock_paypal):
        mocker.patch.dict('app.routes.events.rest.current_app.config', {'ENVIRONMENT': 'test'})
        response = client.post(
            url_for('events.create_test_paypal', item_id=sample_uuid),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert mock_paypal.call_args == call(sample_uuid, 'test paypal')
        resp_text = response.get_data(as_text=True)
        print(resp_text)
        assert resp_text == 'test booking code'

    def it_does_not_create_a_paypal_button_in_live(self, mocker, client, sample_uuid, mock_paypal):
        mocker.patch.dict('app.routes.events.rest.current_app.config', {'ENVIRONMENT': 'live'})

        response = client.post(
            url_for('events.create_test_paypal', item_id=sample_uuid),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.get_data(as_text=True) == 'Cannot test paypal on live environment'
