from abc import ABC, abstractmethod
from studiengang import Studiengang
from student import Student

class StudentRepository(ABC):
    @abstractmethod
    def load(self) -> Student: ...
    @abstractmethod
    def save(self, s: Student) -> None: ...


class JsonStudentRepository(StudentRepository):
    def __init__(self, path: str = "data/student.json"):
        self.path = path

    def load(self) -> Student:
        # TODO: JSON einlesen, in Entities mappen
        raise NotImplementedError
    def save(self, s: Student) -> None:
        # TODO: Entitie serialisieren und schreiben
        raise NotImplementedError