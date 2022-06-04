"""empty message

Revision ID: 4068451aa01e
Revises: 5b211a959a8c
Create Date: 2022-06-03 11:31:04.861921

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4068451aa01e'
down_revision = '5b211a959a8c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'genres')
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    op.add_column('artist', sa.Column('genres', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    # ### end Alembic commands ###