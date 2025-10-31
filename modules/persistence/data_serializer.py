import json
import pickle
from typing import Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import os


class DataSerializer:
    """Handles serialization and deserialization of simulation data."""

    def __init__(self, base_path: str = "data/saves"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def serialize_to_json(self, data: Any, filename: str, indent: int = 2) -> str:
        """Serialize data to JSON format.

        Args:
            data: Data to serialize
            filename: Output filename (without extension)
            indent: JSON indentation level

        Returns:
            Path to the saved file
        """
        filepath = self.base_path / f"{filename}.json"

        # Handle datetime objects
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=json_serializer)

        return str(filepath)

    def deserialize_from_json(self, filename: str) -> Any:
        """Deserialize data from JSON format.

        Args:
            filename: Filename to load (without extension)

        Returns:
            Deserialized data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        filepath = self.base_path / f"{filename}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"Save file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert ISO datetime strings back to datetime objects
        def convert_datetimes(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and self._is_iso_datetime(value):
                        try:
                            obj[key] = datetime.fromisoformat(value)
                        except ValueError:
                            pass  # Keep as string if not valid datetime
                    elif isinstance(value, (dict, list)):
                        convert_datetimes(value)
            elif isinstance(obj, list):
                for item in obj:
                    convert_datetimes(item)

        convert_datetimes(data)
        return data

    def serialize_to_pickle(self, data: Any, filename: str) -> str:
        """Serialize data to pickle format (for complex Python objects).

        Args:
            data: Data to serialize
            filename: Output filename (without extension)

        Returns:
            Path to the saved file
        """
        filepath = self.base_path / f"{filename}.pkl"

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

        return str(filepath)

    def deserialize_from_pickle(self, filename: str) -> Any:
        """Deserialize data from pickle format.

        Args:
            filename: Filename to load (without extension)

        Returns:
            Deserialized data

        Raises:
            FileNotFoundError: If file doesn't exist
            pickle.UnpicklingError: If pickle data is corrupted
        """
        filepath = self.base_path / f"{filename}.pkl"

        if not filepath.exists():
            raise FileNotFoundError(f"Save file not found: {filepath}")

        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        return data

    def list_save_files(self, extension: str = "json") -> list[str]:
        """List all save files with the specified extension.

        Args:
            extension: File extension to filter by (without dot)

        Returns:
            List of save file names (without extension)
        """
        pattern = f"*.{extension}"
        files = list(self.base_path.glob(pattern))
        return [f.stem for f in files]

    def delete_save_file(self, filename: str, extension: str = "json") -> bool:
        """Delete a save file.

        Args:
            filename: Filename to delete (without extension)
            extension: File extension

        Returns:
            True if file was deleted, False if it didn't exist
        """
        filepath = self.base_path / f"{filename}.{extension}"

        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def get_file_info(self, filename: str, extension: str = "json") -> Optional[Dict[str, Any]]:
        """Get information about a save file.

        Args:
            filename: Filename to check (without extension)
            extension: File extension

        Returns:
            Dictionary with file information, or None if file doesn't exist
        """
        filepath = self.base_path / f"{filename}.{extension}"

        if not filepath.exists():
            return None

        stat = filepath.stat()

        return {
            'filename': filename,
            'extension': extension,
            'size_bytes': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'created_time': datetime.fromtimestamp(stat.st_ctime)
        }

    def validate_save_data(self, data: Dict[str, Any], data_type: str) -> bool:
        """Validate save data structure.

        Args:
            data: Data to validate
            data_type: Type of data ("company", "market", "simulation")

        Returns:
            True if data is valid, False otherwise
        """
        if not isinstance(data, dict):
            return False

        required_fields = {
            'company': ['id', 'name', 'financial_data', 'operations_data'],
            'market': ['state', 'round_number'],
            'simulation': ['current_state', 'round_manager']
        }

        if data_type not in required_fields:
            return False

        for field in required_fields[data_type]:
            if field not in data:
                return False

        return True

    def _is_iso_datetime(self, string: str) -> bool:
        """Check if a string is in ISO datetime format."""
        try:
            datetime.fromisoformat(string)
            return True
        except ValueError:
            return False

    def export_data(self, data: Any, filename: str, format: str = "json") -> str:
        """Export data in the specified format.

        Args:
            data: Data to export
            filename: Output filename (without extension)
            format: Export format ("json" or "pickle")

        Returns:
            Path to the exported file
        """
        if format == "json":
            return self.serialize_to_json(data, filename)
        elif format == "pickle":
            return self.serialize_to_pickle(data, filename)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_data(self, filename: str, format: str = "json") -> Any:
        """Import data from the specified format.

        Args:
            filename: Filename to import (without extension)
            format: Import format ("json" or "pickle")

        Returns:
            Imported data
        """
        if format == "json":
            return self.deserialize_from_json(filename)
        elif format == "pickle":
            return self.deserialize_from_pickle(filename)
        else:
            raise ValueError(f"Unsupported import format: {format}")

    def create_backup(self, filename: str, extension: str = "json") -> str:
        """Create a backup of a save file.

        Args:
            filename: Filename to backup (without extension)
            extension: File extension

        Returns:
            Path to the backup file
        """
        original_path = self.base_path / f"{filename}.{extension}"
        if not original_path.exists():
            raise FileNotFoundError(f"Original file not found: {original_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename}_backup_{timestamp}.{extension}"
        backup_path = self.base_path / backup_filename

        # Copy file
        import shutil
        shutil.copy2(original_path, backup_path)

        return str(backup_path)