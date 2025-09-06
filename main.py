#!/usr/bin/python
# -*- coding: utf-8 -*-

import pathlib
from repository import JsonStudentRepository
from dashboard_app import DashboardApp

def main():
    base = pathlib.Path(__file__).parent
    repo = JsonStudentRepository(base / "data" / "student.json")
    student = repo.load()
    app = DashboardApp(student=student)
    app.mainloop()

if __name__ == "__main__":
    main()