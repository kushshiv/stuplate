"""coachingclasses table

Revision ID: cfe6bf53fb21
Revises: 25b15ff37c04
Create Date: 2019-09-15 12:01:45.036318

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfe6bf53fb21'
down_revision = '25b15ff37c04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coaching_class', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'coaching_class', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'coaching_class', type_='foreignkey')
    op.drop_column('coaching_class', 'user_id')
    # ### end Alembic commands ###
