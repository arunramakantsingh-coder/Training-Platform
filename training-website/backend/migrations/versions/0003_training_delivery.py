from alembic import op
import sqlalchemy as sa

revision = "0003_training_delivery"
down_revision = "0002_course_catalogue"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "training_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("trainer_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enrollment_limit", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trainer_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("course_id", "slug", name="uq_training_session_course_slug"),
    )
    op.create_index("ix_training_sessions_course_id", "training_sessions", ["course_id"])
    op.create_index("ix_training_sessions_trainer_user_id", "training_sessions", ["trainer_user_id"])
    op.create_index("ix_training_sessions_status", "training_sessions", ["status"])

    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("training_session_id", sa.Integer(), sa.ForeignKey("training_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["training_session_id"], ["training_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("training_session_id", "user_id", name="uq_enrollment_session_user"),
    )
    for name,col in [("ix_enrollments_course_id","course_id"),("ix_enrollments_training_session_id","training_session_id"),("ix_enrollments_user_id","user_id"),("ix_enrollments_organization_id","organization_id"),("ix_enrollments_status","status")]:
        op.create_index(name,"enrollments",[col])

    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("enrollment_id", sa.Integer(), sa.ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="not_started"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["enrollment_id"], ["enrollments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("enrollment_id", "lesson_id", name="uq_progress_enrollment_lesson"),
    )
    op.create_index("ix_lesson_progress_enrollment_id","lesson_progress",["enrollment_id"])
    op.create_index("ix_lesson_progress_lesson_id","lesson_progress",["lesson_id"])

def downgrade() -> None:
    op.drop_index("ix_lesson_progress_lesson_id", table_name="lesson_progress")
    op.drop_index("ix_lesson_progress_enrollment_id", table_name="lesson_progress")
    op.drop_table("lesson_progress")
    for name in ["ix_enrollments_status","ix_enrollments_organization_id","ix_enrollments_user_id","ix_enrollments_training_session_id","ix_enrollments_course_id"]:
        op.drop_index(name, table_name="enrollments")
    op.drop_table("enrollments")
    for name in ["ix_training_sessions_status","ix_training_sessions_trainer_user_id","ix_training_sessions_course_id"]:
        op.drop_index(name, table_name="training_sessions")
    op.drop_table("training_sessions")
