import pandas as pd
import pint_pandas
from medapy import ms_pandas

# Create sample DataFrame
# df = pd.DataFrame({'Field (Oe)': [1, 2, 3],
#                     'Current (uA)': [10, 10, 10],
#                     'Voltage (mV)': [0.05, 0.1, 0.15],
#                     'Resistance (Ohm)': [5, 10, 15],
#                     'Resistivity (uohm cm)': [20, 40, 60],
#                     'Unitless col': [18, 5, 4]
#                     })

N = 3
df = pd.DataFrame({'Field (Oe)': [1, 2, 3] + list(range(N)),
                    'Current (uA)': [10, 10, 10] + list(range(N)),
                    'Voltage (mV)': [0.05, 0.1, 0.15] + list(range(N)),
                    'Resistance (Ohm)': [5, 10, 15] + list(range(N)),
                    'Resistivity (uohm cm)': [20, 40, 60] + list(range(N)),
                    'Unitless col': [18, 5, 4] + list(range(N)),
                    'Unitless col2': [18, 5, 4] + list(range(N)),
                    })

# data = {f'col #{i}': list(range(N)) for i in range(25)}
# df = pd.DataFrame(data)

# print(df)
custom_unit_dict = dict(Ohm='ohm') 
df.ms.init_msheet(translations=custom_unit_dict, patch_rename=True, strict_units=False)
print(df.ms)

# print(df.ms['Field'])
# df0 = pd.DataFrame({'Fld (Oe)': [1, 2, 3],
#                     'Crnt (uA)': [10, 10, 10],
#                     'Volt (mV)': [0.05, 0.1, 0.15],
#                     'Res (Ohm)': [5, 10, 15],
#                     'Re (uohm cm)': [20, 40, 60],
#                     'Unitless': [18, 5, 4]
#                     })


# Add some labels

# df.ms.add_labels({'Field': 'B'})
# print(df.ms.labels)
print(df.ms)

# # Check various methods to access data
# print(f'Standard df access:\n{df["Field"]}\n')
# print(f'MS access by column:\n{df.ms["Field"]}\n')
# print(f'MS access by label:\n{df.ms["H"]}\n')
# print(f'MS access of several columns:\n{df.ms[["H", "R"]]}\n')
# print(f'MS access by axis:\n{df.ms.y}\n')

# # Check axis reassignment
# # By default, x, y, z axes are assigned to the first three columns
# # {'x': 'Field', 'y': 'Current', 'z': 'Voltage'}
# print(f'Default axes: {df.ms.axes}')
# df.ms.set_as_axis('u', 'R') # add new axis
# df.ms.set_as_axis('y', 'rho') # reassign y axis to rho
# df.ms.set_as_axis('x', 'Voltage', swap=True) # assign axis and swap if both exist
# print('=========Original df:')
# print(df.ms)
# print()

# df2 = df.rename(columns={'Field': 'NewField'})
# print('=========New df after rename preserves data:')
# print(df2.ms)

# print(df.ms.wu('R'))