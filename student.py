#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List
from studiengang import Studiengang
from pruefung import Pruefung

@dataclass
class Student:
    id: str
    vorname: str
    nachname: str
    matrikelnummer: str
    studiengang: Studiengang
    pruefungen: List[Pruefung] = field(default_factory=list)
