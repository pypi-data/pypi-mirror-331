import pandas as pd
from cooptools import typeProviders as tp
from cooptools import pandasHelpers as ph
import datetime
from cooptools.coopEnum import CoopEnum, auto
import cooptools.date_utils as du
import numpy as np

class PivotProfileType(CoopEnum):
    DATESTAMP_ACCOUNT__CATEGORY = auto()
    ACCOUNT_CATEGORY__DATESTAMP = auto()
    DATESTAMP__CATEGORY = auto()
    CATEGORY__DATESTAMP = auto()
    DATESTAMP__ACCOUNT = auto()
    DATESTAMP = auto()
    ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP = auto()
    DATESTAMP__SUBACCOUNT = auto()
    SUBACCOUNT_CATEGORY__DATESTAMP = auto()
    DATESTAMP_SUBACCOUNT__CATEGORY = auto()

DATE_STAMP_COL = 'date_stamp'
CATEGORY_COL = 'category'
ACCOUNT_COL = 'account'
AMOUNT_COL = 'amount'
SUBACCOUNT_COL = 'subaccount'

def _groupers(grouped_history_type: PivotProfileType,
              date_group_frequency: str = 'ME',
              date_stamp_col_name:str = None,
              category_col_name: str = None,
              account_col_name: str = None,
              subaccount_col_name: str = None):
    if date_stamp_col_name is None:
        date_stamp_col_name = DATE_STAMP_COL
    if category_col_name is None:
        category_col_name = CATEGORY_COL
    if account_col_name is None:
        account_col_name = ACCOUNT_COL
    if subaccount_col_name is None:
        subaccount_col_name = SUBACCOUNT_COL
    grouper_lst = []

    if grouped_history_type in [PivotProfileType.DATESTAMP_ACCOUNT__CATEGORY,
                                PivotProfileType.DATESTAMP__CATEGORY,
                                PivotProfileType.DATESTAMP__ACCOUNT,
                                PivotProfileType.ACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.CATEGORY__DATESTAMP,
                                PivotProfileType.DATESTAMP,
                                PivotProfileType.ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.DATESTAMP__SUBACCOUNT,
                                PivotProfileType.DATESTAMP_SUBACCOUNT__CATEGORY,
                                PivotProfileType.SUBACCOUNT_CATEGORY__DATESTAMP]:
        grouper_lst.append(pd.Grouper(key=date_stamp_col_name, freq=date_group_frequency))

    if grouped_history_type in [PivotProfileType.DATESTAMP_ACCOUNT__CATEGORY,
                                PivotProfileType.DATESTAMP__CATEGORY,
                                PivotProfileType.ACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.CATEGORY__DATESTAMP,
                                PivotProfileType.ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.DATESTAMP_SUBACCOUNT__CATEGORY,
                                PivotProfileType.SUBACCOUNT_CATEGORY__DATESTAMP
                                ]:
        grouper_lst.append(category_col_name)

    if grouped_history_type in [PivotProfileType.DATESTAMP_ACCOUNT__CATEGORY,
                                PivotProfileType.ACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.DATESTAMP__ACCOUNT,
                                PivotProfileType.ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP]:
        grouper_lst.append(account_col_name)

    if grouped_history_type in [PivotProfileType.ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.DATESTAMP__SUBACCOUNT,
                                PivotProfileType.DATESTAMP_SUBACCOUNT__CATEGORY,
                                PivotProfileType.SUBACCOUNT_CATEGORY__DATESTAMP
                                ]:
        grouper_lst.append(subaccount_col_name)

    if len(grouper_lst) == 0:
        raise ValueError(f"Groupers have not been correctly evaluated")

    return grouper_lst


def _pivot_indexes(grouped_history_type: PivotProfileType,
                   date_stamp_col_name: str = None,
                   category_col_name: str = None,
                   account_col_name: str = None,
                   subaccount_col_name: str = None):
    if date_stamp_col_name is None:
        date_stamp_col_name = DATE_STAMP_COL
    if category_col_name is None:
        category_col_name = CATEGORY_COL
    if account_col_name is None:
        account_col_name = ACCOUNT_COL
    if subaccount_col_name is None:
        subaccount_col_name = SUBACCOUNT_COL
    pivot_index = []

    if grouped_history_type in [PivotProfileType.DATESTAMP_ACCOUNT__CATEGORY,
                                PivotProfileType.DATESTAMP__CATEGORY,
                                PivotProfileType.DATESTAMP__ACCOUNT,
                                PivotProfileType.DATESTAMP,
                                PivotProfileType.DATESTAMP__SUBACCOUNT,
                                PivotProfileType.DATESTAMP_SUBACCOUNT__CATEGORY
                                ]:
        pivot_index.append(date_stamp_col_name)

    if grouped_history_type in [PivotProfileType.DATESTAMP_ACCOUNT__CATEGORY,
                                PivotProfileType.ACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP]:
        pivot_index.append(account_col_name)

    if grouped_history_type in [PivotProfileType.ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.SUBACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.DATESTAMP_SUBACCOUNT__CATEGORY
                                ]:
        pivot_index.append(subaccount_col_name)

    if grouped_history_type in [PivotProfileType.ACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.CATEGORY__DATESTAMP,
                                PivotProfileType.ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.SUBACCOUNT_CATEGORY__DATESTAMP,
                                ]:
        pivot_index.append(category_col_name)

    return pivot_index


def _pivot_columns(grouped_history_type: PivotProfileType,
                   date_stamp_col_name: str = None,
                   category_col_name: str = None,
                   account_col_name: str = None,
                   subaccount_col_name: str = None
                   ):
    if date_stamp_col_name is None:
        date_stamp_col_name = DATE_STAMP_COL
    if category_col_name is None:
        category_col_name = CATEGORY_COL
    if account_col_name is None:
        account_col_name = ACCOUNT_COL
    if subaccount_col_name is None:
        subaccount_col_name = SUBACCOUNT_COL

    pivot_columns = []

    if grouped_history_type in [PivotProfileType.DATESTAMP_ACCOUNT__CATEGORY,
                                PivotProfileType.DATESTAMP__CATEGORY,
                                PivotProfileType.DATESTAMP_SUBACCOUNT__CATEGORY
                                ]:
        pivot_columns.append(category_col_name)

    if grouped_history_type in [PivotProfileType.ACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.CATEGORY__DATESTAMP,
                                PivotProfileType.ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP,
                                PivotProfileType.SUBACCOUNT_CATEGORY__DATESTAMP,
                                ]:
        pivot_columns.append(date_stamp_col_name)

    if grouped_history_type in [PivotProfileType.DATESTAMP__ACCOUNT,
                                ]:
        pivot_columns.append(account_col_name)

    if grouped_history_type in [
        PivotProfileType.DATESTAMP__SUBACCOUNT,
    ]:
        pivot_columns.append(subaccount_col_name)

    return pivot_columns


def amount_pivot(
    history_df_provider: tp.DataFrameProvider,
    start_date: datetime.date = None,
    end_date: datetime.date = None,
    grouped_history_type: PivotProfileType = None,
    date_stamp_col_name: str = DATE_STAMP_COL,
    category_col_name: str = CATEGORY_COL,
    account_col_name: str = ACCOUNT_COL,
    subaccount_col_name: str = SUBACCOUNT_COL,
    amount_col_name: str = AMOUNT_COL,
    invert_amounts: bool = False
):
    df = tp.resolve(history_df_provider)
    df = ph.clean_a_dataframe(
        df=df,
        column_type_definition={
            date_stamp_col_name: datetime.date,
            category_col_name: str,
            account_col_name: str,
            subaccount_col_name: str,
            amount_col_name: float
        }
    )

    if invert_amounts:
        df[amount_col_name] = -df[amount_col_name]

    grouper_lst = _groupers(grouped_history_type,
                            account_col_name=account_col_name,
                            category_col_name=category_col_name,
                            date_stamp_col_name=date_stamp_col_name,
                            subaccount_col_name=subaccount_col_name)
    pivot_index = _pivot_indexes(grouped_history_type,
                            account_col_name=account_col_name,
                            category_col_name=category_col_name,
                            date_stamp_col_name=date_stamp_col_name,
                            subaccount_col_name=subaccount_col_name)
    pivot_columns = _pivot_columns(grouped_history_type,
                            account_col_name=account_col_name,
                            category_col_name=category_col_name,
                            date_stamp_col_name=date_stamp_col_name,
                            subaccount_col_name=subaccount_col_name)

    agg_val = amount_col_name
    pivot_index_amounts = df[pivot_index + pivot_columns + [agg_val]]
    agg_amounts = pivot_index_amounts.groupby(grouper_lst).sum()

    # Pivot
    if not agg_amounts.empty:
        piv = pd.pivot_table(agg_amounts,
                                      values=[agg_val],
                                      index=pivot_index,
                                      columns=pivot_columns,
                                      aggfunc='sum').fillna(0)
    else:
        piv = pd.DataFrame()

    # piv = piv.sort_values(by= axis=1, ascending=True)

    # pad missing months
    if end_date is None:
        end_date = du.date_tryParse(pivot_index_amounts[date_stamp_col_name].max())

    if start_date is None:
        start_date = du.date_tryParse(pivot_index_amounts[date_stamp_col_name].min())

    for mo in du.month_range(start_date, end_date):
        col = (agg_val, mo.strftime("%Y-%m-%d"))
        if col not in piv.columns:
            piv[col] = np.nan

    # Re-order the columns based on their sum
    # piv = piv.reindex(piv.sum().sort_values(ascending=False).index, axis=1)
    # piv['row_sum'] = piv.sum(axis=1)
    # Sort by the row sums
    # piv = piv.sort_values(by='amount', ascending=False)
    # piv.drop('row_sum', axis=1, inplace=True)

    # Re-order the rows based on their sum

    return piv

if __name__ == "__main__":

    def dummy_data():
        return pd.DataFrame(
            {'account': [
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A1',
                    'A2',
                    'A2',
                    'A2',
                    'A2',
                    'A2',
                    'A2',
                    'A2',
                    'A2',
                    'A2',
                    'A2',
                    'A2',
                    'A2'],
                'from_subaccount_name': [
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    '-',
                    'Chatham',
                    'Chatham',
                    '-',
                    'Chatham',
                    'Chatham',
                    '-',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    'Chatham',
                    '-',
                    'Chatham',
                    '-',
                    'Chatham'],
                'spend_category_at_time_of_record':
                [
                    'RENT_MORTGAGE',
                    'RENT_MORTGAGE',
                    'PROPERTY_MANAGEMENT',
                    'RENT_MORTGAGE',
                    'PROPERTY_MANAGEMENT',
                    'RENT_MORTGAGE',
                    'PROPERTY_MANAGEMENT',
                    'RENT_MORTGAGE',
                    'PROPERTY_MANAGEMENT',
                    'RENT_MORTGAGE',
                    'PROPERTY_MANAGEMENT',
                    'ADMINISTRATION',
                    'MAINTENANCE',
                    'RENT_MORTGAGE',
                    'ADMINISTRATION',
                    'MAINTENANCE',
                    'PROPERTY_MANAGEMENT',
                    'ADMINISTRATION',
                    'RENT_MORTGAGE',
                    'PROPERTY_MANAGEMENT',
                    'RENT_MORTGAGE',
                    'PROPERTY_MANAGEMENT',
                    'ADMINISTRATION',
                    'UTILITIES',
                    'ADMINISTRATION',
                    'RENT_MORTGAGE',
                ],
            'ledger_date_stamp':
            [
                '10/3/2024',
                '9/3/2024',
                '8/30/2024',
                '8/5/2024',
                '7/31/2024',
                '7/3/2024',
                '6/25/2024',
                '6/3/2024',
                '5/31/2024',
                '5/3/2024',
                '4/30/2024',
                '4/12/2024',
                '4/3/2024',
                '4/3/2024',
                '3/29/2024',
                '3/26/2024',
                '3/24/2024',
                '3/8/2024',
                '3/4/2024',
                '2/29/2024',
                '2/5/2024',
                '1/31/2024',
                '1/11/2024',
                '1/8/2024',
                '1/5/2024',
                '1/3/2024',
            ],
            'amount':
            [
                '963.87',
                '963.87',
                '119.5',
                '963.87',
                '119.5',
                '963.87',
                '119.5',
                '963.87',
                '119.5',
                '963.87',
                '119.5',
                '131.88',
                '1112',
                '963.87',
                '150',
                '664',
                '119.5',
                '18.48',
                '963.87',
                '119.5',
                '970.46',
                '119.5',
                '94.57',
                '79.98',
                '26.52',
                '942.27']
            }
        )

    def t_pivot_01():
        df = amount_pivot(
            history_df_provider=dummy_data(),
            grouped_history_type=PivotProfileType.ACCOUNT_SUBACCOUNT_CATEGORY__DATESTAMP,
            account_col_name='account',
            subaccount_col_name='from_subaccount_name',
            category_col_name='spend_category_at_time_of_record',
            date_stamp_col_name='ledger_date_stamp'

        )
        ph.pretty_print_dataframe(
            ph.summary_rows_cols(df,
                                 row_sum=True,
                                 row_avg=True,
                                 row_median=True,
                                 column_sum=True,
                                 column_avg=True,
                                 na_fill='-',
                                 replace_zero_val='-'),
            float_format='%.2f')


    t_pivot_01()