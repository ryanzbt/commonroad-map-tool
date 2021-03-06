# -*- coding: utf-8 -*-

"""Test case for xodr file ka_suedtangente."""

import os
import unittest
from io import StringIO
from lxml import etree

from commonroad.common.file_writer import CommonRoadFileWriter

from opendrive2lanelet.opendriveparser.parser import parse_opendrive
from opendrive2lanelet.io.opendrive_convert import convert_opendrive
from test.utils import elements_equal

__author__ = "Benjamin Orthen"
__copyright__ = "TUM Cyber-Physical Systems Group"
__credits__ = ["Priority Program SPP 1835 Cooperative Interacting Automobiles"]
__version__ = "1.1.0"
__maintainer__ = "Benjamin Orthen"
__email__ = "commonroad-i06@in.tum.de"
__status__ = "Released"


class TestOpenDriveBaseClass:
    """Test the conversion of specific xodr files by reading them in, converting them
   and then comparing the outcome."""

    __test__ = False

    xodr_file_name = None
    xml_output_name = None

    def setUp(self):
        """Load the xodr file and create the scenario.

        """
        if not self.xml_output_name:
            self.xml_output_name = self.xodr_file_name
        with open(
            os.path.dirname(os.path.realpath(__file__))
            + f"/xodr_xml_test_files/{self.xodr_file_name}.xodr",
            "r",
        ) as fh:
            opendrive = parse_opendrive(etree.parse(fh).getroot())
        self.scenario = convert_opendrive(opendrive)

    def test_opendrive_scenario(self):
        """Test if the scenario is equal to the loaded xml file.
        Disregard the different dates.

        """
        with open(
            os.path.dirname(os.path.realpath(__file__))
            + f"/xodr_xml_test_files/{self.xml_output_name}.xml",
            "r",
        ) as fh:

            parser = etree.XMLParser(remove_blank_text=True)
            tree_import = etree.parse(fh, parser=parser).getroot()
            string_io = StringIO()
            writer = CommonRoadFileWriter(
                scenario=self.scenario,
                planning_problem_set=None,
                author="",
                affiliation="",
                source="OpenDRIVE 2 Lanelet Converter",
                tags="",
            )
            writer.write_scenario_to_file_io(string_io)
            tree_generated = etree.fromstring(string_io.getvalue(), parser=parser)

            # set same date so this won't change the comparison
            tree_import.set("date", "2018-10-26")
            tree_generated.set("date", "2018-10-26")

            # compare both element trees
            trees_are_equal = elements_equal(tree_import, tree_generated)
            self.assertTrue(trees_are_equal)


class TestSuedTangente(TestOpenDriveBaseClass, unittest.TestCase):
    """Includes roads with multiple lane sections and
    lane sections with multiple width sections.
    This should be split into multiple tests in the future."""

    __test__ = True
    xodr_file_name = "KA-Suedtangente-atlatec"


class TestBasicOpenDrive(TestOpenDriveBaseClass, unittest.TestCase):
    """Basic test with a junction in the middle."""

    __test__ = True
    xodr_file_name = "opendrive-1"


class TestCulDeSac(TestOpenDriveBaseClass, unittest.TestCase):
    """Two adjacent lanes with same successor should not be mistaken
    as merging lanes!"""

    __test__ = True
    xodr_file_name = "CulDeSac"


class TestComplexCrossing(TestOpenDriveBaseClass, unittest.TestCase):
    __test__ = True
    xodr_file_name = "CrossingComplex8Course"


class TestRoundabout(TestOpenDriveBaseClass, unittest.TestCase):
    __test__ = True
    xodr_file_name = "Roundabout8Course"


class TestRightWidthCoefficients(TestOpenDriveBaseClass, unittest.TestCase):
    """Test if algorithm selects the right width index if it is ambiguous.
    This was an error of an github issue for town03.xodr.
    For multiple width coefficients, at the border between the interval of two
    both could apply and it was previously not rightly determined which to select.
    """

    __test__ = True
    xodr_file_name = "town03_right_width_coefficient"


class TestZeroWidthCoefficients(TestOpenDriveBaseClass, unittest.TestCase):
    """Test if this converter discards lanes which have zero width everywhere.
    In this case, it is the lane -1 of road 1."""

    __test__ = True
    xodr_file_name = "zero_width_lanes_map"
    xml_output_name = "CulDeSac"


if __name__ == "__main__":
    unittest.main()
