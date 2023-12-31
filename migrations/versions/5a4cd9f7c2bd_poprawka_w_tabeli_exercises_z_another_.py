"""Poprawka w tabeli Exercises z another_body_part na another_body_part_id

Revision ID: 5a4cd9f7c2bd
Revises: 29ce1810b228
Create Date: 2023-12-11 20:14:13.597550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a4cd9f7c2bd'
down_revision = '29ce1810b228'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exercises', schema=None) as batch_op:
        batch_op.alter_column('another_body_part', new_column_name='another_body_part_id')
        # batch_op.add_column(sa.Column('another_body_part_id', sa.Integer(), nullable=True))
        # batch_op.drop_constraint(None, type_='foreignkey')
        # batch_op.create_foreign_key(None, 'body_parts', ['another_body_part_id'], ['id'])
        # batch_op.drop_column('another_body_part')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exercises', schema=None) as batch_op:
        batch_op.alter_column('another_body_part_id', new_column_name='another_body_part')
        # batch_op.add_column(sa.Column('another_body_part', sa.INTEGER(), nullable=True))
        # batch_op.drop_constraint(None, type_='foreignkey')
        # batch_op.create_foreign_key(None, 'body_parts', ['another_body_part'], ['id'])
        # batch_op.drop_column('another_body_part_id')

    # ### end Alembic commands ###
