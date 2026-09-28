"""initial_schema_and_privascope_v2

Revision ID: 37468fd18880
Revises: 
Create Date: 2026-09-28 16:14:15.789207

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '37468fd18880'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema idempotently."""
    bind = op.get_bind()
    bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_users"))
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'users' in existing_tables:
        user_cols = {c['name'] for c in inspector.get_columns('users')}
        with op.batch_alter_table('users', schema=None) as batch_op:
            if 'google_sub' not in user_cols:
                batch_op.add_column(sa.Column('google_sub', sa.String(length=255), nullable=True))
            if 'auth_provider' not in user_cols:
                batch_op.add_column(sa.Column('auth_provider', sa.String(length=50), nullable=False, server_default='local'))
            if 'email_verified' not in user_cols:
                batch_op.add_column(sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='0'))
            if 'avatar_url' not in user_cols:
                batch_op.add_column(sa.Column('avatar_url', sa.String(length=500), nullable=True))
            if 'is_active' not in user_cols:
                batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))
            if 'last_login_at' not in user_cols:
                batch_op.add_column(sa.Column('last_login_at', sa.DateTime(), nullable=True))
            batch_op.alter_column('password_hash', existing_type=sa.VARCHAR(length=255), nullable=True)

    if 'gateway_audit_logs' not in existing_tables:
        op.create_table(
            'gateway_audit_logs',
            sa.Column('id', sa.String(length=36), primary_key=True),
            sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('session_id', sa.String(length=64), nullable=False, index=True),
            sa.Column('provider', sa.String(length=50), nullable=False),
            sa.Column('policy_decision', sa.String(length=20), nullable=False),
            sa.Column('risk_score', sa.Float(), nullable=True, default=0.0),
            sa.Column('entities_detected_count', sa.Integer(), nullable=True, default=0),
            sa.Column('entity_types_json', sa.Text(), nullable=True),
            sa.Column('detection_latency_ms', sa.Float(), nullable=True, default=0.0),
            sa.Column('policy_latency_ms', sa.Float(), nullable=True, default=0.0),
            sa.Column('tokenization_latency_ms', sa.Float(), nullable=True, default=0.0),
            sa.Column('provider_latency_ms', sa.Float(), nullable=True, default=0.0),
            sa.Column('total_latency_ms', sa.Float(), nullable=True, default=0.0),
            sa.Column('created_at', sa.DateTime(), nullable=True, index=True),
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'gateway_audit_logs' in existing_tables:
        op.drop_table('gateway_audit_logs')

    if 'users' in existing_tables:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.drop_column('avatar_url')
            batch_op.drop_column('email_verified')
            batch_op.drop_column('auth_provider')
            batch_op.drop_column('google_sub')
