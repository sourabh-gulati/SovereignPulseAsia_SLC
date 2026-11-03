"""Add an index for selecting the newest stored daily observation."""
from alembic import op


revision = "0002_daily_yield_lookup"
down_revision = "0001_yield_observations"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_yield_observations_date_maturity",
        "yield_observations",
        ["observation_date", "maturity_years"],
    )


def downgrade():
    op.drop_index("ix_yield_observations_date_maturity", table_name="yield_observations")
