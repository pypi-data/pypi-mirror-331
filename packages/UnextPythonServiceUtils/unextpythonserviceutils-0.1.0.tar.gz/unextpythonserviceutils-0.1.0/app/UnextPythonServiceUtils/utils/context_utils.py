from typing import cast

from ..interfaces.interfaces_pd import Headers_PM
from ..context.vars import headers_context


class ContextUtils:
    @staticmethod
    def get_headers_details() -> Headers_PM:
        return cast(Headers_PM, headers_context.get())
