"""
Base repository with common CRUD operations.
"""
from typing import Generic, TypeVar, Type, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import logging

from src.core.database import Base
from src.core.exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository for CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        """Initialize repository with model class.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def create(self, db: Session, **kwargs) -> ModelType:
        """Create a new record.

        Args:
            db: Database session
            **kwargs: Model field values

        Returns:
            Created model instance

        Raises:
            DatabaseError: If creation fails
        """
        try:
            instance = self.model(**kwargs)
            db.add(instance)
            db.flush()
            db.refresh(instance)
            logger.debug(f"Created {self.model.__name__} with id={instance.id}")
            return instance
        except Exception as e:
            logger.error(f"Failed to create {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to create record: {str(e)}")

    def get_by_id(self, db: Session, id: int) -> Optional[ModelType]:
        """Get record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            logger.error(f"Failed to get {self.model.__name__} by id={id}: {e}")
            raise DatabaseError(f"Failed to retrieve record: {str(e)}")

    def get_by_id_or_fail(self, db: Session, id: int) -> ModelType:
        """Get record by ID or raise exception.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance

        Raises:
            NotFoundError: If record not found
        """
        instance = self.get_by_id(db, id)
        if not instance:
            raise NotFoundError(f"{self.model.__name__} with id={id} not found")
        return instance

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "id",
        order_desc: bool = False,
    ) -> List[ModelType]:
        """Get all records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_desc: Order descending if True

        Returns:
            List of model instances
        """
        try:
            query = db.query(self.model)

            # Apply ordering
            if hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))

            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get all {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to retrieve records: {str(e)}")

    def count(self, db: Session, **filters) -> int:
        """Count records matching filters.

        Args:
            db: Database session
            **filters: Filter conditions

        Returns:
            Count of matching records
        """
        try:
            query = db.query(self.model)
            if filters:
                query = query.filter_by(**filters)
            return query.count()
        except Exception as e:
            logger.error(f"Failed to count {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to count records: {str(e)}")

    def update(self, db: Session, id: int, **kwargs) -> ModelType:
        """Update a record.

        Args:
            db: Database session
            id: Record ID
            **kwargs: Fields to update

        Returns:
            Updated model instance

        Raises:
            NotFoundError: If record not found
            DatabaseError: If update fails
        """
        try:
            instance = self.get_by_id_or_fail(db, id)

            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            db.flush()
            db.refresh(instance)
            logger.debug(f"Updated {self.model.__name__} with id={id}")
            return instance
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update {self.model.__name__} id={id}: {e}")
            raise DatabaseError(f"Failed to update record: {str(e)}")

    def delete(self, db: Session, id: int) -> bool:
        """Delete a record.

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if deleted, False otherwise

        Raises:
            NotFoundError: If record not found
            DatabaseError: If deletion fails
        """
        try:
            instance = self.get_by_id_or_fail(db, id)
            db.delete(instance)
            db.flush()
            logger.debug(f"Deleted {self.model.__name__} with id={id}")
            return True
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete {self.model.__name__} id={id}: {e}")
            raise DatabaseError(f"Failed to delete record: {str(e)}")

    def exists(self, db: Session, **filters) -> bool:
        """Check if record exists matching filters.

        Args:
            db: Database session
            **filters: Filter conditions

        Returns:
            True if exists, False otherwise
        """
        try:
            return db.query(self.model).filter_by(**filters).first() is not None
        except Exception as e:
            logger.error(f"Failed to check existence for {self.model.__name__}: {e}")
            return False

    def find_one(self, db: Session, **filters) -> Optional[ModelType]:
        """Find one record matching filters.

        Args:
            db: Database session
            **filters: Filter conditions

        Returns:
            Model instance or None
        """
        try:
            return db.query(self.model).filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Failed to find {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to find record: {str(e)}")

    def find_all(self, db: Session, **filters) -> List[ModelType]:
        """Find all records matching filters.

        Args:
            db: Database session
            **filters: Filter conditions

        Returns:
            List of model instances
        """
        try:
            return db.query(self.model).filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Failed to find {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to find records: {str(e)}")
