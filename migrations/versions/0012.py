"""empty message

Revision ID: 0012 allow null speaker event
Revises: 0011 update events model
Create Date: 2018-09-15 00:22:34.418001

"""

# revision identifiers, used by Alembic.
revision = '0012 allow null speaker event'
down_revision = '0011 update events model'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('events', 'speaker_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('events', 'speaker_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    # ### end Alembic commands ###
