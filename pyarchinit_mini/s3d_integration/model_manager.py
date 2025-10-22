"""
3D Model Manager - Handle 3D models (GLB/GLTF) for archaeological contexts
"""

import os
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path


class Model3DManager:
    """Manage 3D models for archaeological contexts"""

    # Supported 3D model formats
    SUPPORTED_FORMATS = {
        '.glb': 'model/gltf-binary',
        '.gltf': 'model/gltf+json',
        '.obj': 'model/obj',
        '.ply': 'application/ply',
        '.stl': 'model/stl',
        '.fbx': 'application/fbx',
    }

    def __init__(self, storage_path: str):
        """
        Initialize 3D Model Manager

        Args:
            storage_path: Base directory for storing 3D models
        """
        self.storage_path = Path(storage_path)
        self.models_dir = self.storage_path / '3d_models'
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def is_3d_model(self, filename: str) -> bool:
        """
        Check if file is a supported 3D model format

        Args:
            filename: Name of the file

        Returns:
            True if file is a 3D model, False otherwise
        """
        ext = Path(filename).suffix.lower()
        return ext in self.SUPPORTED_FORMATS

    def get_model_mime_type(self, filename: str) -> Optional[str]:
        """
        Get MIME type for 3D model file

        Args:
            filename: Name of the file

        Returns:
            MIME type or None if not a 3D model
        """
        ext = Path(filename).suffix.lower()
        return self.SUPPORTED_FORMATS.get(ext)

    def save_model(self, file_path: str, us_id: Optional[str] = None,
                  site_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Save 3D model to storage

        Args:
            file_path: Path to the model file
            us_id: Optional US identifier
            site_name: Optional site name

        Returns:
            Dictionary with model metadata
        """
        source_path = Path(file_path)

        if not source_path.exists():
            raise FileNotFoundError(f"Model file not found: {file_path}")

        if not self.is_3d_model(source_path.name):
            raise ValueError(f"Unsupported 3D model format: {source_path.suffix}")

        # Create subdirectory structure
        if site_name:
            target_dir = self.models_dir / site_name
        else:
            target_dir = self.models_dir / 'uncategorized'

        if us_id:
            target_dir = target_dir / f"US_{us_id}"

        target_dir.mkdir(parents=True, exist_ok=True)

        # Copy model file
        target_path = target_dir / source_path.name
        shutil.copy2(source_path, target_path)

        # Return metadata
        return {
            "filename": source_path.name,
            "path": str(target_path.relative_to(self.storage_path)),
            "absolute_path": str(target_path),
            "size": target_path.stat().st_size,
            "format": source_path.suffix.lower(),
            "mime_type": self.get_model_mime_type(source_path.name),
            "us_id": us_id,
            "site": site_name,
        }

    def get_models_for_us(self, us_id: str, site_name: str) -> List[Dict[str, Any]]:
        """
        Get all 3D models for a specific US

        Args:
            us_id: US identifier
            site_name: Site name

        Returns:
            List of model metadata dictionaries
        """
        us_dir = self.models_dir / site_name / f"US_{us_id}"

        if not us_dir.exists():
            return []

        models = []
        for model_file in us_dir.iterdir():
            if model_file.is_file() and self.is_3d_model(model_file.name):
                models.append({
                    "filename": model_file.name,
                    "path": str(model_file.relative_to(self.storage_path)),
                    "absolute_path": str(model_file),
                    "size": model_file.stat().st_size,
                    "format": model_file.suffix.lower(),
                    "mime_type": self.get_model_mime_type(model_file.name),
                    "us_id": us_id,
                    "site": site_name,
                })

        return models

    def get_models_for_site(self, site_name: str) -> List[Dict[str, Any]]:
        """
        Get all 3D models for a specific site

        Args:
            site_name: Site name

        Returns:
            List of model metadata dictionaries
        """
        site_dir = self.models_dir / site_name

        if not site_dir.exists():
            return []

        models = []

        # Iterate through all subdirectories and files
        for item in site_dir.iterdir():
            if item.is_dir():
                # Check if it's a US directory
                if item.name.startswith('US_'):
                    us_id = item.name.replace('US_', '')

                    for model_file in item.iterdir():
                        if model_file.is_file() and self.is_3d_model(model_file.name):
                            models.append({
                                "name": f"{model_file.name} (US {us_id})",
                                "filename": model_file.name,
                                "path": str(model_file.relative_to(self.storage_path)),
                                "absolute_path": str(model_file),
                                "size": model_file.stat().st_size,
                                "format": model_file.suffix.lower(),
                                "mime_type": self.get_model_mime_type(model_file.name),
                                "us_id": us_id,
                                "site": site_name,
                            })
                else:
                    # It's a site-level directory (like "site")
                    for model_file in item.iterdir():
                        if model_file.is_file() and self.is_3d_model(model_file.name):
                            models.append({
                                "name": f"{model_file.name} (Site)",
                                "filename": model_file.name,
                                "path": str(model_file.relative_to(self.storage_path)),
                                "absolute_path": str(model_file),
                                "size": model_file.stat().st_size,
                                "format": model_file.suffix.lower(),
                                "mime_type": self.get_model_mime_type(model_file.name),
                                "us_id": None,
                                "site": site_name,
                            })

        return models

    def delete_model(self, model_path: str) -> bool:
        """
        Delete a 3D model

        Args:
            model_path: Relative or absolute path to the model

        Returns:
            True if deleted successfully, False otherwise
        """
        # Convert to absolute path if relative
        if not Path(model_path).is_absolute():
            model_path = self.storage_path / model_path

        model_file = Path(model_path)

        if model_file.exists() and model_file.is_file():
            model_file.unlink()
            return True

        return False

    def get_viewer_url(self, model_path: str) -> str:
        """
        Get URL for 3D model viewer

        Args:
            model_path: Path to the model

        Returns:
            URL to view the model in web interface
        """
        # Convert to relative path
        if Path(model_path).is_absolute():
            relative_path = Path(model_path).relative_to(self.storage_path)
        else:
            relative_path = model_path

        return f"/3d-viewer/{relative_path}"
