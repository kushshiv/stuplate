"""users table

Revision ID: 561c2234d90e
Revises: f6aba2c1a96f
Create Date: 2019-09-23 21:27:41.253132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '561c2234d90e'
down_revision = 'f6aba2c1a96f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('coaching_class', 'coachingpassword_hash')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coaching_class', sa.Column('coachingpassword_hash', sa.VARCHAR(length=128), nullable=True))
    # ### end Alembic commands ###