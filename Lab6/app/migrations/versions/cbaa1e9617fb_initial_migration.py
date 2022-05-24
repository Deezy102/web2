"""Initial migration.

Revision ID: cbaa1e9617fb
Revises: 
Create Date: 2022-05-18 17:38:58.636694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbaa1e9617fb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], name=op.f('fk_categories_parent_id_categories')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_categories'))
    )
    data_upgrades()
    # ### end Alembic commands ###

def data_upgrades():
    table = sa.sql.table('categories', sa.sql.column('name'))
    op.bulk_insert(table,
        [
            { 'name': 'Программирование' },
            { 'name': 'Математика' },
            { 'name': 'Языкознания' },
        ]
    )
def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('categories')
    # ### end Alembic commands ###