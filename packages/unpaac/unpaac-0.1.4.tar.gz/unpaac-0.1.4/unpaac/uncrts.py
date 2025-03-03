import numpy as np
import pandas as pd
from pint_pandas import PintArray, PintType
from pint_pandas.pint_array import is_pint_type
from uncertainties import unumpy, ufloat_fromstr
from uncertainties_pandas import UncertaintyArray, UncertaintyDtype
from typing import Any, Iterable, Optional, Union


ACCESSOR_NAME: str = "uncrts"

UNCRT_COL_PFX: str = "δ("  # prefix for uncertainty column name
UNCRT_COL_SFX: str = ")"  # suffix for uncertainty column name


def _validate_name(name: str) -> None:
    """Validate if the provided name is a non-empty string."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            f"Invalid column name: {name!r}. Name must be a non-empty string."
        )


def _validate_prefix_suffix(prefix: str, suffix: str) -> None:
    """Validate if at least one of prefix or suffix is a non-empty string."""
    if not (prefix and len(prefix) > 0) and not (suffix and len(suffix) > 0):
        raise ValueError(
            "At least one of 'prefix' or 'suffix' must be a non-empty string."
        )


def _get_uncrt_col_name(name: str, prefix: str, suffix: str) -> str:
    """Generate uncertainty column name from measure column name.

    Raises:
        ValueError: If the prefix/suffix or name is invalid.
    """
    _validate_prefix_suffix(prefix, suffix)
    _validate_name(name)

    return f"{prefix}{name}{suffix}"


def _get_msre_col_name(name: str, prefix: str, suffix: str) -> str:
    """Generate measure column name from uncertainty column name.

    Raises:
        ValueError: If the prefix/suffix or name is invalid.
    """
    _validate_prefix_suffix(prefix, suffix)
    _validate_name(name)

    start_idx = len(prefix) if prefix else None
    end_idx = -len(suffix) if suffix else None
    return name[start_idx:end_idx]


def is_pint_uncertainty_series(obj: Any) -> bool:
    """Check for pandas Series with Pint dtype and Uncertainty subdtype."""
    if not isinstance(obj, pd.Series):
        return False
    if not is_pint_type(obj):
        return False
    return isinstance(getattr(obj.dtype, "subdtype", None), UncertaintyDtype)


def create_pint_series(
    values: Iterable[Union[float, int]],
    unit: str,
    uncertainties: Optional[Iterable[Union[float, int]]] = None,
    **kwargs,
) -> pd.Series:
    """
    Create a pandas Series holding a `PintArray` with optional uncertainties.

    This function converts a sequence of numeric values into a pandas Series containing
    a `PintArray`. If uncertainties are provided, they are combined with the values
    to form an `UncertaintyArray`, which is then nested into the `PintArray`. If the
    input `values` is a pandas Series, attributes like its index and name will be
    inherited unless explicitly overridden via keyword arguments.

    Args:
        values (Iterable[float | int]): The numeric values to include in the series.
        unit (str): The physical unit for the values, compatible with Pint.
        uncertainties (Iterable[float | int], optional): The uncertainties
            corresponding to the values.
        **kwargs: Additional arguments to pass to the pandas Series constructor
            (e.g., `index` or `name`).

    Returns:
        pd.Series: A pandas Series holding a `PintArray`, optionally with uncertainties.

    Raises:
        ValueError: If `uncertainties` is provided and its length does not match
            the length of `values`.

    Example:
        >>> values = [1.0, 2.0, 3.0]
        >>> uncertainties = [0.1, 0.2, 0.3]
        >>> series = create_pint_series(values, "meter", uncertainties=uncertainties, name="length")
        >>> print(series)
        0    1.00+/-0.10
        1    2.00+/-0.20
        2    3.00+/-0.30
        Name: length, dtype: pint[meter][UncertaintyDtype]

    Notes:
        - If `uncertainties` is not provided, the resulting series will only
          contain nominal values without any uncertainty information and the
          subdtype corresponds to the one of the values. The `dtype` for the
          example above without providing `uncertainties` is `pint[meter][Int64]`.
        - When `values` is a pandas Series, its `index` and `name` attributes are
          automatically transferred unless explicitly overridden in `kwargs`.
    """
    new_values = values
    if uncertainties is not None and len(values) != len(uncertainties):
        raise ValueError(
            f"Amount of uncertainties ({len(uncertainties)}) does not match amount of values ({len(values)})."
        )
    elif uncertainties is not None:
        new_values = UncertaintyArray(
            unumpy.uarray(np.array(values), np.array(uncertainties))
        )
    # inherit certain attributes if not declared as kwargs and values is a series
    if isinstance(values, pd.Series):
        attributes_to_check = ["index", "name"]
        for attr in attributes_to_check:
            if attr not in kwargs and hasattr(values, attr):
                kwargs[attr] = getattr(values, attr)
    return pd.Series(PintArray(new_values, unit), **kwargs)


@pd.api.extensions.register_series_accessor(ACCESSOR_NAME)
class UncertaintySeriesAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if not is_pint_uncertainty_series(obj):
            raise AttributeError(
                f"Series.dtype.subdtype is not 'UncertaintyDtype' ({obj.dtype})."
            )

    @property
    def n(self) -> pd.Series:
        """Nominal value as pandas Series holding a ``PintArray`` (shortcut)."""
        return self.nominal_values

    @property
    def nominal_values(self) -> pd.Series:
        """Nominal values as pandas Series holding a ``PintArray``."""
        series = create_pint_series(
            values=[v.m.n if v.m is not pd.NA else np.nan for v in self._obj.values],
            unit=self._obj.pint.units,
            name=self._obj.name,
        )
        series.index = self._obj.index
        return series

    @property
    def s(self) -> pd.Series:
        """Standard deviation as pandas Series holding a ``PintArray`` (shortcut)."""
        return self.std_devs

    @property
    def std_devs(self) -> pd.Series:
        """Standard deviations as pandas Series holding a ``PintArray``."""
        name = (
            None
            if self._obj.name is None
            else _get_uncrt_col_name(self._obj.name, UNCRT_COL_PFX, UNCRT_COL_SFX)
        )
        series = create_pint_series(
            values=[v.m.s if v.m is not pd.NA else np.nan for v in self._obj.values],
            unit=self._obj.pint.units,
            name=name,
        )
        series.index = self._obj.index
        return series

    def to_series(self) -> tuple[pd.Series, pd.Series]:
        """Returns tuple of pint series for nominal values and standard deviationse."""
        return self._obj.uncrts.n, self._obj.uncrts.s


@pd.api.extensions.register_dataframe_accessor(ACCESSOR_NAME)
class UncertaintyDataFrameAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def add(self, column: str, uncrts: Iterable[Union[float, int]]) -> None:
        """
        Add uncertainties to a column in the DataFrame.

        This method assigns uncertainties to the specified column in the DataFrame.
        The uncertainties are assumed to have the same unit as the nominal values
        in the column unless provided as a pint series. If uncertainties are already
        assigned to the column, an `AttributeError` is raised.

        Args:
            column (str): The name of the column to which uncertainties will be added.
            uncrts (Iterable[float | int]): The uncertainties to assign to the column. These
                can be a list, NumPy array, or a PintArray. If a PintArray is provided, its
                units must be compatible with the column's nominal values.

        Returns:
            None

        Raises:
            AttributeError: If uncertainties are already assigned to the specified column.
            ValueError: If the uncertainties provided are incompatible with the column's units.

        Example:
            >>> df = pd.DataFrame({"mass": create_pint_series([1.0, 2.0, 3.0], "kg")
            >>> df.uncrts.add("mass", [0.1, 0.2, 0.3])
            >>> df["mass"]
                      mass
            0  1.00+/-0.10
            1  2.00+/-0.20
            2  3.00+/-0.30
        """
        if is_pint_uncertainty_series(self._obj[column]):
            raise AttributeError(f"Uncertainties already assigned to '{column}'")
        unit = self._obj[column].pint.units
        n = self._obj[column].pint.m
        s = uncrts.pint.to(unit).pint.m if is_pint_type(uncrts) else uncrts
        self._obj[column] = create_pint_series(n, unit=unit, uncertainties=s)

    def convolute(
        self,
        column: Optional[str] = None,
        prefix: str = UNCRT_COL_PFX,
        suffix: str = UNCRT_COL_SFX,
    ) -> pd.DataFrame:
        """
        Combine nominal value and uncertainty columns into a single column with a PintArray.

        This method replaces the specified column (or all eligible columns if none is specified)
        with a PintArray that encapsulates both nominal values and uncertainties.
        The corresponding uncertainty column, identified by the specified prefix and suffix
        pattern, is removed from the DataFrame.

        Args:
            column (str, optional): The name of the column to convolute. If None, all columns
                with matching uncertainty columns will be processed.
            prefix (str): Prefix used to identify the uncertainty column. Default is "δ(".
            suffix (str): Suffix used to identify the uncertainty column. Default is ")".

        Returns:
            pd.DataFrame: A new DataFrame with nominal value and uncertainty columns convoluted
            into single columns with an UncertaintyArray nested in a PintArray.

        Raises:
            ValueError: If the data types of the nominal values and the uncertainties do not match.

        Example:
            >>> df = pd.DataFrame({
            ...     "mass": create_pint_series([1, 2, 3], "mg"),
            ...     "mass_uncertainty": create_pint_series([0.1, 0.2, 0.3], "mg")
            ... })
            >>> df.uncrts.convolute(prefix="", suffix"_uncertainty")
                      mass
            0  1.00+/-0.10
            1  2.00+/-0.20
            2  3.00+/-0.30
        """
        df = self._obj.copy()
        columns = [column] if column is not None else df.columns.to_list()

        def conv_col(column: str, uncrt_col: str) -> None:
            if not df[column].dtype == df[uncrt_col].dtype:
                raise ValueError(
                    "Unequal datatypes for nominal values and standard deviations!"
                )
            df[column] = create_pint_series(
                values=df[column].pint.m,
                unit=df[column].pint.units,
                uncertainties=df[uncrt_col].pint.m,
            )
            df.drop(uncrt_col, axis=1, inplace=True)

        for msre_col in columns:
            uncrt_col = _get_uncrt_col_name(msre_col, prefix=prefix, suffix=suffix)
            if msre_col in df.columns and uncrt_col in df.columns:
                conv_col(msre_col, uncrt_col=uncrt_col)

        return df

    def deconvolute(
        self,
        column: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Split a column with an UncertaintyArray nested in a PintArray into separate columns for
        nominal values and uncertainties.

        This method replaces a specified column (or all eligible columns if none is specified)
        containing a PintArray with two separate columns: one for the nominal values and
        another for the uncertainties. The uncertainty column is inserted next to the original
        column.

        Args:
            column (str, optional): The name of the column to deconvolute. If None, all columns
                with a PintArray will be processed.

        Returns:
            pd.DataFrame: A new DataFrame with the specified columns deconvoluted into separate
            nominal value and uncertainty columns.

        Raises:
            ValueError: If the column specified is not a PintArray with uncertainties.

        Example:
            >>> df = pd.DataFrame({
            ...     "mass": create_pint_series(
            ...         [1.0, 2.0, 3.0], "mg", uncertainties=[0.1, 0.2, 0.3]
            ...     )
            ... })
            >>> df.uncrts.deconvolute()
               mass  δ(mass)
            0   1.0      0.1
            1   2.0      0.2
            2   3.0      0.3
        """
        df = self._obj.copy()
        columns = [column] if column is not None else df.columns.to_list()

        def deconvolute_column(column: str) -> None:
            n, s = df[column].uncrts.to_series()
            df[column] = n
            loc = df.columns.get_loc(column) + 1
            df.insert(loc, s.name, s)

        for msre_col in columns:
            uncrt_col = _get_uncrt_col_name(
                msre_col, prefix=UNCRT_COL_PFX, suffix=UNCRT_COL_SFX
            )
            if uncrt_col not in df.columns and is_pint_uncertainty_series(df[msre_col]):
                deconvolute_column(msre_col)

        return df
