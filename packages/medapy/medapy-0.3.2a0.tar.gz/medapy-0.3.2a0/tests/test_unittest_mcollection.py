class TestParameterDefinitions(unittest.TestCase):
    def setUp(self):
        # Create a temporary JSON file with test definitions
        self.test_definitions = {
            "test_field": {
                "long_names": ["field", "Field"],
                "short_names": ["B"],
                "units": ["T"],
                "special_values": {
                    "LOW": -1,
                    "HIGH": 1
                }
            }
        }

        # Create temporary file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_definitions.json"
        with open(self.config_path, 'w') as f:
            json.dump(self.test_definitions, f)

        self.param_defs = ParameterDefinitions(self.config_path)

    def test_parameter_creation(self):
        param = self.param_defs.create_parameter("test_field")
        self.assertEqual(param.long_names, {"field", "Field"})
        self.assertEqual(param.short_names, {"B"})
        self.assertEqual(param.units, {"T"})
        self.assertEqual(param.special_values, {"LOW": -1, "HIGH": 1})

    def test_pattern_matching(self):
        param = self.param_defs.create_parameter("test_field")

        # Test fixed value pattern
        self.assertIsNotNone(param.patterns.match('fixed', "B=1.5T"))
        self.assertIsNotNone(param.patterns.match('fixed', "B1.5T"))

        # Test sweep pattern
        self.assertIsNotNone(param.patterns.match('sweep', "sweepfield"))
        self.assertIsNotNone(param.patterns.match('sweep', "fieldsweep"))

        # Test range pattern
        self.assertIsNotNone(param.patterns.match('range', "B-1.5to1.5T"))

    def test_value_parsing(self):
        param = self.param_defs.create_parameter("test_field")

        # Test fixed value parsing
        param.parse_fixed("B=1.5T")
        self.assertEqual(param.value, Decimal('1.5'))
        self.assertFalse(param.is_swept)

        # Test special value parsing
        param.parse_fixed("B=LOWT")
        self.assertEqual(param.value, Decimal('-1'))

        # Test range parsing
        param.parse_range("B-1.5to2.5T")
        self.assertTrue(param.is_swept)
        self.assertEqual(param.min_val, Decimal('-1.5'))
        self.assertEqual(param.max_val, Decimal('2.5'))
        self.assertEqual(param.sweep_direction, SweepDirection.UP)

    def tearDown(self):
        # Clean up temporary files
        self.config_path.unlink()
        self.config_path.parent.rmdir()

if __name__ == '__main__':
    unittest.main()