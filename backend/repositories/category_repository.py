from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.skill import Category

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.execute(select(Category).where(Category.id == category_id)).scalar_one_or_none()
