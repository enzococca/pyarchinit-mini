#!/usr/bin/env python3
"""
Advanced Media Manager with Drag & Drop support
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from PIL import Image, ImageTk
import tempfile

class AdvancedMediaManager:
    """
    Advanced Media Manager with drag & drop functionality and entity associations
    """
    
    def __init__(self, parent, media_handler, site_service, us_service, inventario_service):
        self.parent = parent
        self.media_handler = media_handler
        self.site_service = site_service
        self.us_service = us_service
        self.inventario_service = inventario_service
        
        # Current selection
        self.current_entity_type = None
        self.current_entity_id = None
        self.current_site = None
        
        # Media data
        self.media_list = []
        self.thumbnails_cache = {}
        
        # Create main window
        self.window = TkinterDnD.Tk() if parent is None else tk.Toplevel(parent)
        self.window.title("Gestione Media Avanzata")
        self.window.geometry("1200x800")
        self.window.resizable(True, True)
        
        # Make window modal if it has a parent
        if parent:
            self.window.transient(parent)
            self.window.grab_set()
        
        # Create interface
        self.create_interface()
        self.load_sites()
        
    def create_interface(self):
        """Create the main interface"""
        
        # Create main frames
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Top controls
        self.create_top_controls(top_frame)
        
        # Create paned window for main content
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - entity selection and upload
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Right panel - media gallery
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)
        
        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)
        
    def create_top_controls(self, parent):
        """Create top level controls"""
        
        # Title
        title_label = ttk.Label(parent, text="Gestione Media Archeologici", 
                               style="Title.TLabel", font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Global actions
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(side=tk.RIGHT)
        
        ttk.Button(actions_frame, text="Aggiorna", command=self.refresh_media).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Esporta Archive", command=self.export_archive).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Chiudi", command=self.close_window).pack(side=tk.LEFT, padx=5)
        
    def create_left_panel(self, parent):
        """Create left panel with entity selection and upload"""
        
        # Entity selection section
        entity_frame = ttk.LabelFrame(parent, text="Selezione Entità", padding=10)
        entity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Site selection
        ttk.Label(entity_frame, text="Sito:").grid(row=0, column=0, sticky="w", pady=5)
        self.site_var = tk.StringVar()
        self.site_combo = ttk.Combobox(entity_frame, textvariable=self.site_var, width=30)
        self.site_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.site_combo.bind('<<ComboboxSelected>>', self.on_site_changed)
        
        # Entity type selection
        ttk.Label(entity_frame, text="Tipo:").grid(row=1, column=0, sticky="w", pady=5)
        self.entity_type_var = tk.StringVar(value="site")
        entity_types = [("site", "Sito"), ("us", "US"), ("inventario", "Reperto")]
        entity_type_frame = ttk.Frame(entity_frame)
        entity_type_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        for value, text in entity_types:
            ttk.Radiobutton(entity_type_frame, text=text, variable=self.entity_type_var,
                           value=value, command=self.on_entity_type_changed).pack(side=tk.LEFT, padx=5)

        # Entity ID selection
        ttk.Label(entity_frame, text="Entità:").grid(row=2, column=0, sticky="w", pady=5)
        self.entity_var = tk.StringVar()
        self.entity_combo = ttk.Combobox(entity_frame, textvariable=self.entity_var, width=30)
        self.entity_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.entity_combo.bind('<<ComboboxSelected>>', self.on_entity_changed)

        # Configure grid weights
        entity_frame.columnconfigure(1, weight=1)

        # Upload section with drag & drop
        upload_frame = ttk.LabelFrame(parent, text="Carica Media", padding=10)
        upload_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Drag & drop area
        self.create_drop_area(upload_frame)

        # Upload controls
        self.create_upload_controls(upload_frame)

    def create_drop_area(self, parent):
        """Create drag & drop area"""
        
        drop_frame = ttk.LabelFrame(parent, text="Trascina i File Qui", padding=20)
        drop_frame.pack(fill=tk.X, pady=10)
        
        # Drop zone
        self.drop_zone = tk.Label(drop_frame, 
                                 text="📁 Trascina file qui\n\nFormati supportati:\n• Immagini: JPG, PNG, GIF, BMP\n• Documenti: PDF, DOC, TXT\n• Video: MP4, AVI, MOV",
                                 bg="lightgray", 
                                 relief="ridge", 
                                 borderwidth=2,
                                 font=("", 12),
                                 height=8)
        self.drop_zone.pack(fill=tk.X, pady=10)
        
        # Enable drag & drop
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Visual feedback for drag over
        self.drop_zone.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.drop_zone.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        
    def create_upload_controls(self, parent):
        """Create upload controls"""
        
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # File description
        ttk.Label(controls_frame, text="Descrizione:").pack(anchor="w")
        self.description_text = tk.Text(controls_frame, height=3, wrap=tk.WORD)
        self.description_text.pack(fill=tk.X, pady=5)
        
        # Tags
        ttk.Label(controls_frame, text="Tags (separati da virgola):").pack(anchor="w")
        self.tags_entry = ttk.Entry(controls_frame)
        self.tags_entry.pack(fill=tk.X, pady=5)
        
        # Author
        ttk.Label(controls_frame, text="Autore/Fotografo:").pack(anchor="w")
        self.author_entry = ttk.Entry(controls_frame)
        self.author_entry.pack(fill=tk.X, pady=5)
        
        # Upload buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="Seleziona File", 
                  command=self.select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Carica File Selezionati", 
                  command=self.upload_selected_files).pack(side=tk.LEFT, padx=5)
        
        # Selected files list
        self.selected_files = []
        self.files_listbox = tk.Listbox(controls_frame, height=4)
        self.files_listbox.pack(fill=tk.X, pady=5)
        
        files_buttons_frame = ttk.Frame(controls_frame)
        files_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(files_buttons_frame, text="Rimuovi Selezionato", 
                  command=self.remove_selected_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(files_buttons_frame, text="Pulisci Lista", 
                  command=self.clear_file_list).pack(side=tk.LEFT, padx=5)
        
    def create_right_panel(self, parent):
        """Create right panel with media gallery"""
        
        # Media gallery
        gallery_frame = ttk.LabelFrame(parent, text="Galleria Media", padding=5)
        gallery_frame.pack(fill=tk.BOTH, expand=True)
        
        # Gallery controls
        gallery_controls = ttk.Frame(gallery_frame)
        gallery_controls.pack(fill=tk.X, pady=5)
        
        # View options
        ttk.Label(gallery_controls, text="Vista:").pack(side=tk.LEFT)
        self.view_mode = tk.StringVar(value="grid")
        ttk.Radiobutton(gallery_controls, text="Griglia", variable=self.view_mode, 
                       value="grid", command=self.change_view_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(gallery_controls, text="Lista", variable=self.view_mode, 
                       value="list", command=self.change_view_mode).pack(side=tk.LEFT, padx=5)
        
        # Filter options
        ttk.Label(gallery_controls, text="Filtro:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_type = tk.StringVar(value="all")
        filter_types = [("all", "Tutti"), ("image", "Immagini"), ("document", "Documenti"), ("video", "Video")]
        for value, text in filter_types:
            ttk.Radiobutton(gallery_controls, text=text, variable=self.filter_type, 
                           value=value, command=self.apply_filter).pack(side=tk.LEFT, padx=2)
        
        # Search
        ttk.Label(gallery_controls, text="Cerca:").pack(side=tk.RIGHT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(gallery_controls, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.RIGHT)
        search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        # Media display area
        self.create_media_display(gallery_frame)
        
    def create_media_display(self, parent):
        """Create media display area"""
        
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.media_frame = ttk.Frame(canvas)
        
        self.media_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.media_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store references
        self.media_canvas = canvas
        self.media_scrollbar = scrollbar
        
    def load_sites(self):
        """Load available sites"""
        try:
            sites = self.site_service.get_all_sites(size=200)
            site_names = [site.sito for site in sites]
            self.site_combo['values'] = site_names
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento siti: {e}")
    
    def on_site_changed(self, event=None):
        """Handle site selection change"""
        self.current_site = self.site_var.get()
        self.on_entity_type_changed()
        
    def on_entity_type_changed(self, event=None):
        """Handle entity type change"""
        self.current_entity_type = self.entity_type_var.get()
        self.load_entities()
        
    def load_entities(self):
        """Load entities based on type and site"""
        if not self.current_site:
            return
            
        try:
            entities = []
            
            if self.current_entity_type == "site":
                # Just the current site
                entities = [(self.current_site, f"Sito: {self.current_site}")]
            elif self.current_entity_type == "us":
                # Get US for the site
                us_list = self.us_service.get_us_by_site(self.current_site, size=1000)
                entities = [(us.id_us, f"US {us.us} - {us.d_stratigrafica[:50] if us.d_stratigrafica else ''}") 
                           for us in us_list]
            elif self.current_entity_type == "inventario":
                # Get inventory for the site
                inv_list = self.inventario_service.get_inventario_by_site(self.current_site, size=1000)
                entities = [(inv.id_invmat, f"Inv {inv.numero_inventario} - {inv.definizione or inv.tipo_reperto or ''}") 
                           for inv in inv_list]
            
            # Update combobox
            self.entity_combo['values'] = [display for _, display in entities]
            self.entity_data = {display: entity_id for entity_id, display in entities}
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento entità: {e}")
    
    def on_entity_changed(self, event=None):
        """Handle entity selection change"""
        entity_display = self.entity_var.get()
        if entity_display in self.entity_data:
            self.current_entity_id = self.entity_data[entity_display]
            self.refresh_media()
    
    def on_drag_enter(self, event):
        """Handle drag enter"""
        self.drop_zone.config(bg="lightblue")
        
    def on_drag_leave(self, event):
        """Handle drag leave"""
        self.drop_zone.config(bg="lightgray")
        
    def handle_drop(self, event):
        """Handle file drop"""
        self.drop_zone.config(bg="lightgray")
        
        # Get dropped files
        files = self.window.tk.splitlist(event.data)
        
        # Add to selected files list
        for file_path in files:
            if os.path.isfile(file_path) and file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_listbox.insert(tk.END, os.path.basename(file_path))
        
        messagebox.showinfo("File Aggiunti", f"Aggiunti {len(files)} file alla lista")
    
    def select_files(self):
        """Select files using file dialog"""
        files = filedialog.askopenfilenames(
            title="Seleziona file da caricare",
            filetypes=[
                ("Immagini", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Documenti", "*.pdf *.doc *.docx *.txt"),
                ("Video", "*.mp4 *.avi *.mov"),
                ("Tutti i files", "*.*")
            ]
        )
        
        for file_path in files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_listbox.insert(tk.END, os.path.basename(file_path))
    
    def remove_selected_file(self):
        """Remove selected file from list"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.files_listbox.delete(index)
            del self.selected_files[index]
    
    def clear_file_list(self):
        """Clear file list"""
        self.files_listbox.delete(0, tk.END)
        self.selected_files.clear()
    
    def upload_selected_files(self):
        """Upload all selected files"""
        if not self.selected_files:
            messagebox.showwarning("File", "Nessun file selezionato")
            return
            
        if not self.current_entity_type or not self.current_entity_id:
            messagebox.showwarning("Entità", "Seleziona un'entità")
            return
        
        # Get metadata
        description = self.description_text.get("1.0", tk.END).strip()
        tags = self.tags_entry.get().strip()
        author = self.author_entry.get().strip()
        
        uploaded_count = 0
        errors = []
        
        for file_path in self.selected_files:
            try:
                # Store file
                metadata = self.media_handler.store_file(
                    file_path, self.current_entity_type, self.current_entity_id,
                    description, tags, author
                )
                
                # TODO: Save metadata to database
                uploaded_count += 1
                
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        # Show results
        if uploaded_count > 0:
            messagebox.showinfo("Upload Completato", 
                               f"Caricati {uploaded_count} file con successo")
            
            # Clear form
            self.clear_file_list()
            self.description_text.delete("1.0", tk.END)
            self.tags_entry.delete(0, tk.END)
            
            # Refresh media display
            self.refresh_media()
        
        if errors:
            error_message = "Errori durante l'upload:\n" + "\n".join(errors)
            messagebox.showerror("Errori Upload", error_message)
    
    def refresh_media(self):
        """Refresh media display"""
        if not self.current_entity_type or not self.current_entity_id:
            self.clear_media_display()
            return
            
        try:
            # Get media files for current entity
            self.media_list = self.media_handler.organize_media_by_entity(
                self.current_entity_type, self.current_entity_id)
            
            # Apply current filters
            self.apply_filter()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento media: {e}")
    
    def apply_filter(self):
        """Apply current filter to media list"""
        if not hasattr(self, 'media_list'):
            return
            
        filtered_media = self.media_list.copy()
        
        # Apply type filter
        filter_type = self.filter_type.get()
        if filter_type != "all":
            filtered_media = [media for media in filtered_media 
                            if media.get('media_type') == filter_type]
        
        # Apply search filter
        search_term = self.search_var.get().lower()
        if search_term:
            filtered_media = [media for media in filtered_media 
                            if search_term in media.get('filename', '').lower()]
        
        # Display filtered media
        self.display_media(filtered_media)
    
    def display_media(self, media_list):
        """Display media in the gallery"""
        # Clear current display
        self.clear_media_display()
        
        if not media_list:
            no_media_label = ttk.Label(self.media_frame, text="Nessun file multimediale trovato")
            no_media_label.pack(pady=50)
            return
        
        view_mode = self.view_mode.get()
        
        if view_mode == "grid":
            self.display_media_grid(media_list)
        else:
            self.display_media_list(media_list)
    
    def display_media_grid(self, media_list):
        """Display media in grid view"""
        # Create grid
        columns = 4
        for i, media in enumerate(media_list):
            row = i // columns
            col = i % columns
            
            # Create media card
            card = self.create_media_card(self.media_frame, media)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nw")
    
    def display_media_list(self, media_list):
        """Display media in list view"""
        for media in media_list:
            # Create media row
            row = self.create_media_row(self.media_frame, media)
            row.pack(fill=tk.X, padx=5, pady=2)
    
    def create_media_card(self, parent, media):
        """Create media card for grid view"""
        card = ttk.Frame(parent, relief="raised", borderwidth=1)
        
        # Thumbnail
        try:
            if media.get('media_type') == 'image':
                # Load and resize image
                image_path = media['path']
                img = Image.open(image_path)
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Store reference to prevent garbage collection
                card.image = photo
                
                thumbnail_label = tk.Label(card, image=photo)
                thumbnail_label.pack(pady=5)
            else:
                # Show file type icon
                file_type = media.get('media_type', 'unknown')
                icon_text = {'document': '📄', 'video': '🎥', 'audio': '🎵'}.get(file_type, '📁')
                thumbnail_label = tk.Label(card, text=icon_text, font=("", 48))
                thumbnail_label.pack(pady=5)
        except Exception:
            # Fallback icon
            thumbnail_label = tk.Label(card, text="❓", font=("", 48))
            thumbnail_label.pack(pady=5)
        
        # File info
        filename = os.path.basename(media['path'])
        if len(filename) > 20:
            filename = filename[:17] + "..."
        
        ttk.Label(card, text=filename, font=("", 9)).pack()
        
        file_size = media.get('file_size', 0)
        if file_size > 1024*1024:
            size_text = f"{file_size/(1024*1024):.1f} MB"
        elif file_size > 1024:
            size_text = f"{file_size/1024:.0f} KB"
        else:
            size_text = f"{file_size} B"
        
        ttk.Label(card, text=size_text, font=("", 8), foreground="gray").pack()
        
        # Action buttons
        button_frame = ttk.Frame(card)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Apri", width=8,
                  command=lambda: self.open_media(media)).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Elimina", width=8,
                  command=lambda: self.delete_media(media)).pack(side=tk.LEFT, padx=2)
        
        return card
    
    def create_media_row(self, parent, media):
        """Create media row for list view"""
        row = ttk.Frame(parent)
        
        # File icon
        file_type = media.get('media_type', 'unknown')
        icon_text = {'image': '🖼️', 'document': '📄', 'video': '🎥', 'audio': '🎵'}.get(file_type, '📁')
        ttk.Label(row, text=icon_text, font=("", 16)).pack(side=tk.LEFT, padx=5)
        
        # File info
        info_frame = ttk.Frame(row)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        filename = os.path.basename(media['path'])
        ttk.Label(info_frame, text=filename, font=("", 10, "bold")).pack(anchor="w")
        
        # File details
        file_size = media.get('file_size', 0)
        if file_size > 1024*1024:
            size_text = f"{file_size/(1024*1024):.1f} MB"
        else:
            size_text = f"{file_size/1024:.0f} KB"
        
        details = f"{media.get('media_type', '').title()} • {size_text}"
        ttk.Label(info_frame, text=details, font=("", 9), foreground="gray").pack(anchor="w")
        
        # Action buttons
        button_frame = ttk.Frame(row)
        button_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="Apri", width=8,
                  command=lambda: self.open_media(media)).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Elimina", width=8,
                  command=lambda: self.delete_media(media)).pack(side=tk.LEFT, padx=2)
        
        return row
    
    def clear_media_display(self):
        """Clear media display"""
        for widget in self.media_frame.winfo_children():
            widget.destroy()
    
    def change_view_mode(self):
        """Change view mode"""
        self.apply_filter()
    
    def on_search_changed(self, event=None):
        """Handle search change"""
        # Debounce search
        if hasattr(self, 'search_timer'):
            self.window.after_cancel(self.search_timer)
        self.search_timer = self.window.after(500, self.apply_filter)
    
    def open_media(self, media):
        """Open media file"""
        try:
            import subprocess
            import platform
            
            file_path = media['path']
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            elif platform.system() == 'Windows':  # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
                
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il file: {e}")
    
    def delete_media(self, media):
        """Delete media file"""
        filename = os.path.basename(media['path'])
        if messagebox.askyesno("Conferma", f"Sei sicuro di voler eliminare '{filename}'?"):
            try:
                # Delete file
                os.remove(media['path'])
                
                # TODO: Remove from database
                
                # Refresh display
                self.refresh_media()
                
                messagebox.showinfo("Successo", "File eliminato con successo")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore eliminazione file: {e}")
    
    def export_archive(self):
        """Export media archive"""
        if not self.current_entity_type or not self.current_entity_id:
            messagebox.showwarning("Selezione", "Seleziona un'entità")
            return
            
        # Select output file
        filename = filedialog.asksaveasfilename(
            title="Salva archivio media",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")]
        )
        
        if filename:
            try:
                success = self.media_handler.create_media_archive(
                    self.current_entity_type, self.current_entity_id, filename)
                
                if success:
                    messagebox.showinfo("Successo", f"Archivio creato: {filename}")
                else:
                    messagebox.showerror("Errore", "Errore creazione archivio")
                    
            except Exception as e:
                messagebox.showerror("Errore", f"Errore esportazione: {e}")
    
    def close_window(self):
        """Close the window"""
        self.window.destroy()
    
    def run(self):
        """Run the media manager"""
        self.window.mainloop()
