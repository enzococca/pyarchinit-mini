"""
Media file handling and storage
"""

import os
import shutil
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import hashlib

class MediaHandler:
    """
    Handles media file operations, storage, and organization
    """
    
    def __init__(self, base_media_path: str = None):
        # Use centralized media directory by default
        if base_media_path is None:
            base_media_path = str(Path.home() / '.pyarchinit_mini' / 'media')

        self.base_media_path = Path(base_media_path)
        self.base_media_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for media types
        self.images_path = self.base_media_path / "images"
        self.documents_path = self.base_media_path / "documents"
        self.videos_path = self.base_media_path / "videos"
        self.models_path = self.base_media_path / "3d_models"
        self.thumbnails_path = self.base_media_path / "thumbnails"

        # Create subdirectories for system operations
        self.logs_path = self.base_media_path / "logs"
        self.backup_path = self.base_media_path / "backup"
        self.export_path = self.base_media_path / "export"

        for path in [self.images_path, self.documents_path, self.videos_path,
                     self.models_path, self.thumbnails_path, self.logs_path,
                     self.backup_path, self.export_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def store_file(self, file_path: str, entity_type: str, entity_id: int,
                   description: str = "", tags: str = "", author: str = "") -> Dict[str, Any]:
        """
        Store a media file and return metadata
        
        Args:
            file_path: Source file path
            entity_type: Type of entity (site, us, inventario)
            entity_id: Entity ID
            description: File description
            tags: Tags for the file
            author: Author/photographer
            
        Returns:
            Dictionary with file metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        source_path = Path(file_path)
        file_info = self._analyze_file(source_path)
        
        # Generate unique filename
        file_hash = self._calculate_file_hash(source_path)
        extension = source_path.suffix.lower()
        unique_filename = f"{entity_type}_{entity_id}_{file_hash[:8]}{extension}"
        
        # Determine storage location based on media type
        if file_info['media_type'] == 'image':
            target_dir = self.images_path
        elif file_info['media_type'] == 'document':
            target_dir = self.documents_path
        elif file_info['media_type'] == 'video':
            target_dir = self.videos_path
        elif file_info['media_type'] == '3d_model':
            target_dir = self.models_path
        else:
            target_dir = self.base_media_path / "other"
            target_dir.mkdir(exist_ok=True)
        
        # Create subdirectory for entity
        entity_dir = target_dir / f"{entity_type}_{entity_id}"
        entity_dir.mkdir(exist_ok=True)
        
        # Copy file
        target_path = entity_dir / unique_filename
        shutil.copy2(source_path, target_path)
        
        # Generate thumbnail for images
        thumbnail_path = None
        if file_info['media_type'] == 'image':
            thumbnail_path = self._generate_thumbnail(target_path, entity_type, entity_id)
        
        # Prepare metadata
        # ⚠️ IMPORTANT: Store RELATIVE path from base_media_path for web server compatibility
        # Web server serves media from /media/ route, so paths should be: media/images/...
        relative_path = target_path.relative_to(self.base_media_path.parent)

        metadata = {
            'media_name': source_path.name,
            'media_filename': unique_filename,
            'media_path': str(relative_path),  # Relative path: media/images/site_X/file.jpg
            'media_type': file_info['media_type'],
            'mime_type': file_info['mime_type'],
            'file_size': file_info['file_size'],
            'description': description,
            'tags': tags,
            'author': author,
            'width': file_info.get('width'),
            'height': file_info.get('height'),
            'entity_type': entity_type,
            'entity_id': entity_id,
            'thumbnail_path': str(thumbnail_path.relative_to(self.base_media_path.parent)) if thumbnail_path else None
        }

        return metadata
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file and extract metadata"""

        file_stat = file_path.stat()
        mime_type, _ = mimetypes.guess_type(str(file_path))

        info = {
            'file_size': file_stat.st_size,
            'mime_type': mime_type or 'application/octet-stream',
            'media_type': self._determine_media_type(mime_type, file_path)
        }

        # For images, get dimensions
        if info['media_type'] == 'image':
            try:
                with Image.open(file_path) as img:
                    info['width'] = img.width
                    info['height'] = img.height
            except Exception:
                pass

        return info
    
    def _determine_media_type(self, mime_type: str, file_path: Path = None) -> str:
        """Determine media type from MIME type and file extension"""

        # Check file extension for specific types (more reliable than MIME types)
        if file_path:
            ext = file_path.suffix.lower()
            # 3D models
            if ext in ['.obj', '.stl', '.ply', '.gltf', '.glb', '.dae']:
                return '3d_model'
            # Videos
            if ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.mpeg', '.mpg']:
                return 'video'
            # Spreadsheets
            if ext in ['.xlsx', '.xls', '.csv']:
                return 'spreadsheet'
            # Word documents
            if ext in ['.docx', '.doc']:
                return 'docx'

        if not mime_type:
            return 'unknown'

        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type.startswith('model/') or mime_type in [
            'application/sla',  # STL files
            'application/vnd.ms-pki.stl',  # STL files
            'application/ply',  # PLY files
            'model/gltf+json',  # glTF JSON
            'model/gltf-binary',  # glTF binary (GLB)
            'model/obj',  # OBJ files
            'model/stl',  # STL files
            'model/vnd.collada+xml'  # COLLADA
        ]:
            return '3d_model'
        elif mime_type in ['application/pdf', 'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'text/plain', 'text/html']:
            return 'document'
        else:
            return 'document'
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _generate_thumbnail(self, image_path: Path, entity_type: str, entity_id: int) -> Optional[Path]:
        """Generate thumbnail for image"""
        try:
            with Image.open(image_path) as img:
                # Create different thumbnail sizes
                sizes = [(150, 150), (300, 300), (600, 600)]
                thumbnail_paths = []
                
                for size in sizes:
                    # Calculate thumbnail size maintaining aspect ratio
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    
                    # Create thumbnail filename
                    size_name = f"{size[0]}x{size[1]}"
                    thumb_filename = f"thumb_{size_name}_{image_path.stem}.jpg"
                    thumb_path = self.thumbnails_path / f"{entity_type}_{entity_id}" / thumb_filename
                    
                    # Create directory
                    thumb_path.parent.mkdir(exist_ok=True)
                    
                    # Save thumbnail
                    img.save(thumb_path, "JPEG", quality=85)
                    thumbnail_paths.append(thumb_path)
                
                return thumbnail_paths[0] if thumbnail_paths else None
                
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
    
    def get_file_path(self, media_filename: str, entity_type: str, entity_id: int) -> Optional[Path]:
        """Get full path to stored media file"""
        
        # Search in appropriate directory
        search_dirs = [
            self.images_path / f"{entity_type}_{entity_id}",
            self.documents_path / f"{entity_type}_{entity_id}",
            self.videos_path / f"{entity_type}_{entity_id}",
            self.base_media_path / "other" / f"{entity_type}_{entity_id}"
        ]
        
        for search_dir in search_dirs:
            file_path = search_dir / media_filename
            if file_path.exists():
                return file_path
        
        return None
    
    def delete_file(self, media_filename: str, entity_type: str, entity_id: int) -> bool:
        """Delete media file and its thumbnails"""
        try:
            # Find and delete main file
            file_path = self.get_file_path(media_filename, entity_type, entity_id)
            if file_path and file_path.exists():
                os.remove(file_path)
            
            # Delete thumbnails
            thumb_dir = self.thumbnails_path / f"{entity_type}_{entity_id}"
            if thumb_dir.exists():
                for thumb_file in thumb_dir.glob(f"thumb_*_{Path(media_filename).stem}.*"):
                    os.remove(thumb_file)
            
            return True
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_media_info(self, file_path: Path) -> Dict[str, Any]:
        """Get detailed media information"""
        if not file_path.exists():
            return {}
        
        info = self._analyze_file(file_path)
        stat = file_path.stat()
        
        info.update({
            'filename': file_path.name,
            'created_date': stat.st_ctime,
            'modified_date': stat.st_mtime,
            'file_extension': file_path.suffix.lower()
        })
        
        return info
    
    def organize_media_by_entity(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """Get all media files for a specific entity"""
        
        entity_dirs = [
            self.images_path / f"{entity_type}_{entity_id}",
            self.documents_path / f"{entity_type}_{entity_id}",
            self.videos_path / f"{entity_type}_{entity_id}",
            self.base_media_path / "other" / f"{entity_type}_{entity_id}"
        ]
        
        media_files = []
        
        for entity_dir in entity_dirs:
            if entity_dir.exists():
                for file_path in entity_dir.iterdir():
                    if file_path.is_file():
                        info = self.get_media_info(file_path)
                        info['path'] = str(file_path)
                        media_files.append(info)
        
        return media_files
    
    def create_media_archive(self, entity_type: str, entity_id: int, 
                           archive_path: str) -> bool:
        """Create ZIP archive of all media for an entity"""
        try:
            import zipfile
            
            media_files = self.organize_media_by_entity(entity_type, entity_id)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for media_info in media_files:
                    file_path = media_info['path']
                    arcname = f"{entity_type}_{entity_id}/{Path(file_path).name}"
                    zipf.write(file_path, arcname)
            
            return True
            
        except Exception as e:
            print(f"Error creating archive: {e}")
            return False