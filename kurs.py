#!/usr/bin/python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

@dataclass
class Kurs:
    id: str
    name: str
    ects: int