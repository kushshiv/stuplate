"""empty message

Revision ID: e35cf64c9431
Revises: e2256fd36faf
Create Date: 2019-12-13 23:11:47.568032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e35cf64c9431'
down_revision = 'e2256fd36faf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student_coaching_relation', sa.Column('CoachingSubject', sa.String(length=140), nullable=True))
    op.drop_column('student_coaching_relation', 'CoachingStubject')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student_coaching_relation', sa.Column('CoachingStubject', sa.VARCHAR(length=140), nullable=True))
    op.drop_column('student_coaching_relation', 'CoachingSubject')
    # ### end Alembic commands ###
