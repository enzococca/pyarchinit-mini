"""Modal dialog for creating/editing a Pottery record."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from ..services.pottery_service import PotteryService

_INT_FIELDS = ("id_number", "us", "box", "anno", "qty", "bag")
_NUM_FIELDS = (
    "diametro_max", "diametro_rim", "diametro_bottom",
    "diametro_height", "diametro_preserved",
)


class PotteryDialog(tk.Toplevel):
    def __init__(self, parent, svc: PotteryService, id_rep: int | None = None):
        super().__init__(parent)
        self.title(f"Pottery — {'New' if id_rep is None else f'#{id_rep}'}")
        self.svc = svc
        self.id_rep = id_rep
        self.result_id = None
        self.vars = {}

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        desc = ttk.Frame(nb); nb.add(desc, text="Description data")
        tech = ttk.Frame(nb); nb.add(tech, text="Technical Data")
        supp = ttk.Frame(nb); nb.add(supp, text="Supplements")

        desc_fields = [
            "sito", "area", "us", "sector", "anno", "box", "bag",
            "id_number", "material", "form", "specific_form",
            "specific_shape", "photo", "drawing", "note",
        ]
        tech_fields = [
            "fabric", "ware", "munsell", "percent", "surf_trat",
            "wheel_made", "exdeco", "intdeco",
            "descrip_ex_deco", "descrip_in_deco", "qty",
            "diametro_max", "diametro_rim", "diametro_bottom",
            "diametro_height", "diametro_preserved",
        ]

        self._build_fields(desc, desc_fields)
        self._build_fields(tech, tech_fields)
        ttk.Label(supp, text="Bibliography integration coming in a future release.").pack(padx=8, pady=8)

        btn_row = ttk.Frame(self); btn_row.pack(fill="x", padx=8, pady=8)
        ttk.Button(btn_row, text="Save", command=self._save).pack(side="right", padx=4)
        ttk.Button(btn_row, text="Cancel", command=self.destroy).pack(side="right")

        if id_rep is not None:
            self._load()

        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _build_fields(self, parent, fields):
        for i, name in enumerate(fields):
            ttk.Label(parent, text=name).grid(row=i, column=0, sticky="w", padx=4, pady=2)
            v = tk.StringVar()
            self.vars[name] = v
            ttk.Entry(parent, textvariable=v, width=40).grid(row=i, column=1, sticky="we", padx=4, pady=2)
        parent.columnconfigure(1, weight=1)

    def _load(self):
        p = self.svc.get_pottery_by_id(self.id_rep)
        if not p:
            return
        for name, var in self.vars.items():
            val = getattr(p, name, None)
            var.set("" if val is None else str(val))

    def _collect(self):
        data = {}
        for name, var in self.vars.items():
            raw = var.get().strip()
            if raw == "":
                continue
            if name in _INT_FIELDS:
                try:
                    data[name] = int(raw)
                except ValueError:
                    continue
            elif name in _NUM_FIELDS:
                try:
                    data[name] = float(raw)
                except ValueError:
                    continue
            else:
                data[name] = raw
        return data

    def _save(self):
        data = self._collect()
        try:
            if self.id_rep is None:
                p = self.svc.create_pottery(data)
                self.result_id = p.id_rep
            else:
                self.svc.update_pottery(self.id_rep, data)
                self.result_id = self.id_rep
        except ValueError as e:
            messagebox.showerror("Validation", str(e))
            return
        self.destroy()
