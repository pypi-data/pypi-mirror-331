import pandas as pd
from .param_formatter import ParamFormatter

class IndicatorLoader:
    """
    The IndicatorLoader is to load the 
    """
    def __init__(self,
                 country: str,
                 category: list,
                 json_filepath: str,
                 column: str = None):
        self.country = country.lower()
        self.category_str = "|".join(category)
        self.json_filepath = json_filepath
        self.column = column if column else "category_old"

    def load_indicators_from_file(self) -> str:
        """Loads indicators from an Excel file filtered by country and category."""
        ind_df = pd.read_excel(self.json_filepath)
        if "id" in ind_df.columns and self.column in ind_df.columns:
            ind_list = (ind_df[
                (ind_df.country.str.lower() == self.country) &
                (ind_df[self.column].str.contains(self.category_str))]
                ["id"].tolist())
            return ParamFormatter.format_params(ind_list)
        else:
            raise ValueError(f"Column id or {self.column} is not found in provided JSON file.")
