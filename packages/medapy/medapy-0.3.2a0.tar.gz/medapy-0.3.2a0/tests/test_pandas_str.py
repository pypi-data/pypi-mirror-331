import pandas as pd
from pandas.io.formats.format import DataFrameFormatter
from pandas.io.formats.string import StringFormatter

@pd.api.extensions.register_dataframe_accessor("acc")
class CustomAccessor:
    def __init__(self, df):
        self._df = df
        self.labels = {}

    def __str__(self):
        # Get original formatted output
        formatter = DataFrameFormatter(frame=self._df)
        
        original = formatter.get_strcols()
        
        # Create labels row using same column widths
        labels = [self.labels.get(col, '') for col in self._df.columns]
        columns = [(i, col[0].strip()) for i, col in enumerate(original)]
        index_width = len(original[1][0]) + 1  # From first data row
        
        # Modify index column
        col_width = len(original[0][0]) + 1
        original[0].insert(1, f"{'L':>{col_width}}")
        
        # Modify data columns
        for i, column in columns[1:]:
            labels = tuple(lbl for lbl, col in self.labels.items() if col == column)
            col_width = len(original[i][0])
            
            label_fmt = f"{','.join(labels):>{col_width}}" 
            original[i].insert(1, label_fmt)
        
            
        repr_params = pd.io.formats.format.get_dataframe_repr_params()
        line_width = repr_params['line_width']
        
        string_formatter = StringFormatter(formatter, line_width=line_width)
        return string_formatter._join_multiline(original)
    
def format_labels(labels, width): pass
       

df = pd.DataFrame({'Temperature (°C)': [25.3, 22.1], 'Rel Humidity %': [45, 68]})
df.acc.labels = {'Temp': 'Temperature (°C)', 'Humidity': 'Rel Humidity %',
                 'T': 'Temperature (°C)'}
print(df.acc)
print(df)