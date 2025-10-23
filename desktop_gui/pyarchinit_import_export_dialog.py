"""
PyArchInit Import/Export Dialog for Desktop GUI

Allows importing and exporting data between PyArchInit (full version)
and PyArchInit-Mini databases.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from desktop_gui.i18n import _
except ImportError:
    def _(text):
        return text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PyArchInitImportExportDialog(tk.Toplevel):
    """Dialog for importing/exporting data from/to PyArchInit"""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager

        self.title(_("Import/Export from PyArchInit"))
        self.geometry("900x700")
        self.resizable(True, True)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"900x700+{x}+{y}")

        # Variables
        self.source_db_path = tk.StringVar()
        self.db_type = tk.StringVar(value="sqlite")
        self.postgres_host = tk.StringVar(value="localhost")
        self.postgres_port = tk.StringVar(value="5432")
        self.postgres_db = tk.StringVar(value="pyarchinit")
        self.postgres_user = tk.StringVar()
        self.postgres_password = tk.StringVar()

        self.import_sites = tk.BooleanVar(value=True)
        self.import_us = tk.BooleanVar(value=True)
        self.import_inventario = tk.BooleanVar(value=True)
        self.import_periodizzazione = tk.BooleanVar(value=True)
        self.import_thesaurus = tk.BooleanVar(value=False)
        self.import_relationships = tk.BooleanVar(value=True)

        self.selected_sites = []

        # Create UI
        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Tab 1: Import
        import_tab = ttk.Frame(notebook, padding="10")
        notebook.add(import_tab, text=_("Import from PyArchInit"))

        # Tab 2: Export
        export_tab = ttk.Frame(notebook, padding="10")
        notebook.add(export_tab, text=_("Export to PyArchInit"))

        # Create Import tab content
        self._create_import_tab(import_tab)

        # Create Export tab content
        self._create_export_tab(export_tab)

        # Status/Log area (shared between tabs)
        log_frame = ttk.LabelFrame(main_frame, text=_("Status / Log"), padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate', variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text=_("Close"), command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def _create_import_tab(self, parent):
        """Create import tab content"""
        # Database selection section
        db_frame = ttk.LabelFrame(parent, text=_("Source PyArchInit Database"), padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 10))

        # Database type
        type_frame = ttk.Frame(db_frame)
        type_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(type_frame, text=_("Database Type:")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(type_frame, text="SQLite", variable=self.db_type, value="sqlite",
                        command=self._toggle_db_type).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="PostgreSQL", variable=self.db_type, value="postgresql",
                        command=self._toggle_db_type).pack(side=tk.LEFT, padx=5)

        # SQLite path selection
        self.sqlite_frame = ttk.Frame(db_frame)
        self.sqlite_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(self.sqlite_frame, text=_("Database File:")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(self.sqlite_frame, textvariable=self.source_db_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.sqlite_frame, text=_("Browse..."), command=self._browse_database).pack(side=tk.LEFT)

        # PostgreSQL connection details
        self.postgres_frame = ttk.Frame(db_frame)
        # Initially hidden
        # self.postgres_frame.pack(fill=tk.X, pady=(0, 5))

        pg_grid = ttk.Frame(self.postgres_frame)
        pg_grid.pack(fill=tk.X)

        ttk.Label(pg_grid, text=_("Host:")).grid(row=0, column=0, sticky='w', pady=2)
        ttk.Entry(pg_grid, textvariable=self.postgres_host, width=30).grid(row=0, column=1, sticky='ew', pady=2, padx=(5, 10))

        ttk.Label(pg_grid, text=_("Port:")).grid(row=0, column=2, sticky='w', pady=2)
        ttk.Entry(pg_grid, textvariable=self.postgres_port, width=10).grid(row=0, column=3, sticky='w', pady=2, padx=(5, 0))

        ttk.Label(pg_grid, text=_("Database:")).grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(pg_grid, textvariable=self.postgres_db, width=30).grid(row=1, column=1, sticky='ew', pady=2, padx=(5, 10))

        ttk.Label(pg_grid, text=_("User:")).grid(row=2, column=0, sticky='w', pady=2)
        ttk.Entry(pg_grid, textvariable=self.postgres_user, width=30).grid(row=2, column=1, sticky='ew', pady=2, padx=(5, 10))

        ttk.Label(pg_grid, text=_("Password:")).grid(row=3, column=0, sticky='w', pady=2)
        ttk.Entry(pg_grid, textvariable=self.postgres_password, width=30, show='*').grid(row=3, column=1, sticky='ew', pady=2, padx=(5, 10))

        pg_grid.columnconfigure(1, weight=1)

        # Test connection button
        ttk.Button(db_frame, text=_("Test Connection"), command=self._test_connection).pack(anchor='w', pady=(5, 0))

        # What to import section
        import_frame = ttk.LabelFrame(parent, text=_("What to Import"), padding="10")
        import_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Checkboxes for tables
        ttk.Checkbutton(import_frame, text=_("Sites (site_table)"), variable=self.import_sites).pack(anchor='w', pady=2)
        ttk.Checkbutton(import_frame, text=_("US - Stratigraphic Units (us_table)"), variable=self.import_us).pack(anchor='w', pady=2)
        ttk.Checkbutton(import_frame, text=_("US Relationships (from rapporti field)"), variable=self.import_relationships).pack(anchor='w', pady=2, padx=(20, 0))
        ttk.Checkbutton(import_frame, text=_("Inventario Materiali (inventario_materiali_table)"), variable=self.import_inventario).pack(anchor='w', pady=2)
        ttk.Checkbutton(import_frame, text=_("Periodizzazione (periodizzazione_table)"), variable=self.import_periodizzazione).pack(anchor='w', pady=2)
        ttk.Checkbutton(import_frame, text=_("Thesaurus (pyarchinit_thesaurus_sigle)"), variable=self.import_thesaurus).pack(anchor='w', pady=2)

        # Site filter
        filter_frame = ttk.Frame(import_frame)
        filter_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(filter_frame, text=_("Filter by Sites (optional):")).pack(anchor='w')
        sites_info_frame = ttk.Frame(filter_frame)
        sites_info_frame.pack(fill=tk.X, pady=(5, 0))

        self.sites_label = ttk.Label(sites_info_frame, text=_("All sites"), foreground='gray')
        self.sites_label.pack(side=tk.LEFT)

        ttk.Button(sites_info_frame, text=_("Select Sites..."), command=self._select_sites).pack(side=tk.RIGHT)

        # Import button
        ttk.Button(parent, text=_("Start Import"), command=self._start_import,
                   style='Accent.TButton').pack(pady=(10, 0))

    def _create_export_tab(self, parent):
        """Create export tab content"""
        # Target database selection
        db_frame = ttk.LabelFrame(parent, text=_("Target PyArchInit Database"), padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(db_frame, text=_("Export to PyArchInit database (SQLite or PostgreSQL)")).pack(anchor='w', pady=(0, 10))

        # Database path/connection
        path_frame = ttk.Frame(db_frame)
        path_frame.pack(fill=tk.X)

        ttk.Label(path_frame, text=_("Database:")).pack(side=tk.LEFT, padx=(0, 5))
        self.export_db_path = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.export_db_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(path_frame, text=_("Browse..."), command=self._browse_export_database).pack(side=tk.LEFT)

        # What to export
        export_frame = ttk.LabelFrame(parent, text=_("What to Export"), padding="10")
        export_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.export_sites = tk.BooleanVar(value=True)
        self.export_us = tk.BooleanVar(value=True)
        self.export_relationships = tk.BooleanVar(value=True)

        ttk.Checkbutton(export_frame, text=_("Sites"), variable=self.export_sites).pack(anchor='w', pady=2)
        ttk.Checkbutton(export_frame, text=_("US - Stratigraphic Units"), variable=self.export_us).pack(anchor='w', pady=2)
        ttk.Checkbutton(export_frame, text=_("US Relationships (to rapporti field)"), variable=self.export_relationships).pack(anchor='w', pady=2, padx=(20, 0))

        ttk.Label(export_frame, text=_("Note: Only Sites and US can be exported to PyArchInit"),
                  foreground='gray', font=('TkDefaultFont', 9, 'italic')).pack(anchor='w', pady=(10, 0))

        # Export button
        ttk.Button(parent, text=_("Start Export"), command=self._start_export,
                   style='Accent.TButton').pack(pady=(10, 0))

    def _toggle_db_type(self):
        """Toggle between SQLite and PostgreSQL input"""
        if self.db_type.get() == "sqlite":
            self.postgres_frame.pack_forget()
            self.sqlite_frame.pack(fill=tk.X, pady=(0, 5))
        else:
            self.sqlite_frame.pack_forget()
            self.postgres_frame.pack(fill=tk.X, pady=(0, 5))

    def _browse_database(self):
        """Browse for SQLite database file"""
        filename = filedialog.askopenfilename(
            title=_("Select PyArchInit Database"),
            filetypes=[
                (_("SQLite Database"), "*.sqlite *.db *.sqlite3"),
                (_("All Files"), "*.*")
            ]
        )
        if filename:
            self.source_db_path.set(filename)

    def _browse_export_database(self):
        """Browse for export database file"""
        filename = filedialog.askopenfilename(
            title=_("Select Target PyArchInit Database"),
            filetypes=[
                (_("SQLite Database"), "*.sqlite *.db *.sqlite3"),
                (_("All Files"), "*.*")
            ]
        )
        if filename:
            self.export_db_path.set(filename)

    def _get_connection_string(self) -> Optional[str]:
        """Build database connection string"""
        if self.db_type.get() == "sqlite":
            db_path = self.source_db_path.get()
            if not db_path:
                messagebox.showerror(_("Error"), _("Please select a database file"))
                return None
            return f"sqlite:///{db_path}"
        else:
            # PostgreSQL
            host = self.postgres_host.get()
            port = self.postgres_port.get()
            database = self.postgres_db.get()
            user = self.postgres_user.get()
            password = self.postgres_password.get()

            if not all([host, port, database, user]):
                messagebox.showerror(_("Error"), _("Please fill in all PostgreSQL connection details"))
                return None

            return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def _test_connection(self):
        """Test database connection"""
        conn_string = self._get_connection_string()
        if not conn_string:
            return

        self._log(_("Testing connection..."))

        def test_thread():
            try:
                from pyarchinit_mini.services.import_export_service import ImportExportService

                # Get current mini DB connection string
                mini_db_url = self.db_manager.connection.connection_string

                service = ImportExportService(mini_db_url)

                if service.validate_database_connection(conn_string):
                    service.set_source_database(conn_string)
                    sites = service.get_available_sites_in_source()

                    self.after(0, lambda: self._log(
                        _("✓ Connection successful! Found {} sites in database").format(len(sites))
                    ))
                    self.after(0, lambda: messagebox.showinfo(
                        _("Success"),
                        _("Connection successful!\nFound {} sites: {}").format(
                            len(sites),
                            ", ".join(sites[:5]) + ("..." if len(sites) > 5 else "")
                        )
                    ))
                else:
                    self.after(0, lambda: self._log(_("✗ Connection failed")))
                    self.after(0, lambda: messagebox.showerror(
                        _("Error"),
                        _("Failed to connect to database. Please check your connection settings.")
                    ))

            except Exception as e:
                self.after(0, lambda: self._log(f"✗ Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror(_("Error"), str(e)))

        thread = threading.Thread(target=test_thread, daemon=True)
        thread.start()

    def _select_sites(self):
        """Open dialog to select specific sites"""
        conn_string = self._get_connection_string()
        if not conn_string:
            messagebox.showwarning(_("Warning"), _("Please configure database connection first"))
            return

        # Get available sites
        try:
            from pyarchinit_mini.services.import_export_service import ImportExportService

            mini_db_url = self.db_manager.connection.connection_string
            service = ImportExportService(mini_db_url)
            service.set_source_database(conn_string)
            available_sites = service.get_available_sites_in_source()

            # Open site selection dialog
            SiteSelectionDialog(self, available_sites, self._on_sites_selected)

        except Exception as e:
            messagebox.showerror(_("Error"), str(e))

    def _on_sites_selected(self, selected_sites):
        """Callback when sites are selected"""
        self.selected_sites = selected_sites
        if selected_sites:
            self.sites_label.config(text=f"{len(selected_sites)} " + _("sites selected"))
        else:
            self.sites_label.config(text=_("All sites"))

    def _start_import(self):
        """Start import process"""
        conn_string = self._get_connection_string()
        if not conn_string:
            return

        # Check what to import
        if not any([self.import_sites.get(), self.import_us.get(),
                    self.import_inventario.get(), self.import_periodizzazione.get(),
                    self.import_thesaurus.get()]):
            messagebox.showwarning(_("Warning"), _("Please select at least one table to import"))
            return

        # Confirm
        if not messagebox.askyesno(_("Confirm Import"),
                                    _("Start importing data from PyArchInit?\nThis may take several minutes.")):
            return

        # Clear log
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')

        # Start progress bar
        self.progress_bar.start(10)

        # Run import in thread
        def import_thread():
            try:
                from pyarchinit_mini.services.import_export_service import ImportExportService

                mini_db_url = self.db_manager.connection.connection_string
                service = ImportExportService(mini_db_url, conn_string)

                site_filter = self.selected_sites if self.selected_sites else None

                # Import sites
                if self.import_sites.get():
                    self.after(0, lambda: self._log(_("Importing sites...")))
                    stats = service.import_sites(site_filter)
                    self.after(0, lambda: self._log_stats(_("Sites"), stats))

                # Import US
                if self.import_us.get():
                    self.after(0, lambda: self._log(_("Importing US...")))
                    stats = service.import_us(site_filter, self.import_relationships.get())
                    self.after(0, lambda: self._log_stats(_("US"), stats))

                # Import Inventario
                if self.import_inventario.get():
                    self.after(0, lambda: self._log(_("Importing Inventario Materiali...")))
                    stats = service.import_inventario(site_filter)
                    self.after(0, lambda: self._log_stats(_("Inventario"), stats))

                # Import Periodizzazione
                if self.import_periodizzazione.get():
                    self.after(0, lambda: self._log(_("Importing Periodizzazione...")))
                    stats = service.import_periodizzazione(site_filter)
                    self.after(0, lambda: self._log_stats(_("Periodizzazione"), stats))

                # Import Thesaurus
                if self.import_thesaurus.get():
                    self.after(0, lambda: self._log(_("Importing Thesaurus...")))
                    stats = service.import_thesaurus()
                    self.after(0, lambda: self._log_stats(_("Thesaurus"), stats))

                self.after(0, lambda: self.progress_bar.stop())
                self.after(0, lambda: self._log(_("\n✓ Import completed successfully!")))
                self.after(0, lambda: messagebox.showinfo(_("Success"), _("Import completed successfully!")))

            except Exception as e:
                self.after(0, lambda: self.progress_bar.stop())
                self.after(0, lambda: self._log(f"\n✗ Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror(_("Error"), str(e)))

        thread = threading.Thread(target=import_thread, daemon=True)
        thread.start()

    def _start_export(self):
        """Start export process"""
        target_db = self.export_db_path.get()
        if not target_db:
            messagebox.showerror(_("Error"), _("Please select target database"))
            return

        # Build connection string
        target_conn_string = f"sqlite:///{target_db}"

        # Confirm
        if not messagebox.askyesno(_("Confirm Export"),
                                    _("Start exporting data to PyArchInit?\nExisting data may be updated.")):
            return

        # Clear log
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')

        # Start progress bar
        self.progress_bar.start(10)

        # Run export in thread
        def export_thread():
            try:
                from pyarchinit_mini.services.import_export_service import ImportExportService

                mini_db_url = self.db_manager.connection.connection_string
                service = ImportExportService(mini_db_url)

                # Export sites
                if self.export_sites.get():
                    self.after(0, lambda: self._log(_("Exporting sites...")))
                    stats = service.export_sites(target_conn_string)
                    self.after(0, lambda: self._log_stats(_("Sites"), stats))

                # Export US
                if self.export_us.get():
                    self.after(0, lambda: self._log(_("Exporting US...")))
                    stats = service.export_us(target_conn_string, export_relationships=self.export_relationships.get())
                    self.after(0, lambda: self._log_stats(_("US"), stats))

                self.after(0, lambda: self.progress_bar.stop())
                self.after(0, lambda: self._log(_("\n✓ Export completed successfully!")))
                self.after(0, lambda: messagebox.showinfo(_("Success"), _("Export completed successfully!")))

            except Exception as e:
                self.after(0, lambda: self.progress_bar.stop())
                self.after(0, lambda: self._log(f"\n✗ Error: {str(e)}"))
                self.after(0, lambda: messagebox.showerror(_("Error"), str(e)))

        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()

    def _log(self, message):
        """Add message to log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def _log_stats(self, table_name, stats):
        """Log import/export statistics"""
        self._log(f"  {table_name}:")
        self._log(f"    Imported/Exported: {stats.get('imported', stats.get('exported', 0))}")
        self._log(f"    Updated: {stats.get('updated', 0)}")
        self._log(f"    Skipped: {stats.get('skipped', 0)}")
        if stats.get('errors'):
            self._log(f"    Errors: {len(stats['errors'])}")


class SiteSelectionDialog(tk.Toplevel):
    """Dialog for selecting sites to import"""

    def __init__(self, parent, available_sites, callback):
        super().__init__(parent)
        self.callback = callback
        self.available_sites = available_sites

        self.title(_("Select Sites to Import"))
        self.geometry("400x500")

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"400x500+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets"""
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=_("Select sites to import:")).pack(anchor='w', pady=(0, 5))

        # Search box
        search_var = tk.StringVar()
        search_var.trace('w', lambda *args: self._filter_sites(search_var.get()))

        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_frame, text=_("Filter:")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(search_frame, textvariable=search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Listbox with scrollbar
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Populate listbox
        for site in self.available_sites:
            self.listbox.insert(tk.END, site)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text=_("Select All"), command=self._select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=_("Deselect All"), command=self._deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=_("OK"), command=self._ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text=_("Cancel"), command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def _filter_sites(self, filter_text):
        """Filter sites by search text"""
        self.listbox.delete(0, tk.END)
        filter_text = filter_text.lower()

        for site in self.available_sites:
            if filter_text in site.lower():
                self.listbox.insert(tk.END, site)

    def _select_all(self):
        """Select all sites"""
        self.listbox.select_set(0, tk.END)

    def _deselect_all(self):
        """Deselect all sites"""
        self.listbox.selection_clear(0, tk.END)

    def _ok(self):
        """Confirm selection"""
        selected_indices = self.listbox.curselection()
        selected_sites = [self.listbox.get(i) for i in selected_indices]
        self.callback(selected_sites)
        self.destroy()
