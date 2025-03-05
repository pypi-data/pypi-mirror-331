"""Test Address Rule 3 formatting"""

import unittest
import paf


class TestRule3WithBuildingName(unittest.TestCase):
    """Test Address Rule 3 with Building Name Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'building_name': "1A",
            'dependent_thoroughfare_name': "SEASTONE",
            'dependent_thoroughfare_descriptor': "COURT",
            'thoroughfare_name': "STATION",
            'thoroughfare_descriptor': "ROAD",
            'post_town': "HOLT",
            'postcode': "NR25 7HG"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = ["1A SEASTONE COURT", "STATION ROAD", "HOLT", "NR25 7HG"]
        self.assertEqual(
            self.address.as_list(), address, "Incorrect Rule 3 w/ building list format"
            )

    def test_string(self):
        """Test conversion to a string"""
        address = "1A SEASTONE COURT, STATION ROAD, HOLT. NR25 7HG"
        self.assertEqual(
            self.address.as_str(), address, "Incorrect Rule 3 w/ building string format"
            )

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = ("1A SEASTONE COURT", "STATION ROAD", "HOLT", "NR25 7HG")
        self.assertEqual(
            self.address.as_tuple(), address, "Incorrect Rule 3 w/ building tuple format"
            )

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "1A SEASTONE COURT",
            'line_2': "STATION ROAD",
            'post_town': "HOLT",
            'postcode': "NR25 7HG"
            }
        self.assertEqual(
            self.address.as_dict(), address, "Incorrect Rule 3 w/ building dict format"
            )

    def test_premises(self):
        """Test premises"""
        premises = {
            'premises_name': 'SEASTONE COURT',
            'sub_premises_number': 1,
            'sub_premises_suffix': 'A'
            }
        self.assertEqual(
            self.address.premises(), premises, "Incorrect Rule 3 w/ building premises"
            )


class TestRule3WithoutBuildingName(unittest.TestCase):
    """Test Address Rule 3 without Building Name Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'building_name': "THE MANOR",
            'thoroughfare_name': "UPPER",
            'thoroughfare_descriptor': "ROAD",
            'post_town': "HORLEY",
            'postcode': "RH6 0HP"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = ["THE MANOR", "UPPER ROAD", "HORLEY", "RH6 0HP"]
        self.assertEqual(
            self.address.as_list(), address, "Incorrect Rule 3 w/o building list format"
            )

    def test_string(self):
        """Test conversion to a string"""
        address = "THE MANOR, UPPER ROAD, HORLEY. RH6 0HP"
        self.assertEqual(
            self.address.as_str(), address, "Incorrect Rule 3 w/ building string format"
            )

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = ("THE MANOR", "UPPER ROAD", "HORLEY", "RH6 0HP")
        self.assertEqual(
            self.address.as_tuple(), address, "Incorrect Rule 3 w/o building tuple format"
            )

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "THE MANOR",
            'line_2': "UPPER ROAD",
            'post_town': "HORLEY",
            'postcode': "RH6 0HP"
            }
        self.assertEqual(
            self.address.as_dict(), address, "Incorrect Rule 3 w/o building tuple format"
            )

    def test_premises(self):
        """Test premises"""
        premises = {'premises_name': 'THE MANOR'}
        self.assertEqual(
            self.address.premises(), premises, "Incorrect Rule 3 w/o building premises"
            )


class TestRule3WithSplit(unittest.TestCase):
    """Test Address Rule 3 with Split Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'organisation_name': "S D ALCOTT FLORISTS",
            'building_name': "FLOWER HOUSE 189A",
            'thoroughfare_name': "PYE GREEN",
            'thoroughfare_descriptor': "ROAD",
            'post_town': "CANNOCK",
            'postcode': "WS11 5SB"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = [
            "S D ALCOTT FLORISTS",
            "FLOWER HOUSE",
            "189A PYE GREEN ROAD",
            "CANNOCK",
            "WS11 5SB"
            ]
        self.assertEqual(
            self.address.as_list(), address, "Incorrect Rule 3 with split list format"
            )

    def test_string(self):
        """Test conversion to a string"""
        address = (
            "S D ALCOTT FLORISTS, "
            "FLOWER HOUSE, "
            "189A PYE GREEN ROAD, "
            "CANNOCK. "
            "WS11 5SB"
            )
        self.assertEqual(
            self.address.as_str(), address, "Incorrect Rule 3 with split string format"
            )

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = (
            "S D ALCOTT FLORISTS",
            "FLOWER HOUSE",
            "189A PYE GREEN ROAD",
            "CANNOCK",
            "WS11 5SB"
            )
        self.assertEqual(
            self.address.as_tuple(), address, "Incorrect Rule 3 with split tuple format"
            )

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "S D ALCOTT FLORISTS",
            'line_2': "FLOWER HOUSE",
            'line_3': "189A PYE GREEN ROAD",
            'post_town': "CANNOCK",
            'postcode': "WS11 5SB"
            }
        self.assertEqual(
            self.address.as_dict(), address, "Incorrect Rule 3 with split dict format"
            )

    def test_premises(self):
        """Test premises"""
        premises = {
            'premises_number': 189,
            'premises_suffix': 'A',
            'premises_name': 'FLOWER HOUSE'
            }
        self.assertEqual(
            self.address.premises(), premises, "Incorrect Rule 3 with split premises"
            )


class TestRule3WithoutSplit(unittest.TestCase):
    """Test Address Rule 3 without Split Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'organisation_name': "JAMES VILLA HOLIDAYS",
            'building_name': "CENTRE 30",
            'thoroughfare_name': "ST LAURENCE",
            'thoroughfare_descriptor': "AVENUE",
            'post_town': "GRAFTON",
            'postcode': "ME16 0LP"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = [
            "JAMES VILLA HOLIDAYS",
            "CENTRE 30",
            "ST LAURENCE AVENUE",
            "GRAFTON",
            "ME16 0LP"
            ]
        self.assertEqual(
            self.address.as_list(), address, "Incorrect Rule 3 w/o split list format"
            )

    def test_string(self):
        """Test conversion to a string"""
        address = (
            "JAMES VILLA HOLIDAYS, "
            "CENTRE 30, "
            "ST LAURENCE AVENUE, "
            "GRAFTON. "
            "ME16 0LP"
            )
        self.assertEqual(
            self.address.as_str(), address, "Incorrect Rule 3 w/o split string format"
            )

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = (
            "JAMES VILLA HOLIDAYS",
            "CENTRE 30",
            "ST LAURENCE AVENUE",
            "GRAFTON",
            "ME16 0LP"
            )
        self.assertEqual(
            self.address.as_tuple(), address, "Incorrect Rule 3 w/o split tuple format"
            )

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "JAMES VILLA HOLIDAYS",
            'line_2': "CENTRE 30",
            'line_3': "ST LAURENCE AVENUE",
            'post_town': "GRAFTON",
            'postcode': "ME16 0LP"
            }
        self.assertEqual(
            self.address.as_dict(), address, "Incorrect Rule 3 w/o split dict format"
            )

    def test_premises(self):
        """Test premises"""
        premises = {'premises_name': 'CENTRE 30'}
        self.assertEqual(
            self.address.premises(), premises, "Incorrect Rule 3 w/o split premises"
            )


class TestRule3WithoutCharSplit(unittest.TestCase):
    """Test Address Rule 3 without Character Split Exception"""

    @classmethod
    def setUpClass(cls):
        """Set up Address instance"""
        cls.address = paf.Address({
            'organisation_name': "JOBCENTRE PLUS",
            'building_name': "ABERDEEN B D C",
            'thoroughfare_name': "WELLINGTON",
            'thoroughfare_descriptor': "CIRCLE",
            'post_town': "ABERDEEN",
            'postcode': "AB99 8AB"
            })

    def test_list(self):
        """Test conversion to an list"""
        address = [
            "JOBCENTRE PLUS",
            "ABERDEEN B D C",
            "WELLINGTON CIRCLE",
            "ABERDEEN",
            "AB99 8AB"
            ]
        self.assertEqual(
            self.address.as_list(), address, "Incorrect Rule 3 w/o char split list format"
            )

    def test_string(self):
        """Test conversion to a string"""
        address = (
            "JOBCENTRE PLUS, "
            "ABERDEEN B D C, "
            "WELLINGTON CIRCLE, "
            "ABERDEEN. "
            "AB99 8AB"
            )
        self.assertEqual(
            self.address.as_str(), address, "Incorrect Rule 3 w/o char split string format"
            )

    def test_tuple(self):
        """Test conversion to a tuple"""
        address = (
            "JOBCENTRE PLUS",
            "ABERDEEN B D C",
            "WELLINGTON CIRCLE",
            "ABERDEEN",
            "AB99 8AB"
            )
        self.assertEqual(
            self.address.as_tuple(), address, "Incorrect Rule 3 w/o char split tuple format"
            )

    def test_dict(self):
        """Test conversion to a dict"""
        address = {
            'line_1': "JOBCENTRE PLUS",
            'line_2': "ABERDEEN B D C",
            'line_3': "WELLINGTON CIRCLE",
            'post_town': "ABERDEEN",
            'postcode': "AB99 8AB"
            }
        self.assertEqual(
            self.address.as_dict(), address, "Incorrect Rule 3 w/o char split dict format"
            )

    def test_premises(self):
        """Test premises"""
        premises = {'premises_name': 'ABERDEEN B D C'}
        self.assertEqual(
            self.address.premises(), premises, "Incorrect Rule 3 w/o char split premises"
            )


if __name__ == '__main__':
    unittest.main()
