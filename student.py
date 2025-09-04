#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from studiengang import Studiengang

@dataclass
class Student:
    id: str
    vorname: str
    nachname: str
    matrikelnummer: str
    studiengang: Studiengang