"""rename worker -> workers, access_log -> access_logs

Revision ID: 002
Revises: 001
Create Date: 2025-02-26

"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET FOREIGN_KEY_CHECKS = 0")
    op.execute("ALTER TABLE `access_log` DROP FOREIGN KEY `fk_access_log_worker`")
    op.execute("RENAME TABLE `worker` TO `workers`")
    op.execute("RENAME TABLE `access_log` TO `access_logs`")
    op.execute(
        "ALTER TABLE `access_logs` ADD CONSTRAINT `fk_access_log_worker` "
        "FOREIGN KEY (`worker_id`) REFERENCES `workers` (`worker_id`) ON DELETE RESTRICT ON UPDATE CASCADE"
    )
    op.execute("SET FOREIGN_KEY_CHECKS = 1")


def downgrade() -> None:
    op.execute("SET FOREIGN_KEY_CHECKS = 0")
    op.execute("ALTER TABLE `access_logs` DROP FOREIGN KEY `fk_access_log_worker`")
    op.execute("RENAME TABLE `access_logs` TO `access_log`")
    op.execute("RENAME TABLE `workers` TO `worker`")
    op.execute(
        "ALTER TABLE `access_log` ADD CONSTRAINT `fk_access_log_worker` "
        "FOREIGN KEY (`worker_id`) REFERENCES `worker` (`worker_id`) ON DELETE RESTRICT ON UPDATE CASCADE"
    )
    op.execute("SET FOREIGN_KEY_CHECKS = 1")
