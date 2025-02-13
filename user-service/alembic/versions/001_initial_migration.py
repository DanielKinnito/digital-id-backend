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
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('main_id', sa.String(12), unique=True, nullable=False),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('last_name', sa.String(50), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.Enum('Male', 'Female', 'Other', name='gender_types'), nullable=False),
        sa.Column('nationality', sa.String(50), nullable=False),
        sa.Column('current_address', sa.String(255), nullable=False),
        sa.Column('phone_number', sa.String(20)),
        sa.Column('email', sa.String(100), unique=True),
        sa.Column('institutional_ids', postgresql.JSON(astext_type=sa.Text()), default=dict),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer()),
        sa.Column('last_updated_by', sa.Integer()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_main_id', 'users', ['main_id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Create biometric_data table
    op.create_table(
        'biometric_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('fingerprint_template', sa.Text(), nullable=False),
        sa.Column('photo_reference', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create update_requests table
    op.create_table(
        'update_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('requested_changes', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.Column('reviewed_by', sa.Integer()),
        sa.Column('rejection_reason', sa.String(255)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('update_requests')
    op.drop_table('biometric_data')
    op.drop_index('ix_users_email')
    op.drop_index('ix_users_main_id')
    op.drop_index('ix_users_id')
    op.drop_table('users') 