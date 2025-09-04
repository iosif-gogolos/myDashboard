import customtkinter as ctk
from typing import List, Dict, Optional

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class DashboardApp(ctk.CTk):
    """
    Minimal lauffähiges Dashboard mit:
      - Overview-Cards (ECTS gesamt, Ø-Note, offene Prüfungen)
      - Scrollbarer Modulliste mit Fortschritt
    Die Daten liegen hier als In-Memory-Beispiel vor, damit die GUI sofort läuft.
    In Phase 3 kannst du das mit echten Klassen/Repos ersetzen.
    """

    def _seed_data(self) -> None:
        self.kurse: Dict[str, Dict] = {
            "k1": {"id": "k1", "name": "Programmieren 1", "ects": 5},
            "k2": {"id": "k2", "name": "Mathematik 1",     "ects": 5},
            "k3": {"id": "k3", "name": "Datenbanken",       "ects": 5},
            "k4": {"id": "k4", "name": "SE Grundlagen",     "ects": 5},
            "k5": {"id": "k5", "name": "Statistik",         "ects": 5},
        }
        self.module: List[Dict] = [
            {"id": "m1", "name": "Semester 1", "kurse": ["k1", "k2", "k3"]},
            {"id": "m2", "name": "Semester 2", "kurse": ["k4", "k5"]},
        ]
        self.pruefungen: Dict[str, Dict] = {
            "k1": {"kurs_id": "k1", "note": 1.7},
            "k2": {"kurs_id": "k2", "note": 2.3},
            "k3": {"kurs_id": "k3", "note": None},  
            "k4": {"kurs_id": "k4", "note": 3.0},
            "k5": {"kurs_id": "k5", "note": None}, 
        }

    def __init__(self):
        super().__init__()

        self.title("myDashboard - Studienmanager")
        self.geometry("1200x700")
        self.minsize(980, 640)


        self.grid_columnconfigure(0, weight=0)  
        self.grid_columnconfigure(1, weight=1)  
        self.grid_rowconfigure(0, weight=1)

        self._seed_data()

        self.sidebar = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(99, weight=1)

        self._build_sidebar()

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(0, weight=0)  
        self.main.grid_rowconfigure(1, weight=1)  
        self.main.grid_columnconfigure(0, weight=1)

        self.overview_frame = ctk.CTkFrame(self.main)
        self.overview_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        self.overview_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.list_frame = ctk.CTkFrame(self.main)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        self._create_overview_widgets()
        self._create_module_list()

        self.update_dashboard()

    # Sidebar 
    def _build_sidebar(self) -> None:
        title = ctk.CTkLabel(self.sidebar, text="myDashboard", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        subtitle = ctk.CTkLabel(self.sidebar, text="Studienmanager", font=ctk.CTkFont(size=13))
        subtitle.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        # Dummy-Filter (später an Repos/Services hängen)
        ctk.CTkLabel(self.sidebar, text="Ansicht").grid(row=2, column=0, padx=16, pady=(8, 4), sticky="w")
        self.view_option = ctk.CTkOptionMenu(self.sidebar, values=["Alle Module", "Nur offene Prüfungen"], command=lambda _v: self.update_dashboard())
        self.view_option.set("Alle Module")
        self.view_option.grid(row=3, column=0, padx=16, pady=(0, 8), sticky="ew")

        refresh_btn = ctk.CTkButton(self.sidebar, text="Aktualisieren", command=self.update_dashboard)
        refresh_btn.grid(row=98, column=0, padx=16, pady=16, sticky="ew")

        footer = ctk.CTkLabel(self.sidebar, text="© 2025 – I. Gogolos", anchor="w")
        footer.grid(row=99, column=0, padx=16, pady=16, sticky="sw")

    def _create_overview_widgets(self):
        """
        Erstellt die 3 Overview-Karten:
          - ECTS gesamt
          - Ø-Note (gewichtet nach ECTS über bestandene Prüfungen)
          - Offene Prüfungen
        Speichert die Label-Referenzen in self.* für update_dashboard().
        """
        self.card_ects = ctk.CTkFrame(self.overview_frame)
        self.card_avg  = ctk.CTkFrame(self.overview_frame)
        self.card_open = ctk.CTkFrame(self.overview_frame)

        self.card_ects.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=8)
        self.card_avg.grid (row=0, column=1, sticky="ew", padx=8,      pady=8)
        self.card_open.grid(row=0, column=2, sticky="ew", padx=(8, 0), pady=8)

        for c in (self.card_ects, self.card_avg, self.card_open):
            c.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.card_ects, text="ECTS gesamt", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=12, pady=(12, 0), sticky="w")
        self.lbl_ects = ctk.CTkLabel(self.card_ects, text="—", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_ects.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="w")

        ctk.CTkLabel(self.card_avg, text="Ø-Note (gewichtet)", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=12, pady=(12, 0), sticky="w")
        self.lbl_avg = ctk.CTkLabel(self.card_avg, text="—", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_avg.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="w")

        ctk.CTkLabel(self.card_open, text="Offene Prüfungen", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=12, pady=(12, 0), sticky="w")
        self.lbl_open = ctk.CTkLabel(self.card_open, text="—", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_open.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="w")

    def _create_module_list(self):
        """
        Erzeugt eine scrollbare Liste der Module.
        Jedes Modul zeigt:
          - Name
          - ECTS-Summe
          - Fortschrittsbalken (bestandene Kurse / alle Kurse)
        Die Zeilen-Widgets werden in self.module_rows gehalten und in update_dashboard() aktualisiert.
        """

        self.scroll = ctk.CTkScrollableFrame(self.list_frame, label_text="Module")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.scroll.grid_columnconfigure(0, weight=1)

        self.module_rows: Dict[str, Dict[str, ctk.CTkBaseClass]] = {}

        r = 0
        for m in self.module:
            row = ctk.CTkFrame(self.scroll)
            row.grid(row=r, column=0, sticky="ew", padx=4, pady=4)
            row.grid_columnconfigure(1, weight=1)

            lbl_name = ctk.CTkLabel(row, text=m["name"], font=ctk.CTkFont(size=14, weight="bold"))
            lbl_name.grid(row=0, column=0, padx=(8, 8), pady=(8, 0), sticky="w")

            lbl_ects = ctk.CTkLabel(row, text="ECTS: —")
            lbl_ects.grid(row=0, column=2, padx=8, pady=(8, 0), sticky="e")

            prog = ctk.CTkProgressBar(row, height=16)
            prog.grid(row=1, column=0, columnspan=3, sticky="ew", padx=8, pady=(6, 10))
            prog.set(0.0)

            self.module_rows[m["id"]] = {
                "row": row,
                "lbl_name": lbl_name,
                "lbl_ects": lbl_ects,
                "prog": prog,
            }
            r += 1

    def update_dashboard(self):
        """
        Berechnet KPIs und aktualisiert alle sichtbaren Widgets.
        Logik:
          - ECTS gesamt = Summe ECTS aller Kurse
          - Ø-Note gewichtet: sum(note*ects) / sum(ects) über bestandene Prüfungen (note <= 4.0)
          - Offene Prüfungen = Prüfungen mit note == None
          - Modul-Fortschritt = bestandene Kurse / alle Kurse
        """

        show_only_open = (self.view_option.get() == "Nur offene Prüfungen")

        ects_total = sum(k["ects"] for k in self.kurse.values())

        w_sum = 0.0
        w_ects = 0.0
        offene_anzahl = 0

        for pid, p in self.pruefungen.items():
            note: Optional[float] = p["note"]
            if note is None:
                offene_anzahl += 1
                continue
            if note <= 4.0:
                ects = self.kurse[p["kurs_id"]]["ects"]
                w_sum += note * ects
                w_ects += ects

        avg_txt = "—"
        if w_ects > 0:
            avg = w_sum / w_ects
            avg_txt = f"{avg:.2f}"

        self.lbl_ects.configure(text=str(ects_total))
        self.lbl_avg.configure(text=avg_txt)
        self.lbl_open.configure(text=str(offene_anzahl))

        for m in self.module:
            kurse_ids = m["kurse"]
            kurse = [self.kurse[kid] for kid in kurse_ids]
            ects_sum = sum(k["ects"] for k in kurse)

            bestanden = 0
            total = len(kurse_ids)
            for kid in kurse_ids:
                p = self.pruefungen.get(kid)
                if p and p["note"] is not None and p["note"] <= 4.0:
                    bestanden += 1

            progress = (bestanden / total) if total else 0.0

            has_open = any((self.pruefungen.get(kid, {"note": None})["note"] is None) for kid in kurse_ids)
            visible = True if not show_only_open else has_open

            row_widgets = self.module_rows[m["id"]]
            row_widgets["lbl_ects"].configure(text=f"ECTS: {ects_sum}")
            row_widgets["prog"].set(progress)

            if visible:
                row_widgets["row"].grid()  
            else:
                row_widgets["row"].grid_remove()

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
