from drive.files import PDF_MIME_TYPE, DriveFile


def test_drive_file_recognizes_pdf_by_mime_type():
    pdf = DriveFile(
        file_id="1",
        name="Factura.PDF",
        mime_type=PDF_MIME_TYPE,
    )
    folder = DriveFile(
        file_id="2",
        name="Subcarpeta",
        mime_type="application/vnd.google-apps.folder",
    )

    assert pdf.is_pdf is True
    assert folder.is_pdf is False
