from typing import List, Optional
from src.core.models import WorkType, get_all_work_types, get_work_type_by_id, get_work_types_by_category
from src.core.enums import WorkTypeCategory


class WorkTypeDAO:
    """DAO для работы с типами работ"""
    
    @staticmethod
    def get_all() -> List[WorkType]:
        """Получить все типы работ"""
        return get_all_work_types()
    
    @staticmethod
    def get_by_id(work_type_id: str) -> Optional[WorkType]:
        """Получить тип работы по ID"""
        return get_work_type_by_id(work_type_id)
    
    @staticmethod
    def get_by_category(category: WorkTypeCategory) -> List[WorkType]:
        """Получить типы работ по категории"""
        return get_work_types_by_category(category)
    
    @staticmethod
    def search_by_keywords(keywords: List[str]) -> List[WorkType]:
        """Поиск типов работ по ключевым словам"""
        results = []
        all_work_types = get_all_work_types()
        
        for work_type in all_work_types:
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if any(kw.lower() in keyword_lower or keyword_lower in kw.lower() 
                      for kw in work_type.keywords):
                    if work_type not in results:
                        results.append(work_type)
                    break
        
        return results
