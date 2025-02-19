from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from typing import List, Optional, Dict, Any
from . import models

class CRUDBase:
    def __init__(self, model):
        self.model = model

class ScreenshotCRUD(CRUDBase):
    def __init__(self):
        super().__init__(models.Screenshot)

    def create(self, db: Session, *, data: Dict[str, Any]) -> models.Screenshot:
        db_obj = self.model(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[models.Screenshot]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_path(self, db: Session, file_path: str) -> Optional[models.Screenshot]:
        return db.query(self.model).filter(self.model.file_path == file_path).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "timestamp"
    ) -> List[models.Screenshot]:
        return db.query(self.model)\
            .order_by(getattr(self.model, order_by).desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def search(
        self,
        db: Session,
        *,
        query: str,
        app_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        is_favorite: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Screenshot]:
        search_query = db.query(self.model)

        if query:
            search_query = search_query.filter(
                or_(
                    self.model.extracted_text.ilike(f"%{query}%"),
                    self.model.window_title.ilike(f"%{query}%"),
                    self.model.notes.ilike(f"%{query}%")
                )
            )

        if app_name:
            search_query = search_query.filter(self.model.app_name == app_name)

        if start_date:
            search_query = search_query.filter(self.model.timestamp >= start_date)

        if end_date:
            search_query = search_query.filter(self.model.timestamp <= end_date)

        if tags:
            search_query = search_query.filter(
                self.model.tags.any(models.Tag.name.in_(tags))
            )

        if is_favorite is not None:
            search_query = search_query.filter(self.model.is_favorite == is_favorite)

        return search_query.order_by(self.model.timestamp.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def update(
        self,
        db: Session,
        *,
        db_obj: models.Screenshot,
        obj_in: Dict[str, Any]
    ) -> models.Screenshot:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> bool:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

class TagCRUD(CRUDBase):
    def __init__(self):
        super().__init__(models.Tag)

    def create(self, db: Session, *, name: str, is_auto_generated: bool = False) -> models.Tag:
        db_obj = self.model(name=name, is_auto_generated=is_auto_generated)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[models.Tag]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[models.Tag]:
        return db.query(self.model).filter(self.model.name == name).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Tag]:
        return db.query(self.model)\
            .order_by(self.model.name)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_or_create(self, db: Session, *, name: str, is_auto_generated: bool = False) -> models.Tag:
        tag = self.get_by_name(db, name=name)
        if not tag:
            tag = self.create(db, name=name, is_auto_generated=is_auto_generated)
        return tag

    def add_tag_to_screenshot(
        self,
        db: Session,
        *,
        screenshot_id: int,
        tag_name: str,
        is_auto_generated: bool = False
    ) -> Optional[models.Screenshot]:
        screenshot = db.query(models.Screenshot).get(screenshot_id)
        if not screenshot:
            return None

        tag = self.get_or_create(db, name=tag_name, is_auto_generated=is_auto_generated)
        if tag not in screenshot.tags:
            screenshot.tags.append(tag)
            db.commit()
            db.refresh(screenshot)

        return screenshot

    def remove_tag_from_screenshot(
        self,
        db: Session,
        *,
        screenshot_id: int,
        tag_name: str
    ) -> Optional[models.Screenshot]:
        screenshot = db.query(models.Screenshot).get(screenshot_id)
        if not screenshot:
            return None

        tag = self.get_by_name(db, name=tag_name)
        if tag and tag in screenshot.tags:
            screenshot.tags.remove(tag)
            db.commit()
            db.refresh(screenshot)

        return screenshot

    def delete(self, db: Session, *, id: int) -> bool:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

# Create CRUD instances
screenshot_crud = ScreenshotCRUD()
tag_crud = TagCRUD()
