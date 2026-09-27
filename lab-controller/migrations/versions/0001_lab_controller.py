from alembic import op
import sqlalchemy as sa

revision = "0001_lab_controller"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("lab_templates", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("key", sa.String(100), nullable=False, unique=True), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("labs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("template_id", sa.Integer(), nullable=False), sa.Column("owner_user_id", sa.Integer()), sa.Column("name", sa.String(200), nullable=False), sa.Column("state", sa.String(32), nullable=False, server_default="created"), sa.Column("external_reference", sa.String(255)), sa.Column("access_url", sa.String(1000)), sa.Column("error_message", sa.String(2000)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("lab_assignments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("lab_id", sa.Integer(), nullable=False), sa.Column("user_id", sa.Integer(), nullable=False), sa.Column("status", sa.String(32), nullable=False, server_default="active"), sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False), sa.Column("released_at", sa.DateTime(timezone=True)))
    op.create_table("lab_usage", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("lab_id", sa.Integer(), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True)), sa.Column("stopped_at", sa.DateTime(timezone=True)), sa.Column("seconds_used", sa.Integer(), nullable=False, server_default="0"))

def downgrade():
    op.drop_table("lab_usage")
    op.drop_table("lab_assignments")
    op.drop_table("labs")
    op.drop_table("lab_templates")
