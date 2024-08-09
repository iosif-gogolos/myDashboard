import unittest
from modul import Modul

class ModulTests(unittest.TestCase):
    def setUp(self):
        self.modul = Modul()

    def test_initial_values(self):
        self.assertIsNone(self.modul.id)
        self.assertIsNone(self.modul.name)
        self.assertIsNone(self.modul.kurse)
        self.assertIsNone(self.modul.istAbgeschlossen)

    def test_berechne_summe_ects(self):
        # Add test cases here to verify the behavior of berechne_summe_ects method
        pass

if __name__ == '__main__':
    unittest.main()