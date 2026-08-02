"""Herramientas compartidas para almacenamiento seguro."""

from storage.duplicates import (
    FileMoveResult,
    find_identical_file,
    safe_archive_file,
    sha256_bytes,
    sha256_file,
)
from storage.invoice_duplicates import (
    DuplicateCleanupResult,
    InvoiceMoveResult,
    cleanup_exact_invoice_duplicates,
    find_exact_invoice_duplicates,
    fiscal_key_from_filename,
    safe_move_invoice,
)

__all__ = [
    "DuplicateCleanupResult",
    "FileMoveResult",
    "InvoiceMoveResult",
    "cleanup_exact_invoice_duplicates",
    "find_exact_invoice_duplicates",
    "find_identical_file",
    "fiscal_key_from_filename",
    "safe_archive_file",
    "safe_move_invoice",
    "sha256_bytes",
    "sha256_file",
]

from storage.invoice_date_audit import (
    InvoiceDateAuditResult,
    audit_organized_invoice_dates,
    build_corrected_path,
)
