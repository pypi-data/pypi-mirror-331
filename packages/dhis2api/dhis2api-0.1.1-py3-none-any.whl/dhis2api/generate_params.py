# generate_params.py
import itertools
from .param_formatter import ParamFormatter
from .indicator_loader import IndicatorLoader
from typing import List, Optional, Union

class GenerateParams:
    """
    """
    def __init__(
        self,
        country: str,
        dates: List[str],
        level: str,
        category: List[str] = "core",
        indicators: Optional[Union[List[str], None]] = None,
        disaggregate: Optional[str] = None,
        json_filepath: str = None,
    ):
        """
        Initializes the parameters needed for API requests.

        Args:
          country (str): The country to request data for.
          dates (list): A list of dates (in YYYYMM or YYYYQQ format).
          level (str): The level to be used in the parameters.
          category (list): List of categories (defaults to ['core']).
          indicators (list | None): List of indicators, if any.
          disaggregate (str | None): The disaggregate dimension for DHIS data.
          json_filepath (str): Path to the JSON file for indicators.
        """
        self.country = country.lower()
        self.category = category
        self.dates = ParamFormatter.format_params(dates)
        self.level = level
        self.disaggregate = disaggregate
        self.disaggregate_elems = ParamFormatter.format_disaggregate_elems(self.disaggregate)

        # Use the provided list of indicators or load them from the file if not provided
        self.indicators = (
            ParamFormatter.format_params(indicators)
            if indicators
            else IndicatorLoader(self.country, self.category, json_filepath).load_indicators_from_file()
        )

        # Calculate combinations and set dimensions
        self.combinations = len(dates) * len(self.indicators.split(";"))
        self.dimensions = [self.level, self.dates, self.indicators]
        self.rows_elements = ['ou', 'pe', 'dx']

    def split_params(self, situation: str) -> itertools.product:
        """Splits parameters into combinations based on the situation."""
        ou_items = [self.level]
        pe_items = self.dates.split(";")
        dx_items = self.indicators.split(";")

        if situation == "nigeria":
            return itertools.product(ou_items, pe_items, dx_items)
        elif situation == "avoid_crash":
            pe_12_items = [
                ";".join(pe_items[i:i + 12]) for i in range(0, len(pe_items), 12)
            ]
            return itertools.product(ou_items, pe_12_items, dx_items)
        return itertools.product(ou_items, pe_items, dx_items)

    def get_params(self) -> List[dict]:
        """Generates parameters for API requests based on the current configuration."""
        situation = "nigeria" if self.country in ["nigeria", "ghana"] else "avoid_crash" if self.combinations >= 120 else None
        combo = self.split_params(situation) if situation else [self.dimensions]

        params = []
        for ou, pe, dx in combo:
            dim = [f"ou:{ou}", f"pe:{pe}", f"dx:{dx}"]
            rows = self.rows_elements[:]
            if self.disaggregate:
                dim.extend(self.disaggregate)
                rows.insert(3, self.disaggregate_elems)

            param = {
                "dimension": dim,
                'displayProperty': 'NAME',
                'ignoreLimit': 'TRUE',
                'hierarchyMeta': 'TRUE',
                'hideEmptyRows': 'TRUE',
                'showHierarchy': 'TRUE',
                'rows': ";".join(rows)
            }
            params.append(param)
        return params
