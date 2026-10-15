"""create appointments table"""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_appointments"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_name", sa.String(length=120), nullable=False),
        sa.Column("patient_phone", sa.String(length=20), nullable=False, server_default=""),
        sa.Column("doctor", sa.String(length=120), nullable=False),
        sa.Column("department", sa.String(length=40), nullable=False, server_default="GENERAL"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="SCHEDULED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_appointments_scheduled_at", "appointments", ["scheduled_at"])


def downgrade():
    op.drop_index("ix_appointments_scheduled_at", table_name="appointments")
    op.drop_table("appointments")
