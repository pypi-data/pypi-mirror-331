from enum import Enum
from typing import Any, override
from uuid import UUID

from sqlalchemy import Delete, Executable, Result, ScalarResult, Update, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, Session
from sqlalchemy.sql import Select

from archipy.adapters.orm.sqlalchemy.session_manager_adapters import AsyncSessionManagerAdapter, SessionManagerAdapter
from archipy.adapters.orm.sqlalchemy.ports import AnyExecuteParams, AsyncSqlAlchemyPort, SqlAlchemyPort
from archipy.configs.base_config import BaseConfig
from archipy.configs.config_template import SqlAlchemyConfig
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from archipy.models.entities import BaseEntity
from archipy.models.errors import InvalidEntityTypeError
from archipy.models.types.base_types import FilterOperationType
from archipy.models.types.sort_order_type import SortOrderType


class SqlAlchemyFilterMixin:
    """Mixin providing filtering capabilities for SQLAlchemy queries.

    This mixin provides methods to apply various filters to SQLAlchemy queries,
    supporting a wide range of comparison operators for different data types.

    The filtering functionality supports:
    - Equality/inequality comparisons
    - Greater than/less than operations
    - String operations (LIKE, ILIKE, startswith, endswith)
    - List operations (IN, NOT IN)
    - NULL checks

    Examples:
        >>> from sqlalchemy import select
        >>> from archipy.adapters.orm.sqlalchemy.adapters import SqlAlchemyFilterMixin
        >>> from archipy.models.types.base_types import FilterOperationType
        >>>
        >>> class UserRepository(SqlAlchemyFilterMixin):
        ...     def find_active_users_by_name(self, name_fragment):
        ...         query = select(User)
        ...         query = self._apply_filter(
        ...             query,
        ...             User.name,
        ...             name_fragment,
        ...             FilterOperationType.ILIKE
        ...         )
        ...         query = self._apply_filter(
        ...             query,
        ...             User.is_active,
        ...             True,
        ...             FilterOperationType.EQUAL
        ...         )
        ...         return query
    """

    @staticmethod
    def _apply_filter(
        query: Select | Update | Delete,
        field: InstrumentedAttribute,
        value: Any,
        operation: FilterOperationType,
    ) -> Select | Update | Delete:
        """Apply a filter to a SQLAlchemy query.

        This method applies different types of filters based on the specified
        operation type, allowing for flexible query building.

        Args:
            query: The SQLAlchemy query to apply the filter to
            field: The model attribute/column to filter on
            value: The value to compare against
            operation: The type of filter operation to apply

        Returns:
            The updated query with the filter applied

        Examples:
            >>> # Filter users with specific email domain
            >>> query = select(User)
            >>> query = SqlAlchemyFilterMixin._apply_filter(
            ...     query,
            ...     User.email,
            ...     "%@example.com",
            ...     FilterOperationType.LIKE
            ... )
            >>>
            >>> # Filter active users
            >>> query = SqlAlchemyFilterMixin._apply_filter(
            ...     query,
            ...     User.is_active,
            ...     True,
            ...     FilterOperationType.EQUAL
            ... )
            >>>
            >>> # Filter users created after a certain date
            >>> from datetime import datetime
            >>> cutoff_date = datetime(2023, 1, 1)
            >>> query = SqlAlchemyFilterMixin._apply_filter(
            ...     query,
            ...     User.created_at,
            ...     cutoff_date,
            ...     FilterOperationType.GREATER_THAN
            ... )
        """
        if value is not None or operation in [FilterOperationType.IS_NULL, FilterOperationType.IS_NOT_NULL]:
            if operation == FilterOperationType.EQUAL:
                return query.where(field == value)
            if operation == FilterOperationType.NOT_EQUAL:
                return query.where(field != value)
            if operation == FilterOperationType.LESS_THAN:
                return query.where(field < value)
            if operation == FilterOperationType.LESS_THAN_OR_EQUAL:
                return query.where(field <= value)
            if operation == FilterOperationType.GREATER_THAN:
                return query.where(field > value)
            if operation == FilterOperationType.GREATER_THAN_OR_EQUAL:
                return query.where(field >= value)
            if operation == FilterOperationType.IN_LIST:
                return query.where(field.in_(value))
            if operation == FilterOperationType.NOT_IN_LIST:
                return query.where(~field.in_(value))
            if operation == FilterOperationType.LIKE:
                return query.where(field.like(f"%{value}%"))
            if operation == FilterOperationType.ILIKE:
                return query.where(field.ilike(f"%{value}%"))
            if operation == FilterOperationType.STARTS_WITH:
                return query.where(field.startswith(value))
            if operation == FilterOperationType.ENDS_WITH:
                return query.where(field.endswith(value))
            if operation == FilterOperationType.CONTAINS:
                return query.where(field.contains(value))
            if operation == FilterOperationType.IS_NULL:
                return query.where(field.is_(None))
            if operation == FilterOperationType.IS_NOT_NULL:
                return query.where(field.isnot(None))
        return query


class SqlAlchemyPaginationMixin:
    @staticmethod
    def _apply_pagination(query: Select, pagination: PaginationDTO | None) -> Select:
        if pagination is None:
            return query
        return query.limit(pagination.page_size).offset(pagination.offset)


class SqlAlchemySortMixin:
    @staticmethod
    def _apply_sorting(entity: type[BaseEntity], query: Select, sort_info: SortDTO | None) -> Select:
        if sort_info is None:
            return query
        if isinstance(sort_info.column, str):
            sort_column = getattr(entity, sort_info.column)
        elif isinstance(sort_info.column, Enum):
            sort_column = getattr(entity, sort_info.column.name.lower())
        else:
            sort_column = sort_info.column

        if sort_info.order == SortOrderType.ASCENDING:
            return query.order_by(sort_column.asc())
        return query.order_by(sort_column.desc())


class SqlAlchemyAdapter(SqlAlchemyPort, SqlAlchemyPaginationMixin, SqlAlchemySortMixin):
    """Database adapter for SQLAlchemy ORM operations.

    This adapter provides a standardized interface for performing database operations
    using SQLAlchemy ORM. It implements common operations like create, read, update,
    delete (CRUD), along with advanced features for pagination, sorting, and filtering.

    Args:
        orm_config (SqlAlchemyConfig, optional): Configuration for SQLAlchemy.
            If None, retrieves from global config. Defaults to None.

    Examples:
        >>> from archipy.adapters.orm.sqlalchemy.adapters import SqlAlchemyAdapter
        >>> from archipy.models.entities import BaseEntity
        >>>
        >>> # Create adapter with default configuration
        >>> db = SqlAlchemyAdapter()
        >>>
        >>> # Create a new entity
        >>> user = User(name="John Doe", email="john@example.com")
        >>> db.create(user)
        >>>
        >>> # Query with sorting and pagination
        >>> from sqlalchemy import select
        >>> from archipy.models.dtos.pagination_dto import PaginationDTO
        >>> from archipy.models.dtos.sort_dto import SortDTO
        >>>
        >>> query = select(User)
        >>> pagination = PaginationDTO(page=1, page_size=10)
        >>> sort_info = SortDTO(column="created_at", order="DESC")
        >>> results, total = db.execute_search_query(User, query, pagination, sort_info)
    """

    def __init__(self, orm_config: SqlAlchemyConfig | None = None) -> None:
        configs: SqlAlchemyConfig = BaseConfig.global_config().SQLALCHEMY if orm_config is None else orm_config
        self.session_manager = SessionManagerAdapter(configs)

    @override
    def execute_search_query(
        self,
        entity: type[BaseEntity],
        query: Select,
        pagination: PaginationDTO | None = None,
        sort_info: SortDTO | None = SortDTO.default(),
    ) -> tuple[list[BaseEntity], int]:
        try:
            session = self.get_session()
            sorted_query = self._apply_sorting(entity, query, sort_info)
            paginated_query = self._apply_pagination(sorted_query, pagination)

            results = session.execute(paginated_query)
            results = results.scalars().all()

            count_query = select(func.count()).select_from(query.subquery())
            total_count = session.execute(count_query).scalar_one()
            return results, total_count
        except Exception as e:
            raise RuntimeError(f"Database query failed: {e!s}") from e

    @override
    def get_session(self) -> Session:
        return self.session_manager.get_session()

    @override
    def create(self, entity: BaseEntity) -> BaseEntity | None:
        """Creates a new entity in the database.

        Args:
            entity (BaseEntity): The entity to be created.

        Returns:
            BaseEntity | None: The created entity with updated attributes
                (e.g., generated ID), or None if creation failed.

        Raises:
            InvalidEntityTypeError: If the provided entity is not a BaseEntity.

        Examples:
            >>> user = User(name="John Doe", email="john@example.com")
            >>> created_user = db.create(user)
            >>> print(created_user.id)  # UUID is now populated
        """
        if not isinstance(entity, BaseEntity):
            raise InvalidEntityTypeError(entity, BaseEntity)
        session = self.get_session()
        session.add(entity)
        session.flush()
        return entity

    @override
    def bulk_create(self, entities: list[BaseEntity]) -> list[BaseEntity] | None:
        session = self.get_session()
        session.add_all(entities)
        session.flush()
        return entities

    @override
    def get_by_uuid(self, entity_type: type, entity_uuid: UUID):
        """Retrieves an entity by its UUID.

        Args:
            entity_type (type): The entity class to query.
            entity_uuid (UUID): The UUID of the entity to retrieve.

        Returns:
            Any: The retrieved entity or None if not found.

        Raises:
            InvalidEntityTypeError: If entity_type is not a subclass of BaseEntity
                or if entity_uuid is not a UUID.

        Examples:
            >>> from uuid import UUID
            >>> user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            >>> user = db.get_by_uuid(User, user_id)
            >>> if user:
            ...     print(user.name)
        """
        if not issubclass(entity_type, BaseEntity):
            raise InvalidEntityTypeError(entity_type, BaseEntity)
        if not isinstance(entity_uuid, UUID):
            raise InvalidEntityTypeError(entity_uuid, UUID)
        session = self.get_session()
        return session.get(entity_type, entity_uuid)

    @override
    def delete(self, entity: BaseEntity) -> None:
        if not isinstance(entity, BaseEntity):
            raise InvalidEntityTypeError(entity, BaseEntity)
        session = self.get_session()
        session.delete(entity)

    @override
    def bulk_delete(self, entities: list[BaseEntity]) -> None:
        for entity in entities:
            self.delete(entity)

    @override
    def execute(self, statement: Executable, params: AnyExecuteParams | None = None):
        session = self.get_session()
        return session.execute(statement, params)

    @override
    def scalars(self, statement: Executable, params: AnyExecuteParams | None = None):
        session = self.get_session()
        return session.scalars(statement, params)


class AsyncSqlAlchemyAdapter(AsyncSqlAlchemyPort, SqlAlchemyPaginationMixin, SqlAlchemySortMixin):
    """Asynchronous database adapter for SQLAlchemy ORM operations.

    This adapter provides an asynchronous interface for performing database operations
    using SQLAlchemy's async capabilities. It implements common operations like
    create, read, update, delete (CRUD), along with advanced features for pagination,
    sorting, and filtering.

    Args:
        orm_config (SqlAlchemyConfig, optional): Configuration for SQLAlchemy.
            If None, retrieves from global config. Defaults to None.

    Examples:
        >>> from archipy.adapters.orm.sqlalchemy.adapters import AsyncSqlAlchemyAdapter
        >>> from sqlalchemy import select
        >>> from archipy.models.dtos.pagination_dto import PaginationDTO
        >>>
        >>> # Create adapter with default configuration
        >>> db = AsyncSqlAlchemyAdapter()
        >>>
        >>> # Example async function using the adapter
        >>> async def get_users():
        ...     query = select(User)
        ...     pagination = PaginationDTO(page=1, page_size=10)
        ...     results, total = await db.execute_search_query(User, query, pagination)
        ...     return results
    """

    def __init__(self, orm_config: SqlAlchemyConfig | None = None) -> None:
        configs: SqlAlchemyConfig = BaseConfig.global_config().SQLALCHEMY if orm_config is None else orm_config
        self.session_manager = AsyncSessionManagerAdapter(configs)

    @override
    async def execute_search_query(
        self,
        entity: type[BaseEntity],
        query: Select,
        pagination: PaginationDTO | None,
        sort_info: SortDTO | None = SortDTO.default(),
    ) -> tuple[list[BaseEntity], int]:
        """Execute a search query with pagination and sorting.

        This method executes a SELECT query with pagination and sorting applied,
        and returns both the results and the total count of matching records.

        Args:
            entity: The entity class to query
            query: The SQLAlchemy SELECT query
            pagination: Pagination settings (page number and page size)
            sort_info: Sorting information (column and direction)

        Returns:
            A tuple containing:
                - List of entities matching the query
                - Total count of matching records (ignoring pagination)

        Raises:
            RuntimeError: If the database query fails

        Examples:
            >>> async def get_active_users(page: int = 1):
            ...     query = select(User).where(User.is_active == True)
            ...     pagination = PaginationDTO(page=page, page_size=20)
            ...     sort_info = SortDTO(column="created_at", order="DESC")
            ...     users, total = await db.execute_search_query(
            ...         User, query, pagination, sort_info
            ...     )
            ...     return users, total
        """
        try:
            session = self.get_session()
            sorted_query = self._apply_sorting(entity, query, sort_info)
            paginated_query = self._apply_pagination(sorted_query, pagination)

            results = await session.execute(paginated_query)
            results = results.scalars().all()

            count_query = select(func.count()).select_from(query.subquery())
            total_count = await session.execute(count_query)
            total_count = total_count.scalar_one()
            return results, total_count
        except Exception as e:
            raise RuntimeError(f"Database query failed: {e!s}") from e

    @override
    def get_session(self) -> AsyncSession:
        return self.session_manager.get_session()

    @override
    async def create(self, entity: BaseEntity) -> BaseEntity | None:
        if not isinstance(entity, BaseEntity):
            raise InvalidEntityTypeError(entity, BaseEntity)
        session: AsyncSession = self.get_session()
        session.add(entity)
        await session.flush()
        return entity

    @override
    async def bulk_create(self, entities: list[BaseEntity]) -> list[BaseEntity] | None:
        session = self.get_session()
        session.add_all(entities)
        await session.flush()
        return entities

    @override
    async def get_by_uuid(self, entity_type: type, entity_uuid: UUID) -> Any | None:
        if not issubclass(entity_type, BaseEntity):
            raise InvalidEntityTypeError(entity_type, BaseEntity)
        if not isinstance(entity_uuid, UUID):
            raise InvalidEntityTypeError(entity_uuid, UUID)
        session = self.get_session()
        return await session.get(entity_type, entity_uuid)

    @override
    async def delete(self, entity: BaseEntity) -> None:
        if not isinstance(entity, BaseEntity):
            raise InvalidEntityTypeError(entity, BaseEntity)
        session = self.get_session()
        await session.delete(entity)

    @override
    async def bulk_delete(self, entities: list[BaseEntity]) -> None:
        for entity in entities:
            await self.delete(entity)

    @override
    async def execute(self, statement: Executable, params: AnyExecuteParams | None = None) -> Result[Any]:
        session = self.get_session()
        return await session.execute(statement, params)

    @override
    async def scalars(self, statement: Executable, params: AnyExecuteParams | None = None) -> ScalarResult[Any]:
        session = self.get_session()
        return await session.scalars(statement, params)
