"""Create Treasury yield observations."""
from alembic import op
import sqlalchemy as sa

revision = "0001_yield_observations"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "yield_observations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("observation_date", sa.Date(), nullable=False),
        sa.Column("tenor", sa.String(length=8), nullable=False),
        sa.Column("maturity_years", sa.Float(), nullable=False),
        sa.Column("yield_percent", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=False, server_default="US Treasury"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("observation_date", "tenor", name="uq_yield_date_tenor"),
    )
    op.create_index("ix_yield_observations_observation_date", "yield_observations", ["observation_date"])
    op.create_index("ix_yield_observations_tenor", "yield_observations", ["tenor"])
    op.create_index("ix_yield_observations_id", "yield_observations", ["id"])

def downgrade():
    op.drop_index("ix_yield_observations_id", table_name="yield_observations")
    op.drop_index("ix_yield_observations_tenor", table_name="yield_observations")
    op.drop_index("ix_yield_observations_observation_date", table_name="yield_observations")
    op.drop_table("yield_observations")
