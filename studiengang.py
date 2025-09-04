#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List
from modul import Modul

@dataclass
class Studiengang:
    id: str
    name: str
    module: List[Modul] = field(default_factory=list)