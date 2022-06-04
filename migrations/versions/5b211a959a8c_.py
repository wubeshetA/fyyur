"""empty message

Revision ID: 5b211a959a8c
Revises: 
Create Date: 2022-06-03 01:20:36.693338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b211a959a8c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('artist', sa.Column('upcoming_shows_count', sa.Integer(), nullable=True))
    op.add_column('artist', sa.Column('past_shows_count', sa.Integer(), nullable=True))
    op.add_column('venue', sa.Column('website_link', sa.String(length=200), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=1000), nullable=True))
    op.add_column('venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('venue', sa.Column('upcoming_shows_count', sa.Integer(), nullable=True))
    op.add_column('venue', sa.Column('past_shows_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'past_shows_count')
    op.drop_column('venue', 'upcoming_shows_count')
    op.drop_column('venue', 'genres')
    op.drop_column('venue', 'seeking_description')
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'website_link')
    op.drop_column('artist', 'past_shows_count')
    op.drop_column('artist', 'upcoming_shows_count')
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'seeking_venue')
    op.drop_column('artist', 'website_link')
    # ### end Alembic commands ###
