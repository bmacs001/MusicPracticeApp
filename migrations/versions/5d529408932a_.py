"""empty message

Revision ID: 5d529408932a
Revises: 24985e25c569
Create Date: 2020-12-06 18:04:31.492209

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d529408932a'
down_revision = '24985e25c569'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('regiment', sa.Column('goalInSeconds', sa.Integer(), nullable=True))
    op.add_column('regiment', sa.Column('timeElapsedInSeconds', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('regiment', 'timeElapsedInSeconds')
    op.drop_column('regiment', 'goalInSeconds')
    # ### end Alembic commands ###
