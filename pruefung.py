#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

from pruefungsform import Pruefungsform

@dataclass
class Pruefung:
    id: str
    kurs_id: str
    pruefungsform: Pruefungsform
    note: Optional[float] = None
