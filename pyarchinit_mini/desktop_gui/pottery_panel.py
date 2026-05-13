"""Tkinter panel for the Pottery records tab."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from ..services.pottery_service import PotteryService


class PotteryPanel(ttk.Frame):
    """Pottery list view with toolbar + treeview."""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.svc = PotteryService(db_manager)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=4, pady=4)
        for text, cmd in [
            ("+ New", self.on_new),
            ("Edit", self.on_edit),
            ("Delete", self.on_delete),
            ("Refresh", self.refresh),
        ]:
            ttk.Button(toolbar, text=text, command=cmd).pack(side="left", padx=2)

        cols = ("id_rep", "sito", "area", "us", "form", "fabric", "qty")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=80, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.tree.bind("<Double-1>", lambda e: self.on_edit())

        self.status = ttk.Label(self, text="", anchor="w")
        self.status.pack(fill="x", padx=4, pady=2)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        items, total = self.svc.get_all_pottery(page=1, size=1000)
        for p in items:
            self.tree.insert(
                "", "end",
                values=(
                    p.id_rep, p.sito, p.area or "", p.us or "",
                    p.form or "", p.fabric or "", p.qty or "",
                ),
            )
        self.status.config(text=f"{total} record(s)")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def on_new(self):
        from .pottery_dialog_extended import PotteryDialog
        dlg = PotteryDialog(self, self.svc)
        if dlg.result_id is not None:
            self.refresh()

    def on_edit(self):
        id_rep = self._selected_id()
        if id_rep is None:
            messagebox.showinfo("Pottery", "Select a row first.")
            return
        from .pottery_dialog_extended import PotteryDialog
        dlg = PotteryDialog(self, self.svc, id_rep=id_rep)
        if dlg.result_id is not None:
            self.refresh()

    def on_delete(self):
        id_rep = self._selected_id()
        if id_rep is None:
            messagebox.showinfo("Pottery", "Select a row first.")
            return
        if not messagebox.askyesno("Pottery", f"Delete #{id_rep}?"):
            return
        if self.svc.delete_pottery(id_rep):
            self.refresh()
