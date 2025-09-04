from typing import List
from kurs import Kurs
from pruefung import Pruefung
from studiengang import Studiengang

class ProgressService:
    def ects_summe(self, sg: Studiengang) -> int:
        return sum(m.ects_summe for m in sg.module)
    
    def verbleibende_pruefungen(self, pruefungen: List[Pruefung]) -> int:
        return sum(1 for p in pruefungen if p.note is None)
    

class GradeService:
    def durchschnitt_gewichtet(self, pruefungen: List[Pruefung], kurse: List[Kurs]) -> float:
        ects = {k.id: k.ects for k in kurse}
        w_sum = 0.0; p_sum = 0.0
        for p in pruefungen:
            if p.note is None:
                continue
            w = ects.get(p.kurs_id, 0.0)
            w_sum += p.note * w; p_sum += w
        return w_sum / p_sum if p_sum else float("nan")
