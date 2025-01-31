import base64
import json
import io
import pyqrcode
import sys
from urllib import unquote
import requests
from datetime import datetime
from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    url_for
)
import os.path
import re
from sqlalchemy.orm.exc import NoResultFound
import time

from flask_jwt_extended import jwt_required

from app.comms.email import send_email
from app.dao import dao_create_record
from app.dao.events_dao import dao_get_event_by_id
from app.dao.event_dates_dao import dao_get_event_date_on_date, dao_get_event_date_by_id
from app.dao.orders_dao import dao_get_order_with_txn_id
from app.dao.tickets_dao import dao_get_ticket_id, dao_update_ticket
from app.errors import register_errors, InvalidRequest

from app.models import Order, Ticket, TICKET_STATUS_USED
from app.storage.utils import Storage

orders_blueprint = Blueprint('orders', __name__)
register_errors(orders_blueprint)


@orders_blueprint.route('/orders/paypal/ipn', methods=['GET', 'POST'])
def paypal_ipn():
    VERIFY_URL = current_app.config['PAYPAL_VERIFY_URL']

    params = request.form.to_dict(flat=False)
    current_app.logger.info('IPN params: %r', params)

    params['cmd'] = '_notify-validate'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Python-IPN-Verification-Script'
    }
    r = requests.post(VERIFY_URL, params=params, headers=headers, verify=True)
    r.raise_for_status()

    # Check return message and take action as needed
    if r.text == 'VERIFIED':
        current_app.logger.info('VERIFIED: %s', params['txn_id'])

        data = {}
        for key in params.keys():
            if isinstance(params[key], list):
                data[key] = params[key][0]
            else:
                data[key] = params[key]

        order_data, tickets, events = parse_ipn(data)

        if not order_data:
            return 'Paypal IPN no order created'
        order_data['params'] = json.dumps(params)

        order = Order(**order_data)

        dao_create_record(order)
        for i, _ticket in enumerate(tickets):
            _ticket['order_id'] = order.id
            ticket = Ticket(**_ticket)
            dao_create_record(ticket)
            tickets[i]['ticket_id'] = ticket.id

        storage = Storage(current_app.config['STORAGE'])
        message = "<p>Thank you for your order:<p>"
        for i, event in enumerate(events):
            link_to_post = '{}{}'.format(
                current_app.config['API_BASE_URL'], url_for('.use_ticket', ticket_id=tickets[i]['ticket_id']))
            img = pyqrcode.create(link_to_post)
            buffer = io.BytesIO()
            img.png(buffer, scale=2)

            img_b64 = base64.b64encode(buffer.getvalue())
            target_image_filename = '{}{}'.format('qr_codes', str(tickets[i]['ticket_id']))
            storage.upload_blob_from_base64string('qr.code', target_image_filename, img_b64)

            message += '<div><span><img src="{}/{}"></span>'.format(
                current_app.config['IMAGES_URL'], target_image_filename)

            event_date = dao_get_event_date_by_id(tickets[i]['eventdate_id'])
            minutes = ':%M' if event_date.event_datetime.minute > 0 else ''
            message += "<span>{} on {}</span></div>".format(
                event.title, event_date.event_datetime.strftime('%-d %b at %-I{}%p'.format(minutes)))

        send_email(order.email_address, 'New Acropolis Event Tickets', message)

    elif r.text == 'INVALID':
        current_app.logger.info('INVALID %r', params['txn_id'])
    else:
        current_app.logger.info('UNKNOWN response %r', params['txn_id'])

    return 'Paypal IPN'


@orders_blueprint.route('/orders/ticket/<string:ticket_id>', methods=['GET'])
def use_ticket(ticket_id):
    ticket = dao_get_ticket_id(ticket_id)

    if not ticket.event.is_event_today(ticket.eventdate_id):
        data = {
            'update_response': 'Event is not today'
        }
    else:
        if ticket.status == TICKET_STATUS_USED:
            data = {
                'update_response': 'Ticket already used'
            }
        else:
            dao_update_ticket(ticket_id, status=TICKET_STATUS_USED)

            data = {
                'update_response': 'Ticket updated to used'
            }

    data['ticket_id'] = ticket_id
    data['title'] = ticket.event.title

    return jsonify(data)


def parse_ipn(ipn):
    order_data = {}
    receiver_email = None
    tickets = []
    events = []

    order_mapping = {
        'payer_email': 'email_address',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'payment_status': 'payment_status',
        'txn_type': 'txn_type',
        'mc_gross': 'payment_total',
        'txn_id': 'txn_id',
    }

    for key in ipn.keys():
        if key == 'receiver_email':
            receiver_email = ipn[key]
        if key in order_mapping.keys():
            order_data[order_mapping[key]] = ipn[key]

    if order_data['payment_status'] != 'Completed':
        current_app.logger.error(
            'Order: %s, payment not complete: %s', order_data['txn_id'], order_data['payment_status'])
        return None, None, None

    if receiver_email != current_app.config['PAYPAL_RECEIVER']:
        current_app.logger.error('Paypal receiver not valid: %s for %s', receiver_email, order_data['txn_id'])
        order_data['payment_status'] = 'Invalid receiver'
        return None, None, None

    order_found = dao_get_order_with_txn_id(order_data['txn_id'])
    if order_found:
        current_app.logger.error(
            'Order: %s, payment already made', order_data['txn_id'])
        return None, None, None

    if ipn['txn_type'] == 'paypal_here':
        _event_date = datetime.strptime(ipn['payment_date'], '%H:%M:%S %b %d, %Y PST').strftime('%Y-%m-%d')
        event_date = dao_get_event_date_on_date(_event_date)

        ticket = {
            'ticket_number': 1,
            'event_id': event_date.event_id,
            'eventdate_id': event_date.id,
            'status': TICKET_STATUS_USED
        }
        event = dao_get_event_by_id(event_date.event_id)
        events.append(event)

        tickets.append(ticket)
    else:
        counter = 1
        while ('item_number%d' % counter) in ipn:
            try:
                event = dao_get_event_by_id(ipn['item_number%d' % counter])
                events.append(event)
            except NoResultFound:
                current_app.logger.error("Event not found for item_number: %s", ipn['item_number%d' % counter])
                counter += 1
                continue

            event_date_index = int(ipn['option_selection2_%d' % counter]) \
                if ipn['option_name2_%d' % counter] == 'Date' else None
            if not event_date_index:
                event_date_index = 1

            if event_date_index > len(event.event_dates):
                current_app.logger.error(
                    "Event date %s not found for: %s", event_date_index, ipn['item_number%d' % counter])
                counter += 1
                continue

            event_date_id = event.event_dates[event_date_index - 1].id
            quantity = int(ipn['quantity%d' % counter])
            price = float("{0:.2f}".format(float(ipn['mc_gross_%d' % counter]) / quantity))

            for i in range(1, quantity + 1):
                ticket = {
                    'ticket_number': i,
                    'event_id': event.id,
                    'ticket_type': ipn['option_selection1_%d' % counter],
                    'eventdate_id': event_date_id,
                    'price': price,
                    'name':
                        ipn.get('option_selection3_%d' % counter)
                        if ipn.get('option_name3_%d' % counter) == 'Course Member name'
                        else ipn.get('option_selection2_%d' % counter)
                        if ipn['option_name2_%d' % counter] == 'Course Member name'
                        else None
                }
                tickets.append(ticket)
            counter += 1

    if not tickets:
        current_app.logger.error('No valid tickets, no order created: %s', order_data['txn_id'])
        return None, None, None

    order_data['buyer_name'] = '{} {}'.format(order_data['first_name'], order_data['last_name'])
    del order_data['first_name']
    del order_data['last_name']

    return order_data, tickets, events
