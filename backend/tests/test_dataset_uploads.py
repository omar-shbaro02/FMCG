from pathlib import Path

import pytest

from app.services.dataset_uploads import (
    DuplicateDatasetError,
    LocalDatasetStorage,
    UploadValidationError,
)

CSV = b"week_start_date,sku_id\n2026-01-05,SKU-1\n"


def test_csv_is_stored_under_content_hash(tmp_path: Path) -> None:
    result = LocalDatasetStorage(tmp_path, 1024).store("sales.csv", "text/csv", CSV)

    assert Path(result.storage_path).parent == tmp_path
    assert Path(result.storage_path).name == f"{result.sha256}.csv"
    assert Path(result.storage_path).read_bytes() == CSV


@pytest.mark.parametrize("filename", ["../sales.csv", "/tmp/sales.csv", "sales.exe"])
def test_unsafe_or_unsupported_filename_is_rejected(tmp_path: Path, filename: str) -> None:
    with pytest.raises(UploadValidationError):
        LocalDatasetStorage(tmp_path, 1024).store(filename, "text/csv", CSV)


def test_mime_mismatch_and_oversize_are_rejected(tmp_path: Path) -> None:
    storage = LocalDatasetStorage(tmp_path, 10)
    with pytest.raises(UploadValidationError):
        storage.store("sales.csv", "application/octet-stream", CSV)
    with pytest.raises(UploadValidationError):
        storage.store("sales.csv", "text/csv", CSV)


def test_exact_duplicate_is_explicitly_rejected(tmp_path: Path) -> None:
    storage = LocalDatasetStorage(tmp_path, 1024)
    storage.store("sales.csv", "text/csv", CSV)
    with pytest.raises(DuplicateDatasetError):
        storage.store("renamed.csv", "text/csv", CSV)
