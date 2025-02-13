"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create institutional_ids table
    op.create_table(
        'institutional_ids',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('main_id', sa.String(12), nullable=False),
        sa.Column('id_type', sa.Enum('student', 'employee', 'member', 'visitor', name='id_types'), nullable=False),
        sa.Column('id_number', sa.String(20), nullable=False),
        sa.Column('department', sa.String(100)),
        sa.Column('position', sa.String(100)),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime()),
        sa.Column('access_level', sa.String(50)),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('additional_info', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('revoked_at', sa.DateTime()),
        sa.Column('revoked_by', sa.Integer()),
        sa.Column('revocation_reason', sa.String(255)),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_institutional_ids_id', 'institutional_ids', ['id'])
    op.create_index('ix_institutional_ids_main_id', 'institutional_ids', ['main_id'])
    op.create_index('ix_institutional_ids_id_number', 'institutional_ids', ['id_number'])

def downgrade() -> None:
    op.drop_index('ix_institutional_ids_id_number')
    op.drop_index('ix_institutional_ids_main_id')
    op.drop_index('ix_institutional_ids_id')
    op.drop_table('institutional_ids') 