"""Add model_versions table

Revision ID: 3754c1ed7f3c
Revises: 2754c1ed6e2c
Create Date: 2025-03-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3754c1ed7f3c'
down_revision = '2754c1ed6e2c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create model_versions table
    op.create_table('model_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_name', sa.String(), nullable=False),
        sa.Column('model_type', sa.String(), nullable=False),
        sa.Column('creation_date', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('hyperparameters', sa.Text(), nullable=True),
        sa.Column('feature_importance', sa.Text(), nullable=True),
        sa.Column('metrics', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_versions_id'), 'model_versions', ['id'], unique=False)
    op.create_index(op.f('ix_model_versions_version_name'), 'model_versions', ['version_name'], unique=True)
    
    # Add model_version_id to predictions table
    op.add_column('predictions', sa.Column('model_version_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_prediction_model_version', 'predictions', 'model_versions', ['model_version_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key first
    op.drop_constraint('fk_prediction_model_version', 'predictions', type_='foreignkey')
    op.drop_column('predictions', 'model_version_id')
    
    # Drop model_versions table
    op.drop_index(op.f('ix_model_versions_version_name'), table_name='model_versions')
    op.drop_index(op.f('ix_model_versions_id'), table_name='model_versions')
    op.drop_table('model_versions')