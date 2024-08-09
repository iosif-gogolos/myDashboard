import unittest
from pruefung import Pruefung

class TestPruefung(unittest.TestCase):
    def setUp(self):
        self.pruefung = Pruefung()

    def test_initial_attributes(self):
        self.assertIsNone(self.pruefung.id)
        self.assertIsNone(self.pruefung.beschreibung)
        self.assertIsNone(self.pruefung.kurs)
        self.assertIsNone(self.pruefung.pruefungsform)
        self.assertIsNone(self.pruefung.note)
        self.assertIsNone(self.pruefung.student)
        self.assertIsNone(self.pruefung.studiengang)

    def test_get_ects(self):
        # Add test logic here
        pass

    def test_get_student(self):
        # Add test logic here
        pass

if __name__ == '__main__':
    unittest.main()