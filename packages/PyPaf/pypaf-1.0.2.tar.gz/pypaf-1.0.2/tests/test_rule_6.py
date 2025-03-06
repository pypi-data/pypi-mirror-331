"""Test Address Rule 6 formatting"""

import unittest
import paf


class TestRule6WithSubBuildingName(unittest.TestCase):
    """Test Address Rule 6 with Sub-Building Name Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'sub_building_name': "10B",
            'building_name': "BARRY JACKSON TOWER",
            'thoroughfare_name': "ESTONE",
            'thoroughfare_descriptor': "WALK",
            'post_town': "BIRMINGHAM",
            'postcode': "B6 5BA"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = [
            "10B BARRY JACKSON TOWER",
            "ESTONE WALK",
            "BIRMINGHAM",
            "B6 5BA"
            ]
        self.assertEqual(
            self.address.as_list(), address, "Incorrect Rule 6 with sub-building list format"
            )

    def test_string(self):
        """Test conversion to a string"""
        address = "10B BARRY JACKSON TOWER, ESTONE WALK, BIRMINGHAM. B6 5BA"
        self.assertEqual(
            self.address.as_str(), address, "Incorrect Rule 6 with sub-building string format"
            )

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = (
            "10B BARRY JACKSON TOWER",
            "ESTONE WALK",
            "BIRMINGHAM",
            "B6 5BA"
            )
        self.assertEqual(
            self.address.as_tuple(), address, "Incorrect Rule 6 with sub-building tuple format"
            )

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "10B BARRY JACKSON TOWER",
            'line_2': "ESTONE WALK",
            'post_town': "BIRMINGHAM",
            'postcode': "B6 5BA"
            }
        self.assertEqual(
            self.address.as_dict(), address, "Incorrect Rule 6 with sub-building dict format"
            )

    def test_premises(self):
        """Test premises"""
        premises = {
            'premises_name': 'BARRY JACKSON TOWER',
            'sub_premises_number': 10,
            'sub_premises_suffix': 'B'
            }
        self.assertEqual(
            self.address.premises(), premises, "Incorrect Rule 6 w/ sub-building premises"
            )


class TestRule6WithBuildingName(unittest.TestCase):
    """Test Address Rule 6 with Building Name Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'sub_building_name': "CARETAKERS FLAT",
            'building_name': "110-114",
            'thoroughfare_name': "HIGH",
            'thoroughfare_descriptor': "STREET WEST",
            'post_town': "BRISTOL",
            'postcode': "BS1 2AW"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = [
            "CARETAKERS FLAT",
            "110-114 HIGH STREET WEST",
            "BRISTOL",
            "BS1 2AW"
            ]
        self.assertEqual(
            self.address.as_list(), address, "Incorrect Rule 6 w/ building list format"
            )

    def test_string(self):
        """Test conversion to a string"""
        address = "CARETAKERS FLAT, 110-114 HIGH STREET WEST, BRISTOL. BS1 2AW"
        self.assertEqual(
            self.address.as_str(), address, "Incorrect Rule 6 w/ building string format"
            )

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = (
            "CARETAKERS FLAT",
            "110-114 HIGH STREET WEST",
            "BRISTOL",
            "BS1 2AW"
            )
        self.assertEqual(
            self.address.as_tuple(), address, "Incorrect Rule 6 w/ building tuple format"
            )

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "CARETAKERS FLAT",
            'line_2': "110-114 HIGH STREET WEST",
            'post_town': "BRISTOL",
            'postcode': "BS1 2AW"
            }
        self.assertEqual(
            self.address.as_dict(), address, "Incorrect Rule 6 w/ building dict format"
            )

    def test_premises(self):
        """Test premises"""
        premises = {
            'premises_number': 110,
            'premises_suffix': '-114',
            'sub_premises_name': 'CARETAKERS FLAT'
            }
        self.assertEqual(
            self.address.premises(), premises, "Incorrect Rule 6 w/ building premises")


class TestRule6WithSplitException(unittest.TestCase):
    """Test Address Rule 6 with Split Building Name Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'sub_building_name': "STUDIO 18",
            'building_name': "JUSTICE MILL STUDIOS 21-23",
            'thoroughfare_name': "JUSTICE MILL",
            'thoroughfare_descriptor': "LANE",
            'post_town': "ABERDEEN",
            'postcode': "AB11 6AG"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = [
            "STUDIO 18",
            "JUSTICE MILL STUDIOS",
            "21-23 JUSTICE MILL LANE",
            "ABERDEEN",
            "AB11 6AG"
            ]
        self.assertEqual(
            self.address.as_list(), address, "Incorrect Rule 6 w/ split building list format"
            )

    def test_string(self):
        """Test conversion to a string"""
        address = "STUDIO 18, JUSTICE MILL STUDIOS, 21-23 JUSTICE MILL LANE, ABERDEEN. AB11 6AG"
        self.assertEqual(
            self.address.as_str(), address, "Incorrect Rule 6 w/ split building string format"
            )

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = (
            "STUDIO 18",
            "JUSTICE MILL STUDIOS",
            "21-23 JUSTICE MILL LANE",
            "ABERDEEN",
            "AB11 6AG"
            )
        self.assertEqual(
            self.address.as_tuple(), address, "Incorrect Rule 6 w/ split building tuple format"
            )

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "STUDIO 18",
            'line_2': "JUSTICE MILL STUDIOS",
            'line_3': "21-23 JUSTICE MILL LANE",
            'post_town': "ABERDEEN",
            'postcode': "AB11 6AG"
            }
        self.assertEqual(
            self.address.as_dict(), address, "Incorrect Rule 6 w/ split building dict format"
            )

    def test_premises(self):
        """Test premises"""
        premises = {
            'premises_number': 21,
            'premises_suffix': '-23',
            'premises_name': 'JUSTICE MILL STUDIOS',
            'sub_premises_name': 'STUDIO 18'
            }
        self.assertEqual(
            self.address.premises(), premises, "Incorrect Rule 6 w/ split building premises")


class TestRule6WithDoubleException(unittest.TestCase):
    """Test Address Rule 6 with Double Building Name Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'sub_building_name': "91",
            'building_name': "OCEAN APARTMENTS 52-54",
            'thoroughfare_name': "PARK",
            'thoroughfare_descriptor': "ROAD",
            'post_town': "ABERDEEN",
            'postcode': "AB24 5RZ"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = [
            "91 OCEAN APARTMENTS",
            "52-54 PARK ROAD",
            "ABERDEEN",
            "AB24 5RZ"
            ]
        self.assertEqual(
            self.address.as_list(), address, "Incorrect Rule 6 w/ double building list format"
            )

    def test_string(self):
        """Test conversion to a string"""
        address = "91 OCEAN APARTMENTS, 52-54 PARK ROAD, ABERDEEN. AB24 5RZ"
        self.assertEqual(
            self.address.as_str(), address, "Incorrect Rule 6 w/ double building string format"
            )

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = (
            "91 OCEAN APARTMENTS",
            "52-54 PARK ROAD",
            "ABERDEEN",
            "AB24 5RZ"
            )
        self.assertEqual(
            self.address.as_tuple(), address, "Incorrect Rule 6 w/ double building tuple format"
            )

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "91 OCEAN APARTMENTS",
            'line_2': "52-54 PARK ROAD",
            'post_town': "ABERDEEN",
            'postcode': "AB24 5RZ"
            }
        self.assertEqual(
            self.address.as_dict(), address, "Incorrect Rule 6 w/ double building dict format"
            )

    def test_premises(self):
        """Test premises"""
        premises = {
            'premises_number': 52,
            'premises_suffix': '-54',
            'premises_name': 'OCEAN APARTMENTS',
            'sub_premises_number': 91
            }
        self.assertEqual(
            self.address.premises(), premises, "Incorrect Rule 6 w/ split building premises")


class TestRule6(unittest.TestCase):
    """Test Address Rule 6 without Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'sub_building_name': "STABLES FLAT",
            'building_name': "THE MANOR",
            'thoroughfare_name': "UPPER",
            'thoroughfare_descriptor': "HILL",
            'post_town': "HORLEY",
            'postcode': "RH6 0HP"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = [
            "STABLES FLAT",
            "THE MANOR",
            "UPPER HILL",
            "HORLEY",
            "RH6 0HP"
            ]
        self.assertEqual(self.address.as_list(), address, "Incorrect Rule 6 list format")

    def test_string(self):
        """Test conversion to a string"""
        address = "STABLES FLAT, THE MANOR, UPPER HILL, HORLEY. RH6 0HP"
        self.assertEqual(self.address.as_str(), address, "Incorrect Rule 6 string format")

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = (
            "STABLES FLAT",
            "THE MANOR",
            "UPPER HILL",
            "HORLEY",
            "RH6 0HP"
            )
        self.assertEqual(self.address.as_tuple(), address, "Incorrect Rule 6 tuple format")

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "STABLES FLAT",
            'line_2': "THE MANOR",
            'line_3': "UPPER HILL",
            'post_town': "HORLEY",
            'postcode': "RH6 0HP"
            }
        self.assertEqual(self.address.as_dict(), address, "Incorrect Rule 6 dict format")

    def test_premises(self):
        """Test premises"""
        premises = {
            'premises_name': 'THE MANOR',
            'sub_premises_name': 'STABLES FLAT'
            }
        self.assertEqual(self.address.premises(), premises, "Incorrect Rule 6 premises")


if __name__ == '__main__':
    unittest.main()
