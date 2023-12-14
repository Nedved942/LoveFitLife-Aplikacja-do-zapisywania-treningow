"""Poprawienie wlasciwosci kolumn w definicji tabeli User()

Revision ID: 4d1def390347
Revises: c7b47743eaa4
Create Date: 2023-12-14 15:36:25.945637

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d1def390347'
down_revision = 'c7b47743eaa4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('nick',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.create_unique_constraint('unique_user_nick', ['nick'])
        batch_op.create_unique_constraint('unique_user_email', ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('nick',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)

    # ### end Alembic commands ###