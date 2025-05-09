"""Creates one to many relationship between goal and tasks

Revision ID: 1acf1ca700ee
Revises: a0d600803c9e
Create Date: 2025-05-07 11:28:10.092753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1acf1ca700ee'
down_revision = 'a0d600803c9e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('goal_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'goal', ['goal_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('goal_id')

    # ### end Alembic commands ###
