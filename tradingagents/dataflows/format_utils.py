import pandas as pd

def set_pandas_format():
    # Show all rows and columns
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    # sometimes it doesn't work.
    pd.option_context('display.float_format', '{:,.2f}'.format, 
                      'display.precision', 2)
    pd.set_option('display.max_seq_items', None)  # For lists/arrays

def format_large_numbers(x):
    if pd.isna(x):
        return x
    if abs(x) >= 1e9:
        return f'{x/1e9:.1f}B'
    elif abs(x) >= 1e6:
        return f'{x/1e6:.1f}M'
    elif abs(x) >= 1e3:
        return f'{x/1e3:.1f}K'
    elif abs(x)<1:
        return f'{x*100:.2f}%'
    else:
        return f'{x:.2f}'

def show_formatted(dataframe):
    set_pandas_format()
    df_display = dataframe.copy()
    string_names = []
    numeric_names = []
    for col in df_display.columns:
        if col not in ['symbol','ticker','industry', 'shortName', 'date']:
            df_display[col] = pd.to_numeric(df_display[col], errors='coerce')
            df_display[col] = df_display[col].apply(format_large_numbers)
            numeric_names.append(col)
        else:
            string_names.append(col)
    return df_display[string_names+numeric_names]
