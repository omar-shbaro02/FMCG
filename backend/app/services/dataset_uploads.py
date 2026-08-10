import hashlib
from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook

ALLOWED_TYPES = {
    ".csv": {"text/csv", "application/csv", "application/vnd.ms-excel"},
    ".xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
}


class UploadValidationError(ValueError):
    pass


class DuplicateDatasetError(ValueError):
    pass


@dataclass(frozen=True)
class StoredUpload:
    original_filename: str
    storage_path: str
    extension: str
    size_bytes: int
    sha256: str


class LocalDatasetStorage:
    def __init__(self, root: Path, max_bytes: int) -> None:
        self.root = root.resolve()
        self.max_bytes = max_bytes

    def store(self, filename: str, content_type: str | None, content: bytes) -> StoredUpload:
        safe_name = Path(filename).name
        extension = Path(safe_name).suffix.casefold()
        if safe_name != filename or not safe_name or extension not in ALLOWED_TYPES:
            raise UploadValidationError("Only simple CSV or XLSX filenames are accepted")
        if content_type not in ALLOWED_TYPES[extension]:
            raise UploadValidationError("File MIME type does not match its extension")
        if not content or len(content) > self.max_bytes:
            raise UploadValidationError("File is empty or exceeds the configured size limit")
        self._verify_content(extension, content)

        digest = hashlib.sha256(content).hexdigest()
        self.root.mkdir(parents=True, exist_ok=True)
        destination = (self.root / f"{digest}{extension}").resolve()
        if self.root not in destination.parents:
            raise UploadValidationError("Unsafe storage path")
        if destination.exists():
            raise DuplicateDatasetError("This exact file has already been uploaded")
        destination.write_bytes(content)
        return StoredUpload(safe_name, str(destination), extension, len(content), digest)

    @staticmethod
    def _verify_content(extension: str, content: bytes) -> None:
        if extension == ".csv":
            try:
                decoded = content.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise UploadValidationError("CSV must be UTF-8 encoded") from exc
            if "\n" not in decoded and "\r" not in decoded:
                raise UploadValidationError("CSV must contain a header and data rows")
        else:
            from io import BytesIO

            try:
                workbook = load_workbook(BytesIO(content), read_only=True, data_only=False)
                workbook.close()
            except Exception as exc:
                raise UploadValidationError("XLSX workbook is malformed") from exc
