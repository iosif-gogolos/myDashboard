from typing import Tuple
from PIL import Image


import customtkinter as ctk
from typing import List, Dict, Optional

from student import Student
from services import ProgressService, GradeService

from customtkinter import CTkInputDialog
from modul import Modul
from kurs import Kurs
from repository import JsonStudentRepository

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class DashboardApp(ctk.CTk):
    """
    Dashboard mit:
      - Overview-Cards (ECTS gesamt, Ø-Note, offene Prüfungen)
      - Scrollbarer Modulliste mit Fortschritt
    In Phase 3 wird i.d.R. ein Student-Objekt injiziert.
    """

    def __init__(self, student: Optional[Student] = None):
        super().__init__()
        self.prog_service = ProgressService()
        self.grade_service = GradeService()
        self.student = student  # kann None sein (nur für Fallback/Dev)

        self.title("myDashboard - Studienmanager")
        self.geometry("1200x700")
        self.minsize(980, 640)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # UI Layout
        self.sidebar = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(99, weight=1)
        self._build_sidebar()

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew")

        # >>> drei Zeilen: 0=Header, 1=KPIs, 2=Liste
        self.main.grid_rowconfigure(0, weight=0)  # Header: fix
        self.main.grid_rowconfigure(1, weight=0)  # KPIs: fix
        self.main.grid_rowconfigure(2, weight=1)  # Liste: wächst
        self.main.grid_columnconfigure(0, weight=1)

        # Header zuerst anlegen und in row=0 setzen
        self.header_frame = ctk.CTkFrame(self.main)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_label = ctk.CTkLabel(self.header_frame, text="", font=ctk.CTkFont(size=14))
        self.header_label.grid(row=0, column=0, sticky="w", padx=8, pady=0)

        # KPIs in row=1
        self.overview_frame = ctk.CTkFrame(self.main)
        self.overview_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 8))
        self.overview_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self._create_overview_widgets()

        # Liste in row=2
        self.list_frame = ctk.CTkFrame(self.main)
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        self._create_module_list()

        self.update_dashboard()

    # Sidebar
    def _build_sidebar(self) -> None:
        import pathlib
        logo_path = pathlib.Path(__file__).parent / "assets" / "iu_logo.png"

        # optionales Logo
        row = 0
        if logo_path.exists():
            logo_img = ctk.CTkImage(Image.open(logo_path), size=(140, 40))
            logo_lbl = ctk.CTkLabel(self.sidebar, image=logo_img, text="")
            logo_lbl.image = logo_img  # prevent GC
            logo_lbl.grid(row=row, column=0, padx=16, pady=(16, 4), sticky="w")
            row += 1

        # Titel & Untertitel
        title = ctk.CTkLabel(self.sidebar, text="myDashboard", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=row, column=0, padx=16, pady=(8, 0), sticky="w")
        row += 1

        subtitle = ctk.CTkLabel(self.sidebar, text="Studienmanager", font=ctk.CTkFont(size=13))
        subtitle.grid(row=row, column=0, padx=16, pady=(0, 16), sticky="w")
        row += 1

        # Ansicht / Filter
        ctk.CTkLabel(self.sidebar, text="Ansicht").grid(row=row, column=0, padx=16, pady=(8, 4), sticky="w")
        row += 1

        self.view_option = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Alle Module", "Nur offene Prüfungen"],
            command=lambda _v: self.update_dashboard()
        )
        self.view_option.set("Alle Module")
        self.view_option.grid(row=row, column=0, padx=16, pady=(0, 8), sticky="ew")
        row += 1

        # Aktionen
        add_btn = ctk.CTkButton(self.sidebar, text="Modul hinzufügen", command=self._add_module_dialog)
        add_btn.grid(row=row, column=0, padx=16, pady=(0, 8), sticky="ew")
        row += 1

        refresh_btn = ctk.CTkButton(self.sidebar, text="Aktualisieren", command=self.update_dashboard)
        refresh_btn.grid(row=row, column=0, padx=16, pady=16, sticky="ew")

        # Footer unten „ankleben“
        self.sidebar.grid_rowconfigure(99, weight=1)
        footer = ctk.CTkLabel(self.sidebar, text="© 2025 – I. Gogolos", anchor="w")
        footer.grid(row=99, column=0, padx=16, pady=16, sticky="sw")


    def _create_overview_widgets(self):
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
        self.scroll = ctk.CTkScrollableFrame(self.list_frame, label_text="Module")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.scroll.grid_columnconfigure(0, weight=1)
        self.module_rows: Dict[str, Dict[str, ctk.CTkBaseClass]] = {}

    def _ensure_rows(self):
        # Baue die Zeilen dynamisch anhand der Module
        # Lösche vorherige Rows
        for child in self.scroll.winfo_children():
            child.destroy()
        self.module_rows.clear()
        if not self.student:
            return

        r = 0
        for m in self.student.studiengang.module:
            # Container pro Modul
            container = ctk.CTkFrame(self.scroll)
            container.grid(row=r, column=0, sticky="ew", padx=4, pady=6)
            container.grid_columnconfigure(0, weight=1)

            # Kopfzeile des Moduls
            header = ctk.CTkFrame(container, fg_color="transparent")
            header.grid(row=0, column=0, sticky="ew")
            header.grid_columnconfigure(0, weight=1)

            lbl_name = ctk.CTkLabel(header, text=m.name, font=ctk.CTkFont(size=14, weight="bold"))
            lbl_name.grid(row=0, column=0, padx=(8, 8), pady=(8, 0), sticky="w")

            lbl_ects = ctk.CTkLabel(header, text="ECTS: —")
            lbl_ects.grid(row=0, column=1, padx=8, pady=(8, 0), sticky="e")

            prog = ctk.CTkProgressBar(container, height=16)
            prog.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 8))
            prog.set(0.0)

            # Expand/Collapse
            detail_frame = ctk.CTkFrame(container)
            detail_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
            detail_frame.grid_columnconfigure(0, weight=1)

            # Toggle-Button
            is_open = {"value": False}
            def toggle():
                is_open["value"] = not is_open["value"]
                if is_open["value"]:
                    detail_frame.grid()
                    btn_toggle.configure(text="▾ Details verbergen")
                else:
                    detail_frame.grid_remove()
                    btn_toggle.configure(text="▸ Details anzeigen")

            btn_toggle = ctk.CTkButton(container, text="▸ Details anzeigen", width=160, command=toggle)
            btn_toggle.grid(row=3, column=0, sticky="w", padx=8, pady=(0,6))
            # initial zu: details verstecken
            detail_frame.grid_remove()

            # Kursliste (wird in update_dashboard befüllt)
            self.module_rows[m.id] = {
                "container": container,
                "header": header,
                "lbl_name": lbl_name,
                "lbl_ects": lbl_ects,
                "prog": prog,
                "detail_frame": detail_frame,
                "btn_toggle": btn_toggle,
                "is_open": is_open,
                "kurse": m.kurse,  # Referenz, um IDs nicht erneut zu berechnen
            }
            r += 1

    def update_dashboard(self):
        self.header_label.configure(
            text=f"Student: {self.student.vorname} {self.student.nachname}  •  Matr.-Nr.: {self.student.matrikelnummer}  •  Studiengang: {self.student.studiengang.name}"
        )
        show_only_open = (self.view_option.get() == "Nur offene Prüfungen")
        # Wenn kein Student injiziert wurde (Dev/Fallback), zeige Striche
        if not self.student:
            self.lbl_ects.configure(text="—")
            self.lbl_avg.configure(text="—")
            self.lbl_open.configure(text="—")
            return

        # KPIs
        ects_total = self.prog_service.ects_summe(self.student.studiengang)
        avg = self.grade_service.durchschnitt_gewichtet(
            self.student.pruefungen,
            [k for m in self.student.studiengang.module for k in m.kurse]
        )
        offene_anzahl = self.prog_service.verbleibende_pruefungen(self.student.pruefungen)

        self.lbl_ects.configure(text=str(ects_total))
        self.lbl_avg.configure(text=f"{avg:.2f}" if avg is not None else "—")
        self.lbl_open.configure(text=str(offene_anzahl))

        # Module-Liste
        self._ensure_rows()
        k_index, p_index = self._build_indices()

        for m in self.student.studiengang.module:
            row_widgets = self.module_rows.get(m.id)
            if not row_widgets:
                continue

            ects_sum = sum(k.ects for k in m.kurse)
            progress = self.prog_service.modul_fortschritt(self.student.pruefungen, [k.id for k in m.kurse])
            has_open = any((p_index.get(k.id) is None) or (p_index.get(k.id).note is None) for k in m.kurse)

            # Kopf aktualisieren
            row_widgets["lbl_ects"].configure(text=f"ECTS: {ects_sum}")
            row_widgets["prog"].set(progress)

            # Detailbereich neu aufbauen (Kurse)
            df = row_widgets["detail_frame"]
            for child in df.winfo_children():
                child.destroy()

            # Tabellenkopf
            hdr = ctk.CTkFrame(df, fg_color="transparent")
            hdr.grid(row=0, column=0, sticky="ew")
            hdr.grid_columnconfigure((0,1,2,3,4), weight=1)
            ctk.CTkLabel(hdr, text="Kurs", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", padx=(4,4))
            ctk.CTkLabel(hdr, text="ECTS", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, sticky="w", padx=(4,4))
            ctk.CTkLabel(hdr, text="Prüfungsform", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=2, sticky="w", padx=(4,4))
            ctk.CTkLabel(hdr, text="Status / Note", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=3, sticky="w", padx=(4,4))
            ctk.CTkLabel(hdr, text="Aktion", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=4, sticky="w", padx=(4,4))


            # Kurszeilen
            r = 1
            for k in m.kurse:
                row = ctk.CTkFrame(df, fg_color="transparent")
                row.grid(row=r, column=0, sticky="ew", pady=2)
                row.grid_columnconfigure((0,1,2,3,4 ), weight=1)

                p = p_index.get(k.id)  # Pruefung zu diesem Kurs
                pruef_form = getattr(p, "pruefungsform", None)
                note = getattr(p, "note", None)

                # Status-Text
                if p is None or note is None:
                    status_txt = "offen"
                else:
                    status_txt = f"{note:.1f}" if note <= 4.0 else f"nicht bestanden ({note:.1f})"

                ctk.CTkLabel(row, text=k.name).grid(row=0, column=0, sticky="w", padx=4)
                ctk.CTkLabel(row, text=str(k.ects)).grid(row=0, column=1, sticky="w", padx=4)
                ctk.CTkLabel(row, text=(pruef_form.value if pruef_form else "—")).grid(row=0, column=2, sticky="w", padx=4)
                ctk.CTkLabel(row, text=status_txt).grid(row=0, column=3, sticky="w", padx=4)

                btn = ctk.CTkButton(row, text="Note setzen", width=110,
                                    command=lambda kid=k.id: self._set_grade(kid))
                btn.grid(row=0, column=4, sticky="e", padx=4)

                r += 1

            # Sichtbarkeit je nach Filter
            visible = True if not show_only_open else has_open
            if visible:
                row_widgets["container"].grid()
            else:
                row_widgets["container"].grid_remove()

            # Ende von update_dashboard
                
    def _add_module_dialog(self):
        if not self.student:
            return
        # Modulname abfragen
        name_dialog = ctk.CTkInputDialog(title="Neues Modul", text="Modulname:")
        name = name_dialog.get_input()
        if not name:
            return

        # ECTS-Liste der Kurse abfragen (einfacher Modus)
        ects_dialog = ctk.CTkInputDialog(
            title="Kurse anlegen",
            text="Kurse als 'Name:ECTS' kommasepariert eingeben (z.B. 'Datenbanken:5, Statistik:5'):"
        )
        raw = ects_dialog.get_input() or ""
        kurse = []
        idx = 1
        for part in [p.strip() for p in raw.split(",") if p.strip()]:
            try:
                kname, kects = [x.strip() for x in part.split(":")]
                ects = int(kects)
                kurse.append(Kurs(id=f"auto_k{idx}", name=kname, ects=ects))
                idx += 1
            except Exception:
                # Ignoriere fehlerhafte Einträge
                continue

        # Neues Modul anlegen
        new_mod = Modul(id=f"auto_m{len(self.student.studiengang.module)+1}", name=name, kurse=kurse)
        self.student.studiengang.module.append(new_mod)

        # Speichern
        try:
            from pathlib import Path
            base = Path(__file__).parent
            repo = JsonStudentRepository(base / "data" / "student.json")
            repo.save(self.student)
        except Exception as e:
            print("Speicherfehler:", e)

        # UI aktualisieren
        self.update_dashboard()

    def _build_indices(self) -> Tuple[dict, dict]:
        """Liefert zwei Nachschlagewerke:
        - k_index: kurs_id -> Kurs-Objekt
        - p_index: kurs_id -> Pruefung-Objekt (falls vorhanden)"""
        k_index = {}
        for m in self.student.studiengang.module:
            for k in m.kurse:
                k_index[k.id] = k
        p_index = {p.kurs_id: p for p in self.student.pruefungen}
        return k_index, p_index
    
    def _set_grade(self, kurs_id: str):
        from customtkinter import CTkInputDialog
        from pathlib import Path
        from repository import JsonStudentRepository
        from pruefung import Pruefung
        from pruefungsform import Pruefungsform

        # Eingabe
        dlg = CTkInputDialog(title="Note eingeben",
                            text="Note (z.B. 1.7). Leer lassen für 'offen':")
        raw = dlg.get_input()
        note = None
        if raw is not None and raw.strip() != "":
            try:
                note = float(raw.replace(",", "."))
            except ValueError:
                # Ungültige Eingabe -> nichts ändern
                return

        # Pruefung zu Kurs finden/erstellen
        p_index = {p.kurs_id: p for p in self.student.pruefungen}
        p = p_index.get(kurs_id)
        if p is None:
            # wenn keine vorhanden ist, legen wir eine an (Default-Form KLAUSUR)
            p = Pruefung(id=f"autoP_{kurs_id}", kurs_id=kurs_id,
                        pruefungsform=Pruefungsform.KLAUSUR, note=note)
            self.student.pruefungen.append(p)
        else:
            p.note = note

        # Speichern
        base = Path(__file__).parent
        repo = JsonStudentRepository(base / "data" / "student.json")
        repo.save(self.student)

        # UI aktualisieren (KPIs/Progress ziehen nach)
        self.update_dashboard()


