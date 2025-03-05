import unittest

from juham_homewizard.homewizardwatermeter import HomeWizardWaterMeter


class TestVisualCrossing(unittest.TestCase):
    """Unit tests for `HomeWizardWaterMeter`."""

    def test_get_classid(self):
        """Assert that the meta-class driven class initialization works."""
        classid = HomeWizardWaterMeter.get_class_id()
        self.assertEqual("HomeWizardWaterMeter", classid)


if __name__ == "__main__":
    unittest.main()
