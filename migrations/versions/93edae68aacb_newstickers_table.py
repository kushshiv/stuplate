"""newstickers table

Revision ID: 93edae68aacb
Revises: 9bf6633a99fd
Create Date: 2019-08-05 16:39:00.267776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93edae68aacb'
down_revision = '9bf6633a99fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('newsticker',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('news', sa.String(length=140), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('newsticker')
    # ### end Alembic commands ###
