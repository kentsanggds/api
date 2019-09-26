"""empty message

Revision ID: 0032 orders,tickets,ticket_types
Revises: 0031 add email_to_member
Create Date: 2019-09-07 01:35:24.552085

"""

# revision identifiers, used by Alembic.
revision = '0032 orders,tickets,ticket_types'
down_revision = '0031 add email_to_member'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.models import TICKET_TYPES, TICKET_STATUS_UNUSED, TICKET_STATUS_USED

def upgrade():
    op.create_table('ticket_types',
    sa.Column('_type', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('_type')
    )

    for ticket in TICKET_TYPES:
        op.execute(
            "INSERT INTO ticket_types (_type) VALUES ('{}')".format(ticket)
        )

    op.create_table('ticket_statuses',
    sa.Column('status', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('status')
    )

    op.execute(
        "INSERT INTO ticket_statuses (status) VALUES ('{}')".format(TICKET_STATUS_UNUSED)
    )

    op.execute(
        "INSERT INTO ticket_statuses (status) VALUES ('{}')".format(TICKET_STATUS_USED)
    )

    op.create_table('orders',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('old_id', sa.Integer(), nullable=True),
    sa.Column('member_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('old_member_id', sa.Integer(), nullable=True),
    sa.Column('email_address', sa.String(), nullable=True),
    sa.Column('buyer_name', sa.String(), nullable=True),
    sa.Column('txn_id', sa.String(), nullable=True),
    sa.Column('txn_type', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('payment_status', sa.String(), nullable=True),
    sa.Column('payment_total', sa.Numeric(precision=2), nullable=True),
    sa.Column('params', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('tickets',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('old_id', sa.Integer(), nullable=True),
    sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('old_event_id', sa.Integer(), nullable=True),
    sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('old_order_id', sa.Integer(), nullable=True),
    sa.Column('ticket_type', sa.String(), nullable=True),
    sa.Column('eventdate_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('price', sa.Numeric(precision=2), nullable=True),
    sa.Column('ticket_number', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['eventdate_id'], ['event_dates.id'], ),
    sa.ForeignKeyConstraint(['ticket_type'], ['ticket_types._type'], ),
    sa.ForeignKeyConstraint(['status'], ['ticket_statuses.status'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('tickets')
    op.drop_table('orders')
    op.drop_table('ticket_types')
    op.drop_table('ticket_statuses')
