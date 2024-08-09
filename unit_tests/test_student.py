import unittest
from student import Student

class TestStudent(unittest.TestCase):
    def setUp(self):
        self.student = Student()

    def test_initial_attributes(self):
        self.assertIsNone(self.student.nachname)
        self.assertIsNone(self.student.vorname)
        self.assertIsNone(self.student.email)
        self.assertIsNone(self.student.geburtsdatum)
        self.assertIsNone(self.student.geschlecht)
        self.assertIsNone(self.student.matrikelnummer)
        self.assertIsNone(self.student.Attribute1)

    def test_studiengang_auswaehlen(self):
        # Add test logic here
        pass

    def test_modul_auswaehlen(self):
        # Add test logic here
        pass

    def test_notendurchschnitt_anzeigen(self):
        # Add test logic here
        pass

if __name__ == '__main__':
    unittest.main()