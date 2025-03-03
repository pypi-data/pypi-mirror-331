# param_formatter.py
from typing import Optional

class ParamFormatter:
    @staticmethod
    def format_params(items: list) -> str:
        """Formats a list into a semicolon-separated string."""
        return ";".join(str(item) for item in items)

    @staticmethod
    def format_disaggregate_elems(disaggregate: Optional[str]) -> Optional[str]:
        """Formats disaggregate elements if provided."""
        return ParamFormatter.format_params([elem.split(":")[0] for elem in disaggregate]) if disaggregate else None
