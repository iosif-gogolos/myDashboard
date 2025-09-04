#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List
from kurs import Kurs

@dataclass
class Modul:
    id: str
    name: str
    kurse: List[Kurs] = field(default_factory=list)

    @property
    def ects_summe(self) -> int:
        return sum(k.ects for k in self.kurse)

