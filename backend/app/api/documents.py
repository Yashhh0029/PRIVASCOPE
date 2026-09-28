import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.document import Document
from app.models.audit import AuditLog
from app.schemas.scan import DocumentResponse
from app.api.deps import get_current_user
from app.processors.pdf_processor import PdfProcessor
from app.core.logger import logger

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validates uploaded document format, size, and saves securely with UUID filename.
    Logs audit trail for upload event.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected.")

    filename = Path(file.filename).name  # Strips directory traversal attempts
    ext = Path(filename).suffix.lower().lstrip(".")

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '.{ext}'. Supported formats: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}."
        )

    # Read and validate size
    contents = await file.read()
    file_size = len(contents)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty (0 bytes)."
        )

    # Validate binary magic bytes / signatures to prevent extension spoofing
    from app.core.file_validator import validate_file_signature, FileValidationError
    try:
        validate_file_signature(contents, filename)
    except FileValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security rejection: {str(e)}"
        )

    # Save to storage with non-colliding UUID
    stored_name = f"{uuid.uuid4().hex}_{filename}"
    storage_path = settings.UPLOADS_DIR / stored_name

    with open(storage_path, "wb") as f:
        f.write(contents)

    # Record in database
    doc = Document(
        user_id=current_user.id,
        original_filename=filename,
        stored_filename=stored_name,
        file_type=ext,
        file_size=file_size,
        storage_path=str(storage_path),
        status="uploaded"
    )
    db.add(doc)

    # Log audit event
    audit = AuditLog(
        user_id=current_user.id,
        document_id=doc.id,
        action="DOCUMENT_UPLOADED",
        status="SUCCESS",
        details=f"Uploaded '{filename}' ({round(file_size/1024, 1)} KB)"
    )
    db.add(audit)
    db.commit()
    db.refresh(doc)

    logger.info(f"Document {doc.id} uploaded by {current_user.email}: {filename}")
    return DocumentResponse.model_validate(doc)

@router.get("/{doc_id}/preview")
def get_document_preview(
    doc_id: str,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Renders document preview securely with strict ownership check.
    For PDF, renders page as high-res PNG pixmap for client visualization.
    """
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    path = Path(doc.storage_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file missing.")

    if doc.file_type == "pdf":
        pdf_proc = PdfProcessor()
        png_bytes = pdf_proc.render_page_preview(path, page_num=page)
        if png_bytes:
            return Response(content=png_bytes, media_type="image/png")
        return FileResponse(path, media_type="application/pdf")
    elif doc.file_type in ("png", "jpg", "jpeg"):
        media_type = f"image/{'jpeg' if doc.file_type in ('jpg', 'jpeg') else 'png'}"
        return FileResponse(path, media_type=media_type)
    else:
        # For text / csv / excel / docx
        return FileResponse(path, filename=doc.original_filename)
