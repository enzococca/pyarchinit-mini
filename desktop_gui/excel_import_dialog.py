"""
Excel Import Dialog for Desktop GUI
Supports both Harris Matrix Template and Extended Matrix Parser formats
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import threading


class ExcelImportDialog:
    """Dialog for importing Excel files with dual format support"""

    def __init__(self, parent, session, db_manager):
        """
        Initialize Excel import dialog

        Args:
            parent: Parent window
            session: Database session
            db_manager: DatabaseManager instance
        """
        self.parent = parent
        self.session = session
        self.db_manager = db_manager

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Import Excel - Harris Matrix")
        self.dialog.geometry("700x750")
        self.dialog.resizable(True, True)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Variables
        self.selected_file = tk.StringVar()
        self.site_name = tk.StringVar()
        self.format_var = tk.StringVar(value='harris_template')
        self.generate_graphml_var = tk.BooleanVar(value=True)
        self.import_status = tk.StringVar(value="Ready")

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        # Header
        header = ttk.Label(self.dialog, text="Import Excel - Harris Matrix",
                          font=('Arial', 14, 'bold'))
        header.pack(pady=10)

        desc = ttk.Label(self.dialog,
                        text="Import stratigraphic data from Excel files.\n"
                             "Choose between Harris Matrix Template or Extended Matrix Parser format.",
                        wraplength=600, justify=tk.CENTER)
        desc.pack(pady=5)

        # Main frame with scrollbar
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Format Selection
        format_frame = ttk.LabelFrame(main_frame, text="Excel Format", padding=10)
        format_frame.pack(fill=tk.X, pady=10)

        ttk.Label(format_frame, text="Select Excel format:").pack(anchor=tk.W, pady=(0, 5))

        ttk.Radiobutton(format_frame,
                       text="Harris Matrix Template (sheet-based: NODES + RELATIONSHIPS)",
                       variable=self.format_var,
                       value='harris_template',
                       command=self.update_format_info).pack(anchor=tk.W, padx=10, pady=2)

        ttk.Radiobutton(format_frame,
                       text="Extended Matrix Parser (inline: relationships in columns)",
                       variable=self.format_var,
                       value='extended_matrix',
                       command=self.update_format_info).pack(anchor=tk.W, padx=10, pady=2)

        # Format Information
        self.info_frame = ttk.LabelFrame(main_frame, text="Format Information", padding=10)
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.info_text = tk.Text(self.info_frame, height=8, wrap=tk.WORD,
                                font=('Arial', 9), bg='#f5f5f5', relief=tk.FLAT)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Update info for default selection
        self.update_format_info()

        # File Selection
        file_frame = ttk.LabelFrame(main_frame, text="Excel File", padding=10)
        file_frame.pack(fill=tk.X, pady=10)

        file_inner = ttk.Frame(file_frame)
        file_inner.pack(fill=tk.X)

        ttk.Entry(file_inner, textvariable=self.selected_file, state='readonly').pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(file_inner, text="Browse...", command=self.browse_file).pack(side=tk.RIGHT)

        ttk.Label(file_frame, text="Supported formats: .xlsx, .xls, .csv",
                 font=('Arial', 8, 'italic'), foreground='gray').pack(anchor=tk.W, pady=(5, 0))

        # Site Name
        site_frame = ttk.LabelFrame(main_frame, text="Site Name", padding=10)
        site_frame.pack(fill=tk.X, pady=10)

        ttk.Label(site_frame, text="Archaeological site name:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(site_frame, textvariable=self.site_name, width=40).pack(fill=tk.X)
        ttk.Label(site_frame, text="Required: Enter the site name for imported data",
                 font=('Arial', 8, 'italic'), foreground='gray').pack(anchor=tk.W, pady=(5, 0))

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Import Options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)

        ttk.Checkbutton(options_frame, text="Generate GraphML for Extended Matrix visualization",
                       variable=self.generate_graphml_var).pack(anchor=tk.W)

        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)

        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=(0, 5))
        status_label = ttk.Label(status_frame, textvariable=self.import_status,
                                font=('Arial', 9), foreground='blue')
        status_label.pack(side=tk.LEFT)

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=10)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.import_button = ttk.Button(button_frame, text="Import Excel",
                                       command=self.start_import)
        self.import_button.pack(side=tk.LEFT, padx=5)

        self.template_button = ttk.Button(button_frame, text="Download Template",
                                         command=self.download_template)
        self.template_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def update_format_info(self):
        """Update format information based on selection"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)

        if self.format_var.get() == 'harris_template':
            info = """Harris Matrix Template Format

Structured Excel format with separate sheets:

• NODES Sheet:
  - us_number, unit_type, description, area, period, phase

• RELATIONSHIPS Sheet:
  - from_us, to_us, relationship, notes

Supports all Extended Matrix node types: US, USM, USVA, USVB, USVC,
TU, USD, SF, VSF, CON, DOC, Extractor, Combiner, property"""
        else:
            info = """Extended Matrix Parser Format

Single sheet with inline relationships:

• Required Columns:
  - ID: US identifier
  - DEFINITION: Short description
  - LONG_DESCRIPTION: Detailed description
  - PHASE: Archaeological phase

• Relationship Columns (comma-separated US numbers):
  - is_before, covers, is_covered_by, cuts, is_cut_by
  - leans_on, equals, fills

• Optional:
  - NOTES: Additional notes"""

        self.info_text.insert('1.0', info)
        self.info_text.config(state=tk.DISABLED)

    def browse_file(self):
        """Open file browser to select Excel file"""
        filename = filedialog.askopenfilename(
            parent=self.dialog,
            title="Select Excel File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.selected_file.set(filename)

    def download_template(self):
        """Generate and download Harris Matrix Template"""
        try:
            from pyarchinit_mini.cli.harris_template import create_template_data, create_instructions
            import pandas as pd
            import tempfile

            # Ask where to save
            save_path = filedialog.asksaveasfilename(
                parent=self.dialog,
                title="Save Harris Matrix Template",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )

            if not save_path:
                return

            # Create template data
            nodes_df, relationships_df = create_template_data()
            instructions_df = create_instructions()

            # Write Excel file
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                instructions_df.to_excel(writer, sheet_name='INSTRUCTIONS', index=False)
                nodes_df.to_excel(writer, sheet_name='NODES', index=False)
                relationships_df.to_excel(writer, sheet_name='RELATIONSHIPS', index=False)

            messagebox.showinfo("Success",
                              f"Template saved successfully:\n{save_path}",
                              parent=self.dialog)

        except Exception as e:
            messagebox.showerror("Error",
                               f"Template generation failed:\n{str(e)}",
                               parent=self.dialog)

    def start_import(self):
        """Start import process"""
        # Validate inputs
        if not self.selected_file.get():
            messagebox.showwarning("Missing File",
                                  "Please select an Excel file to import.",
                                  parent=self.dialog)
            return

        if not self.site_name.get().strip():
            messagebox.showwarning("Missing Site Name",
                                  "Please enter a site name.",
                                  parent=self.dialog)
            return

        # Disable import button and start progress
        self.import_button.config(state=tk.DISABLED)
        self.template_button.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        self.import_status.set("Importing...")

        # Run import in background thread
        thread = threading.Thread(target=self.perform_import)
        thread.daemon = True
        thread.start()

    def perform_import(self):
        """Perform the import (runs in background thread)"""
        try:
            filepath = self.selected_file.get()
            site_name = self.site_name.get().strip()
            import_format = self.format_var.get()
            generate_graphml = self.generate_graphml_var.get()

            if import_format == 'harris_template':
                result = self.import_harris_template(filepath, site_name, generate_graphml)
            else:
                result = self.import_extended_matrix(filepath, site_name, generate_graphml)

            # Update UI in main thread
            self.dialog.after(0, self.import_complete, result)

        except Exception as e:
            # Update UI in main thread
            self.dialog.after(0, self.import_failed, str(e))

    def import_harris_template(self, filepath, site_name, generate_graphml):
        """Import using Harris Matrix Template format"""
        from pyarchinit_mini.cli.harris_import import HarrisMatrixImporter
        from pyarchinit_mini.models.us import US
        from pyarchinit_mini.models.harris_matrix import USRelationships
        import tempfile

        importer = HarrisMatrixImporter(self.session, self.db_manager)

        # Create temp directory for GraphML output
        temp_dir = tempfile.mkdtemp() if generate_graphml else None

        success = importer.import_matrix(
            file_path=filepath,
            site_name=site_name,
            export_graphml=generate_graphml,
            export_dot=False,
            output_dir=temp_dir
        )

        if not success:
            error_msgs = '\n'.join(importer.errors) if importer.errors else 'Unknown error'
            return {'success': False, 'message': f'Import failed:\n{error_msgs}'}

        # Count imported data
        us_count = self.session.query(US).filter_by(sito=site_name).count()
        rel_count = self.session.query(USRelationships).filter_by(sito=site_name).count()

        return {
            'success': True,
            'message': f'Import completed successfully!\n\n'
                      f'US records: {us_count}\n'
                      f'Relationships: {rel_count}',
            'us_count': us_count,
            'relationships_count': rel_count
        }

    def import_extended_matrix(self, filepath, site_name, generate_graphml):
        """Import using Extended Matrix Parser format"""
        from pyarchinit_mini.services.extended_matrix_excel_parser import import_extended_matrix_excel

        # Use the same database connection as the desktop app
        stats = import_extended_matrix_excel(
            excel_path=filepath,
            site_name=site_name,
            generate_graphml=generate_graphml,
            db_connection=self.db_manager.connection
        )

        if stats.get('errors'):
            error_msgs = '\n'.join(stats['errors'][:5])
            return {
                'success': False,
                'message': f'Import completed with errors:\n{error_msgs}'
            }

        return {
            'success': True,
            'message': f'Import completed successfully!\n\n'
                      f'US created: {stats.get("us_created", 0)}\n'
                      f'US updated: {stats.get("us_updated", 0)}\n'
                      f'Relationships created: {stats.get("relationships_created", 0)}',
            'us_created': stats.get('us_created', 0),
            'us_updated': stats.get('us_updated', 0),
            'relationships_created': stats.get('relationships_created', 0)
        }

    def import_complete(self, result):
        """Handle import completion (runs in main thread)"""
        self.progress_bar.stop()
        self.import_button.config(state=tk.NORMAL)
        self.template_button.config(state=tk.NORMAL)

        if result['success']:
            self.import_status.set("Import completed successfully!")
            messagebox.showinfo("Success", result['message'], parent=self.dialog)

            # Refresh parent window if method exists
            if hasattr(self.parent, 'refresh_data'):
                self.parent.refresh_data()
        else:
            self.import_status.set("Import failed")
            messagebox.showerror("Import Failed", result['message'], parent=self.dialog)

    def import_failed(self, error_msg):
        """Handle import failure (runs in main thread)"""
        self.progress_bar.stop()
        self.import_button.config(state=tk.NORMAL)
        self.template_button.config(state=tk.NORMAL)
        self.import_status.set("Import failed")
        messagebox.showerror("Import Error",
                           f"Import failed with error:\n{error_msg}",
                           parent=self.dialog)
