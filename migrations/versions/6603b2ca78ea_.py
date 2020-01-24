"""empty message

Revision ID: 6603b2ca78ea
Revises: ff721ef063a1
Create Date: 2020-01-24 22:33:14.019534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6603b2ca78ea'
down_revision = 'ff721ef063a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('coaching_batches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('batchIsActive', sa.String(length=140), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('coaching_batches', schema=None) as batch_op:
        batch_op.drop_column('batchIsActive')

    # ### end Alembic commands ###
