from enum import StrEnum
from typing import Dict

"""
Configuration:
- When running locally, mock the queue names in a .env file.

Example:
<env>
embedding-service=yourname-embedding-service
evaluation-service=yourname-evaluation-service
</env>
"""


class QUEUE_NAMES(StrEnum):
    MULTI_AGENT_SERVICE = "multi-agent-service"
    CASE_MANAGEMENT_SERVICE = "case-management-service"


QUEUE_CONFIG: Dict[str, Dict[str, bool]] = {
    QUEUE_NAMES.MULTI_AGENT_SERVICE: dict(fifo=False),
    QUEUE_NAMES.CASE_MANAGEMENT_SERVICE: dict(fifo=False),
}
