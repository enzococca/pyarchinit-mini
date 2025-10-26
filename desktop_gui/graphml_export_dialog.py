"""
GraphML Export Dialog for Desktop GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path


class GraphMLExportDialog:
    """Dialog for GraphML export of Harris Matrix"""

    def __init__(self, parent, matrix_generator, matrix_visualizer, site_service):
        """
        Initialize GraphML export dialog

        Args:
            parent: Parent window
            matrix_generator: HarrisMatrixGenerator instance
            matrix_visualizer: PyArchInitMatrixVisualizer instance
            site_service: SiteService instance
        """
        self.parent = parent
        self.matrix_generator = matrix_generator
        self.matrix_visualizer = matrix_visualizer
        self.site_service = site_service

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export Harris Matrix to GraphML (yEd)")
        self.dialog.geometry("700x650")
        self.dialog.resizable(True, True)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Variables
        self.selected_site = tk.StringVar()
        self.title_var = tk.StringVar()
        self.grouping_var = tk.StringVar(value='period_area')
        self.reverse_epochs_var = tk.BooleanVar(value=False)

        self.create_widgets()
        self.load_sites()

    def create_widgets(self):
        """Create dialog widgets"""
        # Header
        header = ttk.Label(self.dialog, text="Export Harris Matrix to GraphML",
                          font=('Arial', 14, 'bold'))
        header.pack(pady=10)

        desc = ttk.Label(self.dialog,
                        text="Esporta la Harris Matrix in formato GraphML compatibile con yEd Graph Editor.\n"
                             "Questo formato preserva la struttura dei periodi archeologici.",
                        wraplength=600, justify=tk.CENTER)
        desc.pack(pady=5)

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Site selection
        site_frame = ttk.LabelFrame(main_frame, text="Sito Archeologico", padding=10)
        site_frame.pack(fill=tk.X, pady=10)

        ttk.Label(site_frame, text="Seleziona il sito:").pack(anchor=tk.W, pady=(0, 5))
        self.site_combo = ttk.Combobox(site_frame, textvariable=self.selected_site,
                                       state='readonly', width=40)
        self.site_combo.pack(fill=tk.X)

        # Title
        title_frame = ttk.LabelFrame(main_frame, text="Titolo Diagramma (opzionale)", padding=10)
        title_frame.pack(fill=tk.X, pady=10)

        ttk.Label(title_frame, text="Intestazione da visualizzare nel diagramma:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(title_frame, textvariable=self.title_var, width=40).pack(fill=tk.X)
        ttk.Label(title_frame, text="Es: Pompei - Regio VI", font=('Arial', 9, 'italic')).pack(anchor=tk.W)

        # Grouping
        grouping_frame = ttk.LabelFrame(main_frame, text="Raggruppamento", padding=10)
        grouping_frame.pack(fill=tk.X, pady=10)

        ttk.Label(grouping_frame, text="Come raggruppare le unità stratigrafiche:").pack(anchor=tk.W, pady=(0, 5))

        grouping_options = [
            ('period_area', 'Periodo + Area'),
            ('period', 'Solo Periodo'),
            ('area', 'Solo Area'),
            ('none', 'Nessun Raggruppamento')
        ]

        for value, text in grouping_options:
            ttk.Radiobutton(grouping_frame, text=text, variable=self.grouping_var,
                           value=value).pack(anchor=tk.W, padx=10)

        # Reverse epochs
        reverse_frame = ttk.Frame(main_frame)
        reverse_frame.pack(fill=tk.X, pady=10)

        ttk.Checkbutton(reverse_frame, text="Inverti ordine periodi (Periodo 1 = ultima epoca scavata)",
                       variable=self.reverse_epochs_var).pack(anchor=tk.W)


        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Export GraphML", command=self.export_graphml,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Chiudi", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Help
        help_frame = ttk.LabelFrame(self.dialog, text="Info", padding=10)
        help_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        help_text = ("Export GraphML con periodizzazione archeologica e Extended Matrix palette.\n"
                    "Include datazione estesa da periodizzazione_table e rows organizzate per periodo.\n"
                    "Download yEd gratuito: https://www.yworks.com/products/yed")
        ttk.Label(help_frame, text=help_text, font=('Arial', 9), foreground='gray').pack()

    def load_sites(self):
        """Load available sites"""
        try:
            sites = self.site_service.get_all_sites()
            site_names = [s.sito for s in sites if s.sito]

            if site_names:
                self.site_combo['values'] = site_names
                self.site_combo.current(0)
                # Set default title to first site name
                self.title_var.set(site_names[0])
            else:
                messagebox.showwarning("Avviso", "Nessun sito disponibile nel database")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento siti: {str(e)}")

    def export_graphml(self):
        """Export Harris Matrix to GraphML file"""
        try:
            site_name = self.selected_site.get()
            if not site_name:
                messagebox.showwarning("Avviso", "Seleziona un sito")
                return

            title = self.title_var.get() or site_name
            grouping = self.grouping_var.get()
            reverse_epochs = self.reverse_epochs_var.get()

            # Ask for output file
            default_filename = f"{site_name}_harris_matrix.graphml"
            filepath = filedialog.asksaveasfilename(
                parent=self.dialog,
                title="Salva Harris Matrix GraphML",
                defaultextension=".graphml",
                initialfile=default_filename,
                filetypes=[
                    ("GraphML files", "*.graphml"),
                    ("All files", "*.*")
                ]
            )

            if not filepath:
                return

            # Use the new export_to_graphml method which:
            # 1. Generates Harris Matrix graph with transitive reduction
            # 2. Queries periodizzazione_table for datazione_estesa
            # 3. Creates DOT with cluster_datazione subgraphs
            # 4. Converts to GraphML with proper TableNode Rows

            # First generate the Harris Matrix graph
            graph = self.matrix_generator.generate_matrix(site_name)

            # Then export to GraphML with clustering and periodization
            result_path = self.matrix_generator.export_to_graphml(
                graph=graph,
                output_path=filepath,
                site_name=site_name,
                title=title,
                reverse_epochs=reverse_epochs
            )

            if not result_path:
                messagebox.showerror("Errore", "Export GraphML fallito")
                return

            # Get file size for info message
            file_size = os.path.getsize(filepath) / 1024

            messagebox.showinfo("Successo",
                              f"Harris Matrix esportata con successo!\n\n"
                              f"File: {os.path.basename(filepath)}\n"
                              f"Dimensione: {file_size:.1f} KB\n\n"
                              f"Il file include:\n"
                              f"• Periodizzazione con datazione estesa\n"
                              f"• Rows organizzate per periodo\n"
                              f"• Stili Extended Matrix palette\n\n"
                              f"Apri il file con yEd Graph Editor per visualizzare e modificare la matrice.")

            self.dialog.destroy()

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Errore", f"Errore durante l'export GraphML:\n\n{str(e)}")

def show_graphml_export_dialog(parent, matrix_generator, matrix_visualizer, site_service):
    """
    Show GraphML export dialog

    Args:
        parent: Parent window
        matrix_generator: HarrisMatrixGenerator instance
        matrix_visualizer: PyArchInitMatrixVisualizer instance
        site_service: SiteService instance
    """
    GraphMLExportDialog(parent, matrix_generator, matrix_visualizer, site_service)
