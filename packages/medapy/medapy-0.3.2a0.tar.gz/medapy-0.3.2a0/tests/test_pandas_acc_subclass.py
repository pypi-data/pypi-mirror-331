import pandas as pd

# Define the general accessor with common numerical methods
@pd.api.extensions.register_dataframe_accessor("num")
class GeneralNumericalAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def compute_mean(self, column):
        return self._obj[column].mean()

# Define the specific accessor for the field "specific_field"
@pd.api.extensions.register_dataframe_accessor("spec")
class SpecificFieldAccessor(GeneralNumericalAccessor):
    def __init__(self, pandas_obj):
        super().__init__(pandas_obj)
        if 'specific_field' not in self._obj:
            raise AttributeError("DataFrame must have a 'specific_field' column.")

    def compute_specific_mean(self):
        return self.compute_mean('specific_field')

# Testing the accessors
if __name__ == '__main__':
    # Create a simple DataFrame that includes the "specific_field" column.
    data = {
        'specific_field': [1, 2, 3, 4, 5],
        'other_field': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)

    # Use the general accessor to compute the mean of 'other_field'
    print("Mean of other_field:", df.num.compute_mean('other_field'))

    # Use the specific accessor to compute the mean of 'specific_field'
    print("Mean of specific_field:", df.spec.compute_specific_mean())
