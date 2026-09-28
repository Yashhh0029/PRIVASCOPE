from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.user import User
from app.models.document import Document
from app.models.scan import Scan
from app.models.entity import DetectedEntity
from app.models.protection import ProtectionAction
from app.models.audit import AuditLog

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, name: str, email: str, password_hash: str, role: str = "user") -> User:
        user = User(name=name, email=email.lower(), password_hash=password_hash, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, original_filename: str, stored_filename: str,
               file_type: str, file_size: int, storage_path: str) -> Document:
        doc = Document(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type=file_type,
            file_size=file_size,
            storage_path=storage_path
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_id(self, doc_id: str, user_id: str) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == doc_id, Document.user_id == user_id).first()

    def list_by_user(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Document]:
        return self.db.query(Document).filter(Document.user_id == user_id).order_by(desc(Document.created_at)).offset(skip).limit(limit).all()

class ScanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, document_id: Optional[str] = None, stages_json: str = "[]", ocr_status: str = "OCR_NOT_REQUIRED") -> Scan:
        scan = Scan(
            user_id=user_id,
            document_id=document_id,
            status="pending",
            stages_json=stages_json,
            ocr_status=ocr_status
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        return scan

    def get_by_id(self, scan_id: str, user_id: Optional[str] = None) -> Optional[Scan]:
        query = self.db.query(Scan).filter(Scan.id == scan_id)
        if user_id:
            query = query.filter(Scan.user_id == user_id)
        return query.first()

    def list_by_user(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Scan]:
        return self.db.query(Scan).filter(Scan.user_id == user_id).order_by(desc(Scan.created_at)).offset(skip).limit(limit).all()

    def add_entity(self, scan_id: str, entity_type: str, confidence: float, risk_level: str,
                   masked_preview: str, page_number: int = 1, sheet_name: Optional[str] = None,
                   location_data: Optional[str] = None, detection_source: Optional[str] = None) -> DetectedEntity:
        entity = DetectedEntity(
            scan_id=scan_id,
            entity_type=entity_type,
            confidence=confidence,
            risk_level=risk_level,
            masked_preview=masked_preview,
            page_number=page_number,
            sheet_name=sheet_name,
            location_data=location_data,
            detection_source=detection_source
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

class ProtectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, scan_id: str, document_id: str, user_id: str, mode: str,
               output_path: str, output_filename: str, entities_protected: int,
               verification_passed: bool) -> ProtectionAction:
        action = ProtectionAction(
            scan_id=scan_id,
            document_id=document_id,
            user_id=user_id,
            mode=mode,
            output_path=output_path,
            output_filename=output_filename,
            entities_protected=entities_protected,
            verification_passed=verification_passed
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def get_by_id(self, action_id: str, user_id: str) -> Optional[ProtectionAction]:
        return self.db.query(ProtectionAction).filter(
            ProtectionAction.id == action_id,
            ProtectionAction.user_id == user_id
        ).first()

    def get_by_scan_id(self, scan_id: str, user_id: str) -> Optional[ProtectionAction]:
        return self.db.query(ProtectionAction).filter(
            ProtectionAction.scan_id == scan_id,
            ProtectionAction.user_id == user_id
        ).order_by(desc(ProtectionAction.created_at)).first()

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, user_id: str, action: str, status: str = "SUCCESS",
            document_id: Optional[str] = None, details: Optional[str] = None) -> AuditLog:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            status=status,
            document_id=document_id,
            details=details
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def list_by_user(self, user_id: str, skip: int = 0, limit: int = 50) -> List[AuditLog]:
        return self.db.query(AuditLog).filter(AuditLog.user_id == user_id).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
