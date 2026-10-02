from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models.skill import Category

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.execute(select(Category).where(Category.id == category_id)).scalar_one_or_none()

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.execute(select(Category).where(Category.name == name)).scalar_one_or_none()

    def list_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return list(self.db.execute(select(Category).offset(skip).limit(limit)).scalars().all())

    def create_category(self, category: Category) -> Category:
        try:
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            return category
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_category(self, category: Category) -> Category:
        try:
            self.db.commit()
            self.db.refresh(category)
            return category
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_category(self, category: Category) -> None:
        try:
            self.db.delete(category)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
