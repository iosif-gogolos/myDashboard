#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import List, Optional
from kurs import Kurs
from pruefung import Pruefung
from studiengang import Studiengang

class ProgressService:
    def ects_summe(self, sg: Studiengang) -> int:
        return sum(m.ects_summe for m in sg.module)

    def verbleibende_pruefungen(self, pruefungen: List[Pruefung]) -> int:
        return sum(1 for p in pruefungen if p.note is None)

    def modul_fortschritt(self, pruefungen: List[Pruefung], kurs_ids: List[str]) -> float:
        """Bestandene Kurse / alle Kurse für ein Modul (Note <= 4.0 gilt als bestanden)."""
        if not kurs_ids:
            return 0.0
        bestandene = 0
        idx = {p.kurs_id: p for p in pruefungen}
        for kid in kurs_ids:
            p = idx.get(kid)
            if p is not None and p.note is not None and p.note <= 4.0:
                bestandene += 1
        return bestandene / len(kurs_ids)

class GradeService:
    def durchschnitt_gewichtet(self, pruefungen: List[Pruefung], kurse: List[Kurs]) -> Optional[float]:
        ects = {k.id: k.ects for k in kurse}
        w_sum = 0.0
        p_sum = 0.0
        for p in pruefungen:
            if p.note is None or p.note > 4.0:
                continue
            w = ects.get(p.kurs_id, 0)
            w_sum += p.note * w
            p_sum += w
        return (w_sum / p_sum) if p_sum else None
