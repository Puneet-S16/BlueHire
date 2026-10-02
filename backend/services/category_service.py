from typing import List
from models.skill import Category
from schemas.category import CategoryCreate, CategoryUpdate
from repositories.category_repository import CategoryRepository
from core.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError

class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def create_category(self, request: CategoryCreate) -> Category:
        if self.category_repo.get_by_name(request.name):
            raise CategoryAlreadyExistsError("Category with this name already exists")
            
        category = Category(**request.model_dump())
        return self.category_repo.create_category(category)

    def get_category(self, category_id: int) -> Category:
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError("Category not found")
        return category

    def list_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.category_repo.list_categories(skip=skip, limit=limit)

    def update_category(self, category_id: int, request: CategoryUpdate) -> Category:
        category = self.get_category(category_id)
        
        if request.name is not None and request.name != category.name:
            if self.category_repo.get_by_name(request.name):
                raise CategoryAlreadyExistsError("Category with this name already exists")
                
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)
            
        return self.category_repo.update_category(category)

    def delete_category(self, category_id: int) -> None:
        category = self.get_category(category_id)
        self.category_repo.delete_category(category)
