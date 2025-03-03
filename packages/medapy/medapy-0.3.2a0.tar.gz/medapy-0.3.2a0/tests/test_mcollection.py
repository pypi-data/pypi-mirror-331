from pathlib import Path

from medapy.collection import (MeasurementCollection, ParameterDefinition,
                               MeasurementFile, ContactPair, DefinitionsLoader)

field_param = ParameterDefinition(name_id = 'field',
    long_names=frozenset(['field', 'Field']),
    short_names=frozenset(['B', 'H']),
#    units=['T', 'Oe', 'G', 'mT']
)
temp_param = ParameterDefinition(
    name_id = 'temperature',
    long_names=['temperature', 'Temperature'],
    short_names=['T'],
#    units=['K', 'mK']
)

testfile = MeasurementFile(
    "sample_V1-5(1e-3A)_V3-7_V2-8_V4_V6_I11_sweepField_B-14to14T_T=3.0K_date.csv",
    parameters=[field_param, temp_param]
)
print(list(map(str, testfile.parameters.values())))

def print_files(fs):
    for (i, f) in enumerate(fs):
        print(f'{i:2}: {f.path.name}')
    print()

# Initialize collection
script_dir = Path(__file__).parent.absolute()
path = script_dir / 'test_files'
parameters = DefinitionsLoader().get_all()
# print(parameters)
collection = MeasurementCollection(path, parameters)

# print('Full collection:')
# print_files(collection)
# file0 = list(collection)[0]
# print(list(map(str, file0.parameters.values())))
pair = ContactPair(1, 5, 'I', 1e-6)
print(pair)
# pair = ContactPair()
# pair.parse_contacts('I1-5(1uA)')
files_1uA = collection.filter(
    contacts=[pair, (3,7)],
    temperature=(2, 10),
    # position=45.0
)
print('Filtered:')
print_files(files_1uA)


# # Filter with sweep direction
# files_down = collection.filter(sweep_direction='down')
# print('files_down:')
# print_files(files_down)

# files_up = collection.filter(sweep_direction='down')
# print('files_up:')
# print_files(files_up)

# # Filter with temperature range
# files_up_T2_7 = files_up.filter(temperature=(2.0, 7.0))
# print('files_up_T2_7:')
# print_files(files_up_T2_7)

# # Filter with sweep direction and contact pair
# pair = ContactPair()
# pair.parse_contacts('I1-4(1uA)')
# files_up_1uA = files_up.filter(
#     contacts=pair,
#     temperature=(2, 10)
# )
# print('files_up_1uA:')
# print_files(files_up_1uA)

# # Filter with multiple contact configurations
# files4 = collection.filter(
#     contacts=[(1, 2), (3, 4), 9],  # pairs and single contacts
#     polarization='I',  # current mode
#     temperature=(2.0, 4.0)
# )
# print('files4:')
# print_files(files4)

# # Filter by sweep direction
# files5 = collection.filter(
#     sweep_direction='up',
#     field=(-5, 5)
# )
# print('files5:')
# print_files(files5)

# valid replacers for pattern:
#   {NAME} - union of long and short names
#   {SNAME} - short names
#   {LNAME} - long names
#   {VALUE} - number (integer, with decimal part, in scientific notation)
#   {UNIT} - units

# example:
#   long_names: [name1, name2]
#   short_names: [n1, n2]
#   units: [unit1, unit2]
#   special_values:
#     value_name1: value1
#     value_name2: value
#   patterns:
#     fixed: "{SNAME}--{VALUE}{UNIT}" 
#     sweep: "{NAME}sweep|sweep{LNAME}"

# class TestParameterDefinitions(unittest.TestCase):
#     def setUp(self):
#         # Create a temporary JSON file with test definitions
#         self.test_definitions = {
#             "test_field": {
#                 "long_names": ["field", "Field"],
#                 "short_names": ["B"],
#                 "units": ["T"],
#                 "special_values": {
#                     "LOW": -1,
#                     "HIGH": 1
#                 }
#             }
#         }

#         # Create temporary file
#         self.temp_dir = tempfile.mkdtemp()
#         self.config_path = Path(self.temp_dir) / "test_definitions.json"
#         with open(self.config_path, 'w') as f:
#             json.dump(self.test_definitions, f)

#         self.param_defs = ParameterDefinitions(self.config_path)

#     def test_parameter_creation(self):
#         param = self.param_defs.create_parameter("test_field")
#         self.assertEqual(param.long_names, {"field", "Field"})
#         self.assertEqual(param.short_names, {"B"})
#         self.assertEqual(param.units, {"T"})
#         self.assertEqual(param.special_values, {"LOW": -1, "HIGH": 1})

#     def test_pattern_matching(self):
#         param = self.param_defs.create_parameter("test_field")

#         # Test fixed value pattern
#         self.assertIsNotNone(param.patterns.match('fixed', "B=1.5T"))
#         self.assertIsNotNone(param.patterns.match('fixed', "B1.5T"))

#         # Test sweep pattern
#         self.assertIsNotNone(param.patterns.match('sweep', "sweepfield"))
#         self.assertIsNotNone(param.patterns.match('sweep', "fieldsweep"))

#         # Test range pattern
#         self.assertIsNotNone(param.patterns.match('range', "B-1.5to1.5T"))

#     def test_value_parsing(self):
#         param = self.param_defs.create_parameter("test_field")

#         # Test fixed value parsing
#         param.parse_fixed("B=1.5T")
#         self.assertEqual(param.value, Decimal('1.5'))
#         self.assertFalse(param.is_swept)

#         # Test special value parsing
#         param.parse_fixed("B=LOWT")
#         self.assertEqual(param.value, Decimal('-1'))

#         # Test range parsing
#         param.parse_range("B-1.5to2.5T")
#         self.assertTrue(param.is_swept)
#         self.assertEqual(param.min_val, Decimal('-1.5'))
#         self.assertEqual(param.max_val, Decimal('2.5'))
#         self.assertEqual(param.sweep_direction, SweepDirection.UP)

#     def tearDown(self):
#         # Clean up temporary files
#         self.config_path.unlink()
#         self.config_path.parent.rmdir()

# if __name__ == '__main__':
#     unittest.main()