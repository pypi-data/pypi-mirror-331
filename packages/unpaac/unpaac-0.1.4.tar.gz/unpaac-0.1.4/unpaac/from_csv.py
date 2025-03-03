def _check_uncertainty_separator_in_strings(df: pd.DataFrame) -> dict:
    """Check if any string in the DataFrame contains an uncertainty separator (e.g., '+-' or similar).

    Args:
        df (pd.DataFrame): The DataFrame to check.

    Returns:
        dict: A dictionary with column names as keys and booleans as values.
              True indicates the column contains strings with uncertainty separators, False otherwise.
    """
    result = {}

    # Iterate over each column
    for column in df.columns:
        # Check if the column contains strings
        if df[column].apply(lambda x: isinstance(x, str)).any():
            # Check if any string in the series contains an uncertainty separator
            result[column] = bool(
                df[column]
                .apply(lambda x: "+/-" in x if isinstance(x, str) else False)
                .any()
            )
        else:
            result[column] = False

    return result


def read_csv(file_path: str, **kwargs) -> pd.DataFrame:
    """Read from a csv file of a dequantified and deconvoluted DataFrame."""
    df = pd.read_csv(file_path, header=[0, 1], index_col=0)

    for col, has_uncrt_seperator in _check_uncertainty_separator_in_strings(df).items():
        if has_uncrt_seperator:
            df[col].apply(lambda x: ufloat_fromstr(x))
        # .pint.quantify(level=-1)

    # df = pd.read_csv(file_path, header=None, skiprows=2)
    # unit_df = pd.read_csv(file_path, header=0, nrows=1)
    # unit_dct = unit_df.T.dropna()[0].to_dict()
    # df = pd.read_csv(file_path, header=None, skiprows=2)
    # df.columns = unit_df.columns
    # if cfg.units.str_msre in unit_dct.keys():
    #     unit_dct.pop(cfg.units.str_msre)
    # df.attrs[cfg.attrs.str_units] = unit_dct
    # # check if 1st row contains only 1 entry and assume it is the index name if so
    # # if len(df.loc[0].dropna()) == 1:
    # #     index_name = df.loc[0].dropna().values[0]
    # #     df.drop(0, inplace=True)
    # #     df.set_index(df.columns[0], inplace=True)
    # #     df.index.name = index_name
    # df = df.set_index(df.columns[0])
    # if df.index.name == cfg.units.str_msre:
    #     df.index.name = None
    return df


################# tests


    # def test_deconvolute(self) -> None:
    #     """Test deconvolution of a pint uncertainty series."""
    #     result = self.ser.uncrts.deconvolute()
    #     self.assertTrue(isinstance(result, pd.DataFrame))
    #     self.assertTrue(len(result.columns), 2)
    #     self.assertTrue(self.ser.name in result.columns)
    #     self.assertTrue(self.s_col in result.columns)
    #     self.assertEqual(self.unit, result[self.s_col].pint.units)
    #     self.assertEqual(self.unit, result[self.s_col].pint.units)

