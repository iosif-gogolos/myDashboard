#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Any, Dict, List

from abc import ABC, abstractmethod
from studiengang import Studiengang
from student import Student
from modul import Modul
from kurs import Kurs
from pruefung import Pruefung
from pruefungsform import Pruefungsform

class StudentRepository(ABC):
    @abstractmethod
    def load(self) -> Student: ...
    @abstractmethod
    def save(self, s: Student) -> None: ...

class JsonStudentRepository(StudentRepository):
    def __init__(self, path: str = "data/student.json"):
        self.path = Path(path)

    # --------- Mapping: JSON -> Domain -----------------------------------------
    def _from_json(self, data: Dict[str, Any]) -> Student:
        sg_raw = data["studiengang"]
        module: List[Modul] = []
        mod_list = sg_raw.get("module") or sg_raw.get("modules") or []
        for m in mod_list:
            kurse = [Kurs(**k) for k in m.get("kurse", [])]
            module.append(Modul(id=m["id"], name=m["name"], kurse=kurse))
        sg = Studiengang(id=sg_raw["id"], name=sg_raw["name"], module=module)

        pruefungen = []
        for p in data.get("pruefungen", []):
            pf = Pruefungsform(p.get("pruefungsform", "KLAUSUR"))
            pruefungen.append(Pruefung(id=p["id"], kurs_id=p["kurs_id"], pruefungsform=pf, note=p.get("note")))

        return Student(
            id=data["id"],
            vorname=data["vorname"],
            nachname=data["nachname"],
            matrikelnummer=data["matrikelnummer"],
            studiengang=sg,
            pruefungen=pruefungen,
        )

    # --------- Mapping: Domain -> JSON -----------------------------------------
    def _to_json(self, s: Student) -> Dict[str, Any]:
        return {
            "id": s.id,
            "vorname": s.vorname,
            "nachname": s.nachname,
            "matrikelnummer": s.matrikelnummer,
            "studiengang": {
                "id": s.studiengang.id,
                "name": s.studiengang.name,
                "module": [
                    {
                        "id": m.id,
                        "name": m.name,
                        "kurse": [ {"id": k.id, "name": k.name, "ects": k.ects} for k in m.kurse ]
                    } for m in s.studiengang.module
                ]
            },
            "pruefungen": [
                {
                    "id": p.id,
                    "kurs_id": p.kurs_id,
                    "pruefungsform": p.pruefungsform.value,
                    "note": p.note
                } for p in s.pruefungen
            ]
        }

    def load(self) -> Student:
        if not self.path.exists():
            raise FileNotFoundError(f"Datendatei nicht gefunden: {self.path}")
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return self._from_json(data)

    def save(self, s: Student) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = self._to_json(s)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
