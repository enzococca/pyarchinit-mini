#!/usr/bin/env python3
"""
Dialog classes for PyArchInit-Mini GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import tempfile
import os
import sys
import threading
from typing import Optional, List, Callable, Any
from datetime import datetime

# Import i18n
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from desktop_gui.i18n import _

class BaseDialog:
    """Base class for dialog windows"""
    
    def __init__(self, parent, title, width=600, height=400):
        self.result = None
        self.callback = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_window()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.dialog, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        # Content frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def center_window(self):
        """Center dialog window on parent"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_buttons(self, ok_text=None, cancel_text=None):
        """Create standard OK/Cancel buttons"""
        if ok_text is None:
            ok_text = _("OK")
        if cancel_text is None:
            cancel_text = _("Cancel")
        ttk.Button(self.button_frame, text=cancel_text, command=self.cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(self.button_frame, text=ok_text, command=self.ok).pack(side=tk.RIGHT)
    
    def ok(self):
        """OK button handler - to be overridden"""
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel button handler"""
        self.result = None
        self.dialog.destroy()

class SiteDialog(BaseDialog):
    """Dialog for creating/editing sites with media support"""

    def __init__(self, parent, site_service, media_service=None, site=None, callback=None):
        title = _("New Site") if site is None else _("Edit Site")
        super().__init__(parent, title, 800, 600)

        self.site_service = site_service
        self.media_service = media_service
        self.site = site
        self.callback = callback
        self.media_list = []

        # Create media directory
        self.media_dir = self.create_media_directory()

        self.create_form()
        self.create_buttons(_("Save"), _("Cancel"))
        
        if site:
            self.populate_form()
            self.load_media()
    
    def create_media_directory(self):
        """Create media directory for the site"""
        if self.site:
            # Handle both dict and DTO objects
            if hasattr(self.site, 'sito'):
                site_name = self.site.sito or 'unknown_site'
            elif hasattr(self.site, 'get'):
                site_name = self.site.get('sito', 'unknown_site')
            else:
                site_name = 'unknown_site'
        else:
            site_name = 'new_site'
        
        media_dir = os.path.join(tempfile.gettempdir(), 'pyarchinit_media', 'sites', site_name)
        os.makedirs(media_dir, exist_ok=True)
        return media_dir
    
    def create_form(self):
        """Create site form with tabs"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic info tab
        self.create_basic_tab()
        
        # Media tab
        self.create_media_tab()
        
        # Description tab
        self.create_description_tab()
    
    def create_basic_tab(self):
        """Create basic information tab"""
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text=_("Basic Information"))

        # Create scrollable frame
        canvas = tk.Canvas(basic_frame)
        scrollbar = ttk.Scrollbar(basic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create form fields
        self.fields = {}

        # Nome sito (required)
        ttk.Label(scrollable_frame, text=_("Site Name *:")).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.fields['sito'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['sito'].grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)

        # Nazione
        ttk.Label(scrollable_frame, text=_("Country:")).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.fields['nazione'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['nazione'].grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)

        # Regione
        ttk.Label(scrollable_frame, text=_("Region:")).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.fields['regione'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['regione'].grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Comune
        ttk.Label(scrollable_frame, text=_("Municipality:")).grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.fields['comune'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['comune'].grid(row=3, column=1, sticky="ew", padx=(10, 5), pady=5)

        # Provincia
        ttk.Label(scrollable_frame, text=_("Province:")).grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.fields['provincia'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['provincia'].grid(row=4, column=1, sticky="ew", padx=(10, 5), pady=5)

        # Definizione sito
        ttk.Label(scrollable_frame, text=_("Site Definition:")).grid(row=5, column=0, sticky="w", pady=5, padx=5)
        self.fields['definizione_sito'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['definizione_sito'].grid(row=5, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Configure column weights
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Focus on first field
        self.fields['sito'].focus()
    
    def create_description_tab(self):
        """Create description tab"""
        desc_frame = ttk.Frame(self.notebook)
        self.notebook.add(desc_frame, text=_("Description"))

        # Descrizione
        ttk.Label(desc_frame, text=_("Site description:")).pack(anchor="w", pady=(10, 5))
        self.fields['descrizione'] = tk.Text(desc_frame, width=60, height=15)
        self.fields['descrizione'].pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def create_media_tab(self):
        """Create media management tab with thumbnails and drag & drop"""
        media_frame = ttk.Frame(self.notebook)
        self.notebook.add(media_frame, text=_("Media"))

        # Control buttons frame
        control_frame = ttk.Frame(media_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(control_frame, text=_("Add Media"), command=self.add_media_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text=_("Remove Selected"), command=self.remove_media_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text=_("Preview"), command=self.preview_media).pack(side=tk.LEFT, padx=5)

        # Drag and drop area
        drop_frame = ttk.LabelFrame(media_frame, text=_("Drag media files here"))
        drop_frame.pack(fill=tk.X, padx=10, pady=5)

        self.drop_area = tk.Label(drop_frame,
                                text=_("Drag media files here\n(Images, PDF, Video, Audio)"),
                                relief="sunken", bd=2, height=3)
        self.drop_area.pack(fill=tk.X, padx=5, pady=5)
        
        # Enable drag and drop
        self.drop_area.bind("<Button-1>", self.add_media_file)
        
        # Media list with thumbnails
        list_frame = ttk.LabelFrame(media_frame, text="File Media")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for media list
        columns = ('Nome', 'Tipo', 'Dimensione', 'Descrizione')
        self.media_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=8)
        
        # Configure columns
        self.media_tree.heading('#0', text='Thumbnail')
        self.media_tree.column('#0', width=100, minwidth=100)
        
        for col in columns:
            self.media_tree.heading(col, text=col)
            self.media_tree.column(col, width=120)
        
        # Scrollbars
        media_scrollbar_y = ttk.Scrollbar(list_frame, orient="vertical", command=self.media_tree.yview)
        media_scrollbar_x = ttk.Scrollbar(list_frame, orient="horizontal", command=self.media_tree.xview)
        self.media_tree.configure(yscrollcommand=media_scrollbar_y.set, xscrollcommand=media_scrollbar_x.set)
        
        self.media_tree.pack(side="left", fill="both", expand=True)
        media_scrollbar_y.pack(side="right", fill="y")
        media_scrollbar_x.pack(side="bottom", fill="x")
        
        # Description frame for selected media
        desc_frame = ttk.LabelFrame(media_frame, text="Descrizione Media")
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.media_description = tk.Text(desc_frame, height=3)
        self.media_description.pack(fill=tk.X, padx=5, pady=5)
        
        # Bind selection event
        self.media_tree.bind('<<TreeviewSelect>>', self.on_media_select)
    
    def add_media_file(self, event=None):
        """Add media file with file dialog"""
        filetypes = [
            ('Tutti i file supportati', '*.jpg *.jpeg *.png *.gif *.bmp *.pdf *.mp4 *.avi *.mov *.mp3 *.wav'),
            ('Immagini', '*.jpg *.jpeg *.png *.gif *.bmp'),
            ('Documenti', '*.pdf *.doc *.docx'),
            ('Video', '*.mp4 *.avi *.mov *.wmv'),
            ('Audio', '*.mp3 *.wav *.ogg'),
            ('Tutti i file', '*.*')
        ]
        
        file_paths = filedialog.askopenfilenames(
            title="Seleziona file media",
            filetypes=filetypes
        )
        
        for file_path in file_paths:
            self.process_media_file(file_path)
    
    def process_media_file(self, file_path):
        """Process and add media file to the list"""
        try:
            if not os.path.exists(file_path):
                messagebox.showerror("Errore", f"File non trovato: {file_path}")
                return
            
            # Get file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Determine media type
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                media_type = 'image'
            elif file_ext in ['.pdf', '.doc', '.docx']:
                media_type = 'document'
            elif file_ext in ['.mp4', '.avi', '.mov', '.wmv']:
                media_type = 'video'
            elif file_ext in ['.mp3', '.wav', '.ogg']:
                media_type = 'audio'
            else:
                media_type = 'other'
            
            # Copy file to media directory
            dest_path = os.path.join(self.media_dir, file_name)
            if file_path != dest_path:
                import shutil
                shutil.copy2(file_path, dest_path)
            
            # Add to media list
            media_info = {
                'file_path': dest_path,
                'file_name': file_name,
                'media_type': media_type,
                'file_size': file_size,
                'description': ''
            }
            
            self.media_list.append(media_info)
            self.refresh_media_list()
            
            messagebox.showinfo("Successo", f"File '{file_name}' aggiunto con successo")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'aggiunta del file: {str(e)}")
    
    def refresh_media_list(self):
        """Refresh the media list display"""
        # Clear existing items
        for item in self.media_tree.get_children():
            self.media_tree.delete(item)
        
        # Add media items
        for i, media in enumerate(self.media_list):
            # Format file size
            size_str = self.format_file_size(media['file_size'])
            
            # Insert item
            item_id = self.media_tree.insert('', 'end', 
                                            text=f"Media {i+1}",
                                            values=(media['file_name'], 
                                                   media['media_type'], 
                                                   size_str,
                                                   media['description'][:50] + '...' if len(media['description']) > 50 else media['description']))
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024*1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.1f} MB"
    
    def on_media_select(self, event):
        """Handle media selection"""
        selection = self.media_tree.selection()
        if selection:
            item = selection[0]
            index = self.media_tree.index(item)
            if 0 <= index < len(self.media_list):
                media = self.media_list[index]
                self.media_description.delete('1.0', tk.END)
                self.media_description.insert('1.0', media['description'])
    
    def remove_media_file(self):
        """Remove selected media file"""
        selection = self.media_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un file media da rimuovere")
            return
        
        item = selection[0]
        index = self.media_tree.index(item)
        
        if 0 <= index < len(self.media_list):
            media = self.media_list[index]
            
            # Confirm deletion
            if messagebox.askyesno("Conferma", f"Rimuovere il file '{media['file_name']}'?"):
                # Remove file from filesystem
                try:
                    if os.path.exists(media['file_path']):
                        os.remove(media['file_path'])
                except Exception as e:
                    messagebox.showerror("Errore", f"Errore durante la rimozione del file: {str(e)}")
                
                # Remove from list
                self.media_list.pop(index)
                self.refresh_media_list()
                
                # Clear description
                self.media_description.delete('1.0', tk.END)
    
    def preview_media(self):
        """Preview selected media file"""
        selection = self.media_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un file media da visualizzare")
            return
        
        item = selection[0]
        index = self.media_tree.index(item)
        
        if 0 <= index < len(self.media_list):
            media = self.media_list[index]
            try:
                # Open file with default application
                if os.path.exists(media['file_path']):
                    import subprocess
                    if sys.platform.startswith('darwin'):  # macOS
                        subprocess.call(['open', media['file_path']])
                    elif sys.platform.startswith('win'):  # Windows
                        os.startfile(media['file_path'])
                    else:  # Linux
                        subprocess.call(['xdg-open', media['file_path']])
                else:
                    messagebox.showerror("Errore", "File non trovato")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'apertura del file: {str(e)}")
    
    def load_media(self):
        """Load existing media files for the site"""
        if not self.site or not self.media_service:
            return
        
        try:
            # Load media from service
            # Get site ID handling both dict and DTO objects
            if hasattr(self.site, 'id_sito'):
                site_id = self.site.id_sito
            elif hasattr(self.site, 'get'):
                site_id = self.site.get('id_sito')
            else:
                site_id = None
            
            if site_id:
                media_files = self.media_service.get_media_by_entity('site', site_id)
            
            for media in media_files:
                media_info = {
                    'file_path': media.get('file_path', ''),
                    'file_name': media.get('media_name', ''),
                    'media_type': media.get('media_type', 'other'),
                    'file_size': media.get('file_size', 0),
                    'description': media.get('description', '')
                }
                self.media_list.append(media_info)
            
            self.refresh_media_list()
            
        except Exception as e:
            logger.error(f"Error loading media: {e}")
    
    def populate_form(self):
        """Populate form with existing site data"""
        if not self.site:
            return
        
        # Helper function to get attribute from both dict and DTO objects
        def get_attr(obj, attr_name, default=""):
            if hasattr(obj, attr_name):
                return getattr(obj, attr_name) or default
            elif hasattr(obj, 'get'):
                return obj.get(attr_name, default)
            else:
                return default
        
        self.fields['sito'].insert(0, get_attr(self.site, 'sito'))
        self.fields['nazione'].insert(0, get_attr(self.site, 'nazione'))
        self.fields['regione'].insert(0, get_attr(self.site, 'regione'))
        self.fields['comune'].insert(0, get_attr(self.site, 'comune'))
        self.fields['provincia'].insert(0, get_attr(self.site, 'provincia'))
        self.fields['definizione_sito'].insert(0, get_attr(self.site, 'definizione_sito'))
        self.fields['descrizione'].insert("1.0", get_attr(self.site, 'descrizione'))
    
    def ok(self):
        """Save site data"""
        try:
            # Validate required fields
            nome_sito = self.fields['sito'].get().strip()
            if not nome_sito:
                messagebox.showerror(_("Error"), _("Site name is required"))
                return

            # Prepare data
            site_data = {
                'sito': nome_sito,
                'nazione': self.fields['nazione'].get().strip() or None,
                'regione': self.fields['regione'].get().strip() or None,
                'comune': self.fields['comune'].get().strip() or None,
                'provincia': self.fields['provincia'].get().strip() or None,
                'definizione_sito': self.fields['definizione_sito'].get().strip() or None,
                'descrizione': self.fields['descrizione'].get("1.0", tk.END).strip() or None
            }

            # Save site
            if self.site:
                # Update existing site - get ID handling both dict and DTO objects
                if hasattr(self.site, 'id_sito'):
                    site_id = self.site.id_sito
                elif hasattr(self.site, 'get'):
                    site_id = self.site.get('id_sito')
                else:
                    raise ValueError("Cannot get site ID from site object")

                updated_site = self.site_service.update_site_dto(site_id, site_data)
                messagebox.showinfo(_("Success"), _("Site updated successfully"))
            else:
                # Create new site
                new_site = self.site_service.create_site_dto(site_data)
                messagebox.showinfo(_("Success"), _("Site created successfully"))

            # Call callback to refresh data
            if self.callback:
                self.callback()

            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error saving: {}").format(str(e)))

class USDialog(BaseDialog):
    """Dialog for creating/editing US"""

    def __init__(self, parent, us_service, site_names, us=None, callback=None):
        title = _("New US") if us is None else _("Edit US")
        super().__init__(parent, title, 600, 500)

        self.us_service = us_service
        self.site_names = site_names
        self.us = us
        self.callback = callback

        self.create_form()
        self.create_buttons(_("Save"), _("Cancel"))
        
        if us:
            self.populate_form()
    
    def create_form(self):
        """Create US form"""
        # Create scrollable frame
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        self.fields = {}
        row = 0

        # Sito (required)
        ttk.Label(scrollable_frame, text=_("Site *:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['sito'] = ttk.Combobox(scrollable_frame, values=self.site_names, width=37)
        self.fields['sito'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Area
        ttk.Label(scrollable_frame, text=_("Area:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['area'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['area'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # US number (required)
        ttk.Label(scrollable_frame, text=_("US Number *:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['us'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['us'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Descrizione stratigrafica
        ttk.Label(scrollable_frame, text=_("Stratigraphic Description:")).grid(row=row, column=0, sticky="nw", pady=5)
        self.fields['d_stratigrafica'] = tk.Text(scrollable_frame, width=40, height=3)
        self.fields['d_stratigrafica'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Descrizione interpretativa
        ttk.Label(scrollable_frame, text=_("Interpretative Description:")).grid(row=row, column=0, sticky="nw", pady=5)
        self.fields['d_interpretativa'] = tk.Text(scrollable_frame, width=40, height=3)
        self.fields['d_interpretativa'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Anno scavo
        ttk.Label(scrollable_frame, text=_("Excavation Year:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['anno_scavo'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['anno_scavo'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Schedatore
        ttk.Label(scrollable_frame, text=_("Cataloguer:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['schedatore'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['schedatore'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Formazione
        ttk.Label(scrollable_frame, text=_("Formation:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['formazione'] = ttk.Combobox(scrollable_frame, values=["", _("Natural"), _("Artificial")], width=37)
        self.fields['formazione'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Configure column weights
        scrollable_frame.columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Focus on first field
        self.fields['sito'].focus()
    
    def populate_form(self):
        """Populate form with existing US data"""
        if not self.us:
            return
        
        self.fields['sito'].set(self.us.sito or "")
        self.fields['area'].insert(0, self.us.area or "")
        self.fields['us'].insert(0, str(self.us.us) if self.us.us else "")
        self.fields['d_stratigrafica'].insert("1.0", self.us.d_stratigrafica or "")
        self.fields['d_interpretativa'].insert("1.0", self.us.d_interpretativa or "")
        self.fields['anno_scavo'].insert(0, str(self.us.anno_scavo) if self.us.anno_scavo else "")
        self.fields['schedatore'].insert(0, self.us.schedatore or "")
        self.fields['formazione'].set(self.us.formazione or "")
    
    def ok(self):
        """Save US data"""
        try:
            # Validate required fields
            sito = self.fields['sito'].get().strip()
            us_number = self.fields['us'].get().strip()

            if not sito:
                messagebox.showerror(_("Error"), _("Site is required"))
                return

            if not us_number:
                messagebox.showerror(_("Error"), _("US number is required"))
                return

            try:
                us_number = int(us_number)
            except ValueError:
                messagebox.showerror(_("Error"), _("US number must be an integer"))
                return

            # Prepare data
            us_data = {
                'sito': sito,
                'area': self.fields['area'].get().strip() or None,
                'us': us_number,
                'd_stratigrafica': self.fields['d_stratigrafica'].get("1.0", tk.END).strip() or None,
                'd_interpretativa': self.fields['d_interpretativa'].get("1.0", tk.END).strip() or None,
                'schedatore': self.fields['schedatore'].get().strip() or None,
                'formazione': self.fields['formazione'].get().strip() or None
            }

            # Anno scavo
            anno_text = self.fields['anno_scavo'].get().strip()
            if anno_text:
                try:
                    us_data['anno_scavo'] = int(anno_text)
                except ValueError:
                    messagebox.showerror(_("Error"), _("Excavation year must be a number"))
                    return
            else:
                us_data['anno_scavo'] = None

            # Save US
            if self.us:
                # Update existing US
                updated_us = self.us_service.update_us(self.us.id_us, us_data)
                messagebox.showinfo(_("Success"), _("US updated successfully"))
            else:
                # Create new US
                new_us = self.us_service.create_us(us_data)
                messagebox.showinfo(_("Success"), _("US created successfully"))

            # Call callback to refresh data
            if self.callback:
                self.callback()

            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error saving: {}").format(str(e)))

class InventarioDialog(BaseDialog):
    """Dialog for creating/editing inventory items"""

    def __init__(self, parent, inventario_service, site_names, inventario=None, callback=None):
        title = _("New Artifact") if inventario is None else _("Edit Artifact")
        super().__init__(parent, title, 500, 400)

        self.inventario_service = inventario_service
        self.site_names = site_names
        self.inventario = inventario
        self.callback = callback

        self.create_form()
        self.create_buttons(_("Save"), _("Cancel"))
        
        if inventario:
            self.populate_form()
    
    def create_form(self):
        """Create inventory form"""
        self.fields = {}
        row = 0

        # Sito (required)
        ttk.Label(self.content_frame, text=_("Site *:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['sito'] = ttk.Combobox(self.content_frame, values=self.site_names, width=37)
        self.fields['sito'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Numero inventario (required)
        ttk.Label(self.content_frame, text=_("Inventory Number *:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['numero_inventario'] = ttk.Entry(self.content_frame, width=40)
        self.fields['numero_inventario'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Tipo reperto
        ttk.Label(self.content_frame, text=_("Artifact Type:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['tipo_reperto'] = ttk.Combobox(self.content_frame,
                                                  values=["", _("Ceramic"), _("Metal"), _("Stone"), _("Bone"), _("Glass")],
                                                  width=37)
        self.fields['tipo_reperto'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Definizione
        ttk.Label(self.content_frame, text=_("Definition:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['definizione'] = ttk.Entry(self.content_frame, width=40)
        self.fields['definizione'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Area
        ttk.Label(self.content_frame, text=_("Area:")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['area'] = ttk.Entry(self.content_frame, width=40)
        self.fields['area'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # US
        ttk.Label(self.content_frame, text="US:").grid(row=row, column=0, sticky="w", pady=5)
        self.fields['us'] = ttk.Entry(self.content_frame, width=40)
        self.fields['us'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Peso
        ttk.Label(self.content_frame, text=_("Weight (g):")).grid(row=row, column=0, sticky="w", pady=5)
        self.fields['peso'] = ttk.Entry(self.content_frame, width=40)
        self.fields['peso'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1

        # Descrizione
        ttk.Label(self.content_frame, text=_("Description:")).grid(row=row, column=0, sticky="nw", pady=5)
        self.fields['descrizione'] = tk.Text(self.content_frame, width=40, height=5)
        self.fields['descrizione'].grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Configure column weights
        self.content_frame.columnconfigure(1, weight=1)
        
        # Focus on first field
        self.fields['sito'].focus()
    
    def populate_form(self):
        """Populate form with existing inventory data"""
        if not self.inventario:
            return
        
        self.fields['sito'].set(self.inventario.sito or "")
        self.fields['numero_inventario'].insert(0, str(self.inventario.numero_inventario) if self.inventario.numero_inventario else "")
        self.fields['tipo_reperto'].set(self.inventario.tipo_reperto or "")
        self.fields['definizione'].insert(0, self.inventario.definizione or "")
        self.fields['area'].insert(0, self.inventario.area or "")
        self.fields['us'].insert(0, str(self.inventario.us) if self.inventario.us else "")
        self.fields['peso'].insert(0, str(self.inventario.peso) if self.inventario.peso else "")
        self.fields['descrizione'].insert("1.0", self.inventario.descrizione or "")
    
    def ok(self):
        """Save inventory data"""
        try:
            # Validate required fields
            sito = self.fields['sito'].get().strip()
            numero_inv = self.fields['numero_inventario'].get().strip()

            if not sito:
                messagebox.showerror(_("Error"), _("Site is required"))
                return

            if not numero_inv:
                messagebox.showerror(_("Error"), _("Inventory number is required"))
                return

            try:
                numero_inv = int(numero_inv)
            except ValueError:
                messagebox.showerror(_("Error"), _("Inventory number must be an integer"))
                return

            # Prepare data
            inv_data = {
                'sito': sito,
                'numero_inventario': numero_inv,
                'tipo_reperto': self.fields['tipo_reperto'].get().strip() or None,
                'definizione': self.fields['definizione'].get().strip() or None,
                'area': self.fields['area'].get().strip() or None,
                'descrizione': self.fields['descrizione'].get("1.0", tk.END).strip() or None
            }

            # US
            us_text = self.fields['us'].get().strip()
            if us_text:
                try:
                    inv_data['us'] = int(us_text)
                except ValueError:
                    messagebox.showerror(_("Error"), _("US must be a number"))
                    return
            else:
                inv_data['us'] = None

            # Peso
            peso_text = self.fields['peso'].get().strip()
            if peso_text:
                try:
                    inv_data['peso'] = float(peso_text)
                except ValueError:
                    messagebox.showerror(_("Error"), _("Weight must be a number"))
                    return
            else:
                inv_data['peso'] = None

            # Save inventory
            if self.inventario:
                # Update existing item
                updated_item = self.inventario_service.update_inventario(self.inventario.id_invmat, inv_data)
                messagebox.showinfo(_("Success"), _("Artifact updated successfully"))
            else:
                # Create new item
                new_item = self.inventario_service.create_inventario(inv_data)
                messagebox.showinfo(_("Success"), _("Artifact created successfully"))

            # Call callback to refresh data
            if self.callback:
                self.callback()

            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error saving: {}").format(str(e)))

class HarrisMatrixDialog(BaseDialog):
    """Dialog for generating and viewing Harris Matrix"""

    def __init__(self, parent, matrix_generator, matrix_visualizer, sites,
                 site_service=None, us_service=None, db_manager=None):
        super().__init__(parent, _("Harris Matrix Generator"), 1200, 900)

        self.matrix_generator = matrix_generator
        self.matrix_visualizer = matrix_visualizer
        self.sites = sites
        self.site_service = site_service
        self.us_service = us_service
        self.db_manager = db_manager

        self.create_interface()
        self.create_buttons(_("Close"), "")
        # Remove OK button, only keep Close
        for widget in self.button_frame.winfo_children():
            if widget['text'] == '':
                widget.destroy()
    
    def create_interface(self):
        """Create Harris Matrix interface"""
        # Site selection
        selection_frame = ttk.Frame(self.content_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(selection_frame, text=_("Select Site:")).pack(side=tk.LEFT)

        self.site_var = tk.StringVar()
        site_names = [site.sito for site in self.sites]
        self.site_combobox = ttk.Combobox(selection_frame, textvariable=self.site_var,
                                         values=site_names, width=30)
        self.site_combobox.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(selection_frame, text=_("Generate Matrix"),
                  command=self.generate_matrix).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(selection_frame, text=_("Advanced Editor"),
                  command=self.open_advanced_editor).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(selection_frame, text=_("Export"),
                  command=self.export_matrix).pack(side=tk.LEFT, padx=(10, 0))
        
        # Results area
        results_frame = ttk.Frame(self.content_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Statistics
        self.stats_text = scrolledtext.ScrolledText(results_frame, height=8)
        self.stats_text.pack(fill=tk.X, pady=(0, 10))
        
        # Matrix visualization area
        vis_label_frame = ttk.Frame(results_frame)
        vis_label_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(vis_label_frame, text=_("Matrix Visualization:")).pack(side=tk.LEFT)

        # Layout options
        ttk.Label(vis_label_frame, text=_("Layout:")).pack(side=tk.LEFT, padx=(20, 5))
        self.layout_var = tk.StringVar(value="period_area")
        layout_combo = ttk.Combobox(vis_label_frame, textvariable=self.layout_var, 
                                   values=["period_area", "period", "area", "none"], 
                                   width=15, state="readonly")
        layout_combo.pack(side=tk.LEFT, padx=(0, 10))
        layout_combo.bind('<<ComboboxSelected>>', self.on_layout_changed)
        
        # Zoom controls
        ttk.Button(vis_label_frame, text="🔍+", width=4, 
                  command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(vis_label_frame, text="🔍-", width=4, 
                  command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(vis_label_frame, text="⌂", width=4, 
                  command=self.zoom_fit).pack(side=tk.LEFT, padx=2)
        
        # Matrix visualization with pan and zoom
        self.matrix_frame = ttk.Frame(results_frame, relief="sunken", borderwidth=1)
        self.matrix_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Create matplotlib figure for visualization
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        
        self.fig, self.ax = plt.subplots(figsize=(16, 12))
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, self.matrix_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar for pan/zoom
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.matrix_frame)
        self.toolbar.update()
        
        # Enable pan and zoom interactions
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.canvas.mpl_connect('button_release_event', self.on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Pan state
        self.pan_active = False
        self.last_pan_point = None
        self.press_event = None
        
        # Initialize empty plot with pan instructions
        instructions = _('Select a site and generate the Harris Matrix\n\nControls:\n• Drag with mouse to pan\n• Mouse wheel to zoom\n• Zoom buttons for precise control')
        self.ax.text(0.5, 0.5, instructions, 
                    ha='center', va='center', transform=self.ax.transAxes, 
                    fontsize=12, color='gray')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()
        
        # Current matrix data
        self.current_graph = None
        self.current_levels = None
        self.current_site = None
        self.current_image_path = None
        self.zoom_factor = 1.0
    
    def generate_matrix(self):
        """Generate Harris Matrix for selected site"""
        site_name = self.site_var.get()
        if not site_name:
            messagebox.showwarning(_("Selection"), _("Select a site"))
            return

        try:
            # Show progress
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert("1.0", _("Generating Harris Matrix for {}...\n").format(site_name))
            self.dialog.update()
            
            # Generate matrix
            self.current_graph = self.matrix_generator.generate_matrix(site_name)
            self.current_levels = self.matrix_generator.get_matrix_levels(self.current_graph)
            stats = self.matrix_generator.get_matrix_statistics(self.current_graph)
            self.current_site = site_name
            
            # Display statistics
            self.display_statistics(stats)
            
            # Display matrix levels
            self.display_levels()
            
            # Visualize matrix
            self.visualize_matrix()

            messagebox.showinfo(_("Completed"), _("Harris Matrix generated successfully!"))

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error generating matrix: {}").format(str(e)))
    
    def display_statistics(self, stats):
        """Display matrix statistics"""
        self.stats_text.delete("1.0", tk.END)

        stats_text = _("HARRIS MATRIX STATISTICS - {}\n\nTotal US: {}\nStratigraphic Relationships: {}\nStratigraphic Levels: {}\nValid Matrix: {}\nIsolated US: {}\n\n").format(
            self.current_site,
            stats['total_us'],
            stats['total_relationships'],
            stats['levels'],
            _('Yes') if stats['is_valid'] else _('No'),
            stats['isolated_us']
        )

        if not stats['is_valid']:
            stats_text += _("⚠️ WARNING: The matrix contains cycles or logical errors\n")

        self.stats_text.insert("1.0", stats_text)
    
    def display_levels(self):
        """Display matrix levels"""
        if not self.current_levels:
            return

        levels_text = _("\nSTRATIGRAPHIC LEVELS:\n\n")

        for level, us_list in sorted(self.current_levels.items()):
            levels_text += _("Level {}: US {}\n").format(level, ', '.join(map(str, us_list)))

        self.stats_text.insert(tk.END, levels_text)
    
    def visualize_matrix(self):
        """Visualize Harris Matrix using PyArchInit-style Graphviz"""
        if not self.current_graph or not self.current_graph.nodes():
            self.ax.clear()
            self.ax.text(0.5, 0.5, _('No data to visualize\nGenerate a Harris Matrix first'),
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=14, color='red')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
            return
            
        try:
            self.ax.clear()
            
            # Use PyArchInit-style visualizer
            from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
            visualizer = PyArchInitMatrixVisualizer()
            
            # Get layout setting
            grouping = self.layout_var.get()
            
            # Generate high-resolution matrix image with optimized settings
            settings = {
                'dpi': '300',  # Good resolution without excessive file size
                'show_legend': True, 
                'show_periods': True,
                'ranksep': '1.0',  # Optimized spacing for better layout
                'nodesep': '0.4',  # Reduced node spacing
                'size': '40,40!',   # Force size to fill more space (! forces exact size)
                'ratio': 'fill',  # Fill the entire space
                'pad': '0.1'     # Minimal padding
            }
            
            import tempfile
            output_path = tempfile.mktemp(suffix='_harris_matrix')
            self.current_image_path = visualizer.create_matrix(
                self.current_graph, 
                grouping=grouping,
                settings=settings,
                output_path=output_path
            )
            
            # Load and display image
            if self.current_image_path and os.path.exists(self.current_image_path):
                import matplotlib.image as mpimg
                img = mpimg.imread(self.current_image_path)
                self.ax.imshow(img)
                self.ax.axis('off')

                # Add title
                title = _("Harris Matrix - {} (Layout: {})").format(self.current_site, grouping)
                self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

                # Fit to window
                self.zoom_fit()

            else:
                # Fallback message
                self.ax.text(0.5, 0.5, _('Error generating image\nTry the Advanced Editor'),
                            ha='center', va='center', transform=self.ax.transAxes,
                            fontsize=14, color='red')
                self.ax.set_xticks([])
                self.ax.set_yticks([])

            self.canvas.draw()

        except Exception as e:
            print(f"Error in visualize_matrix: {e}")
            self.ax.clear()
            self.ax.text(0.5, 0.5, _('Visualization error:\n{}\n\nUse the Advanced Editor for more options').format(str(e)),
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, color='red')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
    
    def on_layout_changed(self, event=None):
        """Handle layout option change"""
        if self.current_graph:
            self.visualize_matrix()
    
    def zoom_in(self):
        """Zoom in on the matrix"""
        self.zoom_factor *= 1.2
        self._apply_zoom()
    
    def zoom_out(self):
        """Zoom out on the matrix"""
        self.zoom_factor /= 1.2
        self._apply_zoom()
    
    def zoom_fit(self):
        """Fit matrix to window"""
        self.zoom_factor = 1.0
        if hasattr(self.ax, 'images') and self.ax.images:
            self.ax.set_xlim(auto=True)
            self.ax.set_ylim(auto=True)
            self.ax.autoscale()
        self.canvas.draw()
    
    def _apply_zoom(self):
        """Apply zoom factor to the display"""
        if hasattr(self.ax, 'images') and self.ax.images:
            # Get current limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            # Calculate center
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            
            # Calculate new range
            x_range = (xlim[1] - xlim[0]) / self.zoom_factor
            y_range = (ylim[1] - ylim[0]) / self.zoom_factor
            
            # Set new limits
            self.ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            self.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            
            self.canvas.draw()
    
    def on_scroll(self, event):
        """Handle mouse wheel zoom"""
        if event.inaxes == self.ax and hasattr(self.ax, 'images') and self.ax.images:
            if event.button == 'up':
                scale_factor = 1.1
                self.zoom_factor *= scale_factor
            elif event.button == 'down':
                scale_factor = 1 / 1.1
                self.zoom_factor *= scale_factor
            else:
                return
            
            # Get mouse position
            x_mouse, y_mouse = event.xdata, event.ydata
            if x_mouse is None or y_mouse is None:
                return
                
            # Get current limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            # Calculate new limits centered on mouse position
            x_range = (xlim[1] - xlim[0]) / scale_factor
            y_range = (ylim[1] - ylim[0]) / scale_factor
            
            new_xlim = [x_mouse - x_range * (x_mouse - xlim[0]) / (xlim[1] - xlim[0]),
                       x_mouse + x_range * (xlim[1] - x_mouse) / (xlim[1] - xlim[0])]
            new_ylim = [y_mouse - y_range * (y_mouse - ylim[0]) / (ylim[1] - ylim[0]),
                       y_mouse + y_range * (ylim[1] - y_mouse) / (ylim[1] - ylim[0])]
            
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.canvas.draw()
    
    def on_button_press(self, event):
        """Handle mouse button press for pan"""
        if event.inaxes == self.ax and event.button == 1 and hasattr(self.ax, 'images') and self.ax.images:
            self.pan_active = True
            self.press_event = event
            # Change cursor to indicate pan mode
            self.canvas.get_tk_widget().config(cursor='fleur')
    
    def on_button_release(self, event):
        """Handle mouse button release"""
        if event.button == 1:
            self.pan_active = False
            self.press_event = None
            # Reset cursor
            self.canvas.get_tk_widget().config(cursor='arrow')
    
    def on_mouse_move(self, event):
        """Handle mouse movement for pan"""
        if (self.pan_active and self.press_event and event.inaxes == self.ax and 
            hasattr(self.ax, 'images') and self.ax.images):
            
            # Calculate the movement in data coordinates
            dx = event.xdata - self.press_event.xdata
            dy = event.ydata - self.press_event.ydata
            
            if dx is not None and dy is not None:
                # Get current axis limits
                xlim = self.ax.get_xlim()
                ylim = self.ax.get_ylim()
                
                # Apply pan (move in opposite direction)
                new_xlim = [xlim[0] - dx, xlim[1] - dx]
                new_ylim = [ylim[0] - dy, ylim[1] - dy]
                
                # Update axis limits
                self.ax.set_xlim(new_xlim)
                self.ax.set_ylim(new_ylim)
                
                # Redraw canvas
                self.canvas.draw_idle()
    
    def export_matrix(self):
        """Export Harris Matrix to files"""
        if not self.current_graph or not self.current_site:
            messagebox.showwarning(_("Warning"), _("Generate a matrix first"))
            return

        # Select export directory
        export_dir = filedialog.askdirectory(title=_("Select folder for export"))
        if not export_dir:
            return
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"harris_matrix_{self.current_site}_{timestamp}"
            
            # Export using PyArchInit visualizer
            from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
            visualizer = PyArchInitMatrixVisualizer()
            
            # Export to multiple formats with current layout
            base_path = os.path.join(export_dir, filename)
            exports = visualizer.export_multiple_formats(
                self.current_graph, 
                base_path,
                grouping=self.layout_var.get()
            )
            
            # Show success message
            export_list = "\n".join([f"- {fmt}: {path}" for fmt, path in exports.items()])
            messagebox.showinfo(_("Export Completed"), _("Matrix exported to:\n\n{}").format(export_list))

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error during export: {}").format(str(e)))
    
    def open_advanced_editor(self):
        """Open advanced Harris Matrix editor"""
        try:
            from .harris_matrix_editor import HarrisMatrixEditor
            
            # Check if we have the necessary services
            if not hasattr(self, 'site_service') or not hasattr(self, 'us_service'):
                messagebox.showerror(_("Error"), _("Services not available for advanced editor"))
                return
            
            # Get services from parent or create them
            from pyarchinit_mini.services.site_service import SiteService
            from pyarchinit_mini.services.us_service import USService
            from pyarchinit_mini.database.manager import DatabaseManager
            from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
            from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
            
            # Try to get services from main window or create new ones
            if hasattr(self, 'db_manager'):
                db_manager = self.db_manager
            else:
                # This shouldn't happen but let's be safe
                messagebox.showerror(_("Error"), _("Database manager not available"))
                return
            
            site_service = SiteService(db_manager)
            us_service = USService(db_manager)
            matrix_generator = HarrisMatrixGenerator(db_manager, us_service)
            matrix_visualizer = PyArchInitMatrixVisualizer()
            
            # Create and show the editor
            editor = HarrisMatrixEditor(
                self.dialog, 
                matrix_generator, 
                matrix_visualizer, 
                site_service, 
                us_service
            )

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error opening editor: {}").format(str(e)))

class PDFExportDialog(BaseDialog):
    """Dialog for PDF export"""

    def __init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites):
        super().__init__(parent, _("Export PDF"), 600, 400)

        self.pdf_generator = pdf_generator
        self.site_service = site_service
        self.us_service = us_service
        self.inventario_service = inventario_service
        self.sites = sites

        self.create_interface()
        self.create_buttons(_("Export"), _("Cancel"))
    
    def create_interface(self):
        """Create PDF export interface"""
        # Site selection
        ttk.Label(self.content_frame, text=_("Select Site:")).grid(row=0, column=0, sticky="w", pady=5)

        self.site_var = tk.StringVar()
        site_names = [site.sito for site in self.sites]
        self.site_combobox = ttk.Combobox(self.content_frame, textvariable=self.site_var,
                                         values=site_names, width=30)
        self.site_combobox.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Export type selection
        ttk.Label(self.content_frame, text=_("Export Type:")).grid(row=1, column=0, sticky="w", pady=5)

        self.export_type = tk.StringVar(value="us")
        export_frame = ttk.Frame(self.content_frame)
        export_frame.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

        ttk.Radiobutton(export_frame, text=_("US Sheets"), variable=self.export_type, value="us").pack(anchor="w")
        ttk.Radiobutton(export_frame, text=_("Inventory Sheets"), variable=self.export_type, value="inventario").pack(anchor="w")
        ttk.Radiobutton(export_frame, text=_("Complete Site Report"), variable=self.export_type, value="site").pack(anchor="w")

        # Logo selection
        ttk.Label(self.content_frame, text=_("Custom Logo:")).grid(row=2, column=0, sticky="w", pady=5)
        
        logo_frame = ttk.Frame(self.content_frame)
        logo_frame.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        self.logo_file = tk.StringVar()
        ttk.Entry(logo_frame, textvariable=self.logo_file, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(logo_frame, text=_("Browse..."), command=self.select_logo_file).pack(side=tk.RIGHT, padx=(5, 0))

        # Output file
        ttk.Label(self.content_frame, text=_("Output File:")).grid(row=3, column=0, sticky="w", pady=5)

        file_frame = ttk.Frame(self.content_frame)
        file_frame.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)

        self.output_file = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.output_file, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text=_("Browse..."), command=self.select_output_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Configure column weights
        self.content_frame.columnconfigure(1, weight=1)
        logo_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)
    
    def select_logo_file(self):
        """Select logo file"""
        filename = filedialog.askopenfilename(
            title=_("Select logo"),
            filetypes=[(_("Images"), "*.png *.jpg *.jpeg *.gif *.bmp"), (_("All files"), "*.*")]
        )
        if filename:
            self.logo_file.set(filename)

    def select_output_file(self):
        """Select output file"""
        filename = filedialog.asksaveasfilename(
            title=_("Save PDF report"),
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), (_("All files"), "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def ok(self):
        """Generate PDF report"""
        site_name = self.site_var.get()
        output_path = self.output_file.get()
        export_type = self.export_type.get()
        logo_path = self.logo_file.get() or None

        if not site_name:
            messagebox.showwarning(_("Selection"), _("Select a site"))
            return

        if not output_path:
            messagebox.showwarning(_("Output File"), _("Specify the output file"))
            return

        try:
            # Find site
            site = None
            for s in self.sites:
                if s.sito == site_name:
                    site = s
                    break

            if not site:
                messagebox.showerror(_("Error"), _("Site not found"))
                return
            
            # Handle different export types
            if export_type == "us":
                # Generate US PDF
                us_list = self.us_service.get_all_us(size=1000, filters={'sito': site_name})
                if not us_list:
                    messagebox.showwarning(_("Data"), _("No US found for site {}").format(site_name))
                    return
                
                # Convert to dict format
                us_data = []
                for us in us_list:
                    us_dict = us.to_dict() if hasattr(us, 'to_dict') else {
                        'us': us.us,
                        'sito': us.sito,
                        'area': us.area,
                        'd_stratigrafica': us.d_stratigrafica,
                        'd_interpretativa': us.d_interpretativa,
                        'anno_scavo': us.anno_scavo,
                        'responsabile': getattr(us, 'responsabile', ''),
                        'data_schedatura': getattr(us, 'data_schedatura', ''),
                        'rapporti': getattr(us, 'rapporti', ''),
                        'campioni': getattr(us, 'campioni', ''),
                        'documentazione': getattr(us, 'documentazione', '')
                    }
                    us_data.append(us_dict)
                
                # Generate US PDF with logo
                result_path = self.pdf_generator.generate_us_pdf(site_name, us_data, output_path, logo_path)
                messagebox.showinfo(_("Success"), _("US sheets saved to:\n{}").format(result_path))

            elif export_type == "inventario":
                # Generate Inventario PDF
                inv_list = self.inventario_service.get_all_inventario(size=1000, filters={'sito': site_name})
                if not inv_list:
                    messagebox.showwarning(_("Data"), _("No artifacts found for site {}").format(site_name))
                    return
                
                # Convert to dict format
                inv_data = []
                for inv in inv_list:
                    inv_dict = inv.to_dict() if hasattr(inv, 'to_dict') else {
                        'numero_inventario': inv.numero_inventario,
                        'sito': inv.sito,
                        'tipo_reperto': inv.tipo_reperto,
                        'definizione': inv.definizione,
                        'area': inv.area,
                        'us': inv.us,
                        'peso': inv.peso,
                        'stato_conservazione': getattr(inv, 'stato_conservazione', ''),
                        'schedatore': getattr(inv, 'schedatore', ''),
                        'date_scheda': getattr(inv, 'date_scheda', ''),
                        'descrizione': inv.descrizione,
                        'criterio_schedatura': getattr(inv, 'criterio_schedatura', ''),
                        'elementi_reperto': getattr(inv, 'elementi_reperto', ''),
                        'misurazioni': getattr(inv, 'misurazioni', ''),
                        'tecnologie': getattr(inv, 'tecnologie', ''),
                        'datazione_reperto': getattr(inv, 'datazione_reperto', ''),
                        'rif_biblio': getattr(inv, 'rif_biblio', '')
                    }
                    inv_data.append(inv_dict)
                
                # Generate Inventario PDF with logo
                result_path = self.pdf_generator.generate_inventario_pdf(site_name, inv_data, output_path, logo_path)
                messagebox.showinfo(_("Success"), _("Inventory sheets saved to:\n{}").format(result_path))
                
            else:  # site - complete report
                # Get data
                site_data = site.to_dict() if hasattr(site, 'to_dict') else {
                    'sito': site.sito,
                    'comune': site.comune,
                    'provincia': site.provincia,
                    'regione': site.regione,
                    'nazione': site.nazione,
                    'definizione_sito': getattr(site, 'definizione_sito', ''),
                    'descrizione': getattr(site, 'descrizione', '')
                }
                
                us_data = []
                inventory_data = []
                
                # Get US data
                us_list = self.us_service.get_all_us(size=1000, filters={'sito': site_name})
                if us_list:
                    us_data = [us.to_dict() if hasattr(us, 'to_dict') else {
                        'us': us.us,
                        'sito': us.sito,
                        'area': us.area,
                        'd_stratigrafica': us.d_stratigrafica,
                        'd_interpretativa': us.d_interpretativa,
                        'anno_scavo': us.anno_scavo
                    } for us in us_list]
                
                # Get inventory data
                inv_list = self.inventario_service.get_all_inventario(size=1000, filters={'sito': site_name})
                if inv_list:
                    inventory_data = [inv.to_dict() if hasattr(inv, 'to_dict') else {
                        'numero_inventario': inv.numero_inventario,
                        'sito': inv.sito,
                        'tipo_reperto': inv.tipo_reperto,
                        'definizione': inv.definizione,
                        'us': inv.us,
                        'peso': inv.peso,
                        'stato_conservazione': getattr(inv, 'stato_conservazione', '')
                    } for inv in inv_list]
                
                # Generate complete site report
                pdf_bytes = self.pdf_generator.generate_site_report(site_data, us_data, inventory_data, output_path=output_path)

                if pdf_bytes is None:
                    messagebox.showerror(_("Error"), _("Error generating PDF"))
                    return

                messagebox.showinfo(_("Success"), _("Complete report saved to:\n{}").format(output_path))

            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error generating PDF: {}").format(str(e)))


class DatabaseConfigDialog(BaseDialog):
    """Dialog for database configuration"""

    def __init__(self, parent, callback=None):
        super().__init__(parent, _("Database Configuration"), 600, 500)

        self.callback = callback
        self.create_interface()
        self.create_buttons(_("Connect"), _("Cancel"))
    
    def create_interface(self):
        """Create database configuration interface"""

        # Database type selection
        type_frame = ttk.LabelFrame(self.content_frame, text=_("Database Type"), padding=10)
        type_frame.pack(fill=tk.X, padx=10, pady=10)

        self.db_type = tk.StringVar(value="sqlite")
        ttk.Radiobutton(type_frame, text=_("SQLite (Local file)"),
                       variable=self.db_type, value="sqlite",
                       command=self.on_db_type_change).pack(anchor="w", pady=2)
        ttk.Radiobutton(type_frame, text=_("PostgreSQL (Server)"),
                       variable=self.db_type, value="postgresql",
                       command=self.on_db_type_change).pack(anchor="w", pady=2)

        # SQLite configuration
        self.sqlite_frame = ttk.LabelFrame(self.content_frame, text=_("SQLite Configuration"), padding=10)
        self.sqlite_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(self.sqlite_frame, text=_("Database File:")).grid(row=0, column=0, sticky="w", pady=5)
        self.sqlite_path = tk.StringVar(value="./pyarchinit_mini.db")
        ttk.Entry(self.sqlite_frame, textvariable=self.sqlite_path, width=50).grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        ttk.Button(self.sqlite_frame, text=_("Browse"), command=self.browse_sqlite_file).grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # Quick access buttons
        buttons_frame = ttk.Frame(self.sqlite_frame)
        buttons_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Button(buttons_frame, text=_("Sample Database"),
                  command=self.use_sample_database).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text=_("New Database"),
                  command=self.create_new_database).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text=_("Import Database"),
                  command=self.import_database).pack(side=tk.LEFT)

        self.sqlite_frame.columnconfigure(1, weight=1)

        # PostgreSQL configuration
        self.postgres_frame = ttk.LabelFrame(self.content_frame, text=_("PostgreSQL Configuration"), padding=10)
        self.postgres_frame.pack(fill=tk.X, padx=10, pady=10)

        # Host
        ttk.Label(self.postgres_frame, text=_("Host:")).grid(row=0, column=0, sticky="w", pady=5)
        self.pg_host = tk.StringVar(value="localhost")
        ttk.Entry(self.postgres_frame, textvariable=self.pg_host, width=30).grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Port
        ttk.Label(self.postgres_frame, text=_("Port:")).grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.pg_port = tk.StringVar(value="5432")
        ttk.Entry(self.postgres_frame, textvariable=self.pg_port, width=10).grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)

        # Database
        ttk.Label(self.postgres_frame, text=_("Database:")).grid(row=1, column=0, sticky="w", pady=5)
        self.pg_database = tk.StringVar(value="pyarchinit")
        ttk.Entry(self.postgres_frame, textvariable=self.pg_database, width=30).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Username
        ttk.Label(self.postgres_frame, text=_("Username:")).grid(row=2, column=0, sticky="w", pady=5)
        self.pg_username = tk.StringVar(value="postgres")
        ttk.Entry(self.postgres_frame, textvariable=self.pg_username, width=30).grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Password
        ttk.Label(self.postgres_frame, text=_("Password:")).grid(row=3, column=0, sticky="w", pady=5)
        self.pg_password = tk.StringVar()
        ttk.Entry(self.postgres_frame, textvariable=self.pg_password, show="*", width=30).grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Test connection button
        ttk.Button(self.postgres_frame, text=_("Test Connection"),
                  command=self.test_connection).grid(row=4, column=1, pady=10)
        
        self.postgres_frame.columnconfigure(1, weight=1)
        
        # Connection info
        info_frame = ttk.LabelFrame(self.content_frame, text=_("Information"), padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info_text = _("""DATABASE CONFIGURATION

SQLite:
• Local database stored in a file
• Ideal for single user
• Easy to transport and share

PostgreSQL:
• Professional database server
• Supports multi-user access
• Better performance for large datasets
• Requires PostgreSQL server installation

NOTE: Changing database will reload the interface
and data migrations may be required.""")

        ttk.Label(info_frame, text=info_text, justify="left").pack(anchor="w")
        
        # Initialize visibility
        self.on_db_type_change()
    
    def on_db_type_change(self):
        """Handle database type change"""
        if self.db_type.get() == "sqlite":
            self.sqlite_frame.pack(fill=tk.X, padx=10, pady=5)
            self.postgres_frame.pack_forget()
        else:
            self.postgres_frame.pack(fill=tk.X, padx=10, pady=5)
            self.sqlite_frame.pack_forget()
    
    def browse_sqlite_file(self):
        """Browse for SQLite file"""
        filename = filedialog.askopenfilename(
            title=_("Select SQLite database file"),
            filetypes=[("SQLite files", "*.db"), (_("All files"), "*.*")]
        )
        if filename:
            self.sqlite_path.set(filename)
    
    def use_sample_database(self):
        """Use the sample database"""
        import os
        sample_db_path = os.path.join("data", "pyarchinit_mini_sample.db")

        if os.path.exists(sample_db_path):
            self.sqlite_path.set(sample_db_path)
            messagebox.showinfo(_("Sample Database"),
                               _("Sample database loaded!\n\n"
                               "Contents:\n"
                               "• 1 Archaeological site\n"
                               "• 100 Stratigraphic units\n"
                               "• 50 Artifacts\n"
                               "• 70+ Stratigraphic relationships"))
        else:
            if messagebox.askyesno(_("Missing Database"),
                                  _("The sample database does not exist.\n"
                                  "Do you want to create it now?")):
                self.create_sample_database()
    
    def create_new_database(self):
        """Create a new empty database"""
        filename = filedialog.asksaveasfilename(
            title=_("Create new SQLite database"),
            defaultextension=".db",
            filetypes=[("SQLite files", "*.db"), (_("All files"), "*.*")]
        )
        if filename:
            # Remove file if it exists
            import os
            if os.path.exists(filename):
                os.remove(filename)
            self.sqlite_path.set(filename)
            messagebox.showinfo(_("New Database"), _("New database created: {}").format(filename))

    def import_database(self):
        """Import database from file"""
        filename = filedialog.askopenfilename(
            title=_("Import SQLite database"),
            filetypes=[("SQLite files", "*.db"), (_("All files"), "*.*")]
        )
        if filename:
            self.sqlite_path.set(filename)
            messagebox.showinfo(_("Import Database"), _("Database imported: {}").format(filename))
    
    def create_sample_database(self):
        """Create sample database"""
        try:
            import subprocess
            import sys
            import os
            
            script_path = os.path.join("scripts", "populate_simple_data.py")
            if os.path.exists(script_path):
                # Run the script
                result = subprocess.run([sys.executable, script_path], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    sample_db_path = os.path.join("data", "pyarchinit_mini_sample.db")
                    self.sqlite_path.set(sample_db_path)
                    messagebox.showinfo(_("Success"),
                                       _("Sample database created successfully!\n\n"
                                       "Contents:\n"
                                       "• 1 Archaeological site\n"
                                       "• 100 US with relationships\n"
                                       "• 50 Artifacts"))
                else:
                    messagebox.showerror(_("Error"), _("Database creation error: {}").format(result.stderr))
            else:
                messagebox.showerror(_("Error"), _("Database creation script not found"))

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error during creation: {}").format(str(e)))
    
    def test_connection(self):
        """Test PostgreSQL connection"""
        try:
            connection_string = self.build_postgres_connection_string()

            # Test connection
            from pyarchinit_mini.database.connection import DatabaseConnection
            test_conn = DatabaseConnection.from_url(connection_string)

            if test_conn.test_connection():
                messagebox.showinfo(_("Success"), _("PostgreSQL connection successful!"))
            else:
                messagebox.showerror(_("Error"), _("PostgreSQL connection failed"))

            test_conn.close()

        except Exception as e:
            messagebox.showerror(_("Error"), _("Connection test error: {}").format(str(e)))

    def build_postgres_connection_string(self):
        """Build PostgreSQL connection string"""
        host = self.pg_host.get().strip()
        port = self.pg_port.get().strip()
        database = self.pg_database.get().strip()
        username = self.pg_username.get().strip()
        password = self.pg_password.get()

        if not all([host, port, database, username]):
            raise ValueError(_("All PostgreSQL fields are required"))

        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    def ok(self):
        """Connect to selected database"""
        try:
            if self.db_type.get() == "sqlite":
                db_path = self.sqlite_path.get().strip()
                if not db_path:
                    messagebox.showerror(_("Error"), _("Specify the SQLite file path"))
                    return
                connection_string = f"sqlite:///{db_path}"
            else:
                connection_string = self.build_postgres_connection_string()

            # Test connection before applying
            from pyarchinit_mini.database.connection import DatabaseConnection
            test_conn = DatabaseConnection.from_url(connection_string)

            if not test_conn.test_connection():
                messagebox.showerror(_("Error"), _("Unable to connect to database"))
                test_conn.close()
                return

            test_conn.close()

            # Apply connection
            if self.callback:
                self.callback(connection_string)

            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(_("Error"), _("Database configuration error: {}").format(str(e)))

class MediaManagerDialog(BaseDialog):
    """Dialog for media management"""

    def __init__(self, parent, media_handler):
        super().__init__(parent, _("Media Management"), 700, 500)

        self.media_handler = media_handler

        self.create_interface()
        self.create_buttons(_("Close"), "")
        # Remove OK button, only keep Close
        for widget in self.button_frame.winfo_children():
            if widget['text'] == '':
                widget.destroy()

    def create_interface(self):
        """Create media management interface"""
        # Upload section
        upload_frame = ttk.LabelFrame(self.content_frame, text=_("Upload New File"), padding=10)
        upload_frame.pack(fill=tk.X, pady=(0, 10))

        # File selection
        ttk.Label(upload_frame, text=_("File:")).grid(row=0, column=0, sticky="w", pady=5)

        file_frame = ttk.Frame(upload_frame)
        file_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        self.selected_file = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.selected_file, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text=_("Browse..."), command=self.select_file).pack(side=tk.RIGHT, padx=(5, 0))

        # Entity info
        ttk.Label(upload_frame, text=_("Entity Type:")).grid(row=1, column=0, sticky="w", pady=5)
        self.entity_type = ttk.Combobox(upload_frame, values=["site", "us", "inventario"], width=27)
        self.entity_type.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

        ttk.Label(upload_frame, text=_("Entity ID:")).grid(row=2, column=0, sticky="w", pady=5)
        self.entity_id = ttk.Entry(upload_frame, width=30)
        self.entity_id.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Description
        ttk.Label(upload_frame, text=_("Description:")).grid(row=3, column=0, sticky="nw", pady=5)
        self.description = tk.Text(upload_frame, width=30, height=3)
        self.description.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Upload button
        ttk.Button(upload_frame, text=_("Upload File"), command=self.upload_file).grid(row=4, column=1, sticky="e", pady=5)

        # Configure column weights
        upload_frame.columnconfigure(1, weight=1)
        file_frame.columnconfigure(0, weight=1)

        # Media list section
        list_frame = ttk.LabelFrame(self.content_frame, text=_("Media Files"), padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # TODO: Implement media file listing
        ttk.Label(list_frame, text=_("Media file list (in development)")).pack()
    
    def select_file(self):
        """Select file to upload"""
        filename = filedialog.askopenfilename(
            title=_("Select file to upload"),
            filetypes=[
                (_("Images"), "*.jpg *.jpeg *.png *.gif *.bmp"),
                (_("Documents"), "*.pdf *.doc *.docx *.txt"),
                (_("Videos"), "*.mp4 *.avi *.mov"),
                (_("All files"), "*.*")
            ]
        )
        if filename:
            self.selected_file.set(filename)

    def upload_file(self):
        """Upload selected file"""
        file_path = self.selected_file.get()
        entity_type = self.entity_type.get()
        entity_id_str = self.entity_id.get().strip()
        description = self.description.get("1.0", tk.END).strip()

        if not file_path:
            messagebox.showwarning(_("File"), _("Select a file to upload"))
            return

        if not entity_type:
            messagebox.showwarning(_("Entity"), _("Select the entity type"))
            return

        if not entity_id_str:
            messagebox.showwarning(_("ID"), _("Enter the entity ID"))
            return

        try:
            entity_id = int(entity_id_str)
        except ValueError:
            messagebox.showerror(_("ID"), _("ID must be a number"))
            return

        try:
            # Store file
            metadata = self.media_handler.store_file(
                file_path, entity_type, entity_id, description, "", ""
            )

            messagebox.showinfo(_("Success"), _("File uploaded successfully!"))

            # Clear form
            self.selected_file.set("")
            self.entity_type.set("")
            self.entity_id.delete(0, tk.END)
            self.description.delete("1.0", tk.END)

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error during upload: {}").format(str(e)))

class StatisticsDialog(BaseDialog):
    """Dialog for viewing statistics"""

    def __init__(self, parent, site_service, us_service, inventario_service):
        super().__init__(parent, _("Statistics"), 600, 400)

        self.site_service = site_service
        self.us_service = us_service
        self.inventario_service = inventario_service

        self.create_interface()
        self.create_buttons(_("Close"), "")
        # Remove OK button, only keep Close
        for widget in self.button_frame.winfo_children():
            if widget['text'] == '':
                widget.destroy()

        self.load_statistics()

    def create_interface(self):
        """Create statistics interface"""
        # Statistics display
        self.stats_text = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        # Refresh button
        refresh_frame = ttk.Frame(self.content_frame)
        refresh_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(refresh_frame, text=_("Refresh"), command=self.load_statistics).pack(side=tk.RIGHT)
    
    def load_statistics(self):
        """Load and display statistics"""
        try:
            # Get basic counts
            total_sites = self.site_service.count_sites()
            total_us = self.us_service.count_us()
            total_inventory = self.inventario_service.count_inventario()
            
            # Get site statistics
            sites = self.site_service.get_all_sites(size=100)

            stats_text = _("PYARCHINIT-MINI STATISTICS\nDate: {}\n\nOVERALL TOTALS:\n• Archaeological Sites: {}\n• Stratigraphic Units: {}\n• Catalogued Artifacts: {}\n\nDETAILS BY SITE:\n").format(
                datetime.now().strftime('%d/%m/%Y %H:%M'),
                total_sites,
                total_us,
                total_inventory
            )

            for site in sites:
                site_name = site.sito
                us_count = self.us_service.count_us({'sito': site_name})
                inv_count = self.inventario_service.count_inventario({'sito': site_name})

                stats_text += f"\n{site_name}:\n"
                stats_text += _("  - US: {}\n").format(us_count)
                stats_text += _("  - Artifacts: {}\n").format(inv_count)
                if site.comune:
                    stats_text += _("  - Municipality: {}\n").format(site.comune)
            
            # Display statistics
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert("1.0", stats_text)

        except Exception as e:
            messagebox.showerror(_("Error"), _("Error loading statistics: {}").format(str(e)))