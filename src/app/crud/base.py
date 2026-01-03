# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Any, Generic, List, Optional, Tuple, Type, TypeVar, Union, cast

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import desc, exc
from sqlmodel import SQLModel, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

__all__ = ["BaseCRUD"]


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]) -> None:
        self.session = session
        self.model = model

    async def create(self, payload: CreateSchemaType) -> ModelType:
        entry = self.model(**payload.model_dump())
        try:
            self.session.add(entry)
            await self.session.commit()
        except exc.IntegrityError as error:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An entry with the same index already exists : {error!s}",
            )
        await self.session.refresh(entry)

        return entry

    async def get(self, entry_id: int, strict: bool = False) -> Union[ModelType, None]:
        entry: Union[ModelType, None] = await self.session.get(self.model, entry_id)
        if strict and entry is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table {self.model.__name__} has no corresponding entry.",
            )
        return entry

    async def get_by(self, field_name: str, val: Union[str, int], strict: bool = False) -> Union[ModelType, None]:
        statement = select(self.model).where(getattr(self.model, field_name) == val)  # type: ignore[var-annotated]
        results = await self.session.exec(statement=statement)
        entry = results.one_or_none()
        if strict and entry is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table {self.model.__name__} has no corresponding entry.",
            )
        return entry

    async def fetch_all(
        self,
        filters: Union[Tuple[str, Any], List[Tuple[str, Any]], None] = None,
        in_pair: Union[Tuple[str, List], None] = None,
        inequality_pair: Optional[Tuple[str, str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[ModelType]:
        statement = select(self.model)  # type: ignore[var-annotated]
        if isinstance(filters, tuple):
            statement = statement.where(getattr(self.model, filters[0]) == filters[1])
        elif isinstance(filters, list):
            for filter_ in filters:
                statement = statement.where(getattr(self.model, filter_[0]) == filter_[1])

        if isinstance(in_pair, tuple):
            statement = statement.where(getattr(self.model, in_pair[0]).in_(in_pair[1]))

        if isinstance(inequality_pair, tuple):
            field, op, value = inequality_pair
            if op == ">=":
                statement = statement.where(getattr(self.model, field) >= value)
            elif op == ">":
                statement = statement.where(getattr(self.model, field) > value)
            elif op == "<=":
                statement = statement.where(getattr(self.model, field) <= value)
            elif op == "<":
                statement = statement.where(getattr(self.model, field) < value)
            else:
                raise ValueError(f"Unsupported inequality operator: {op}")

        if order_by is not None:
            statement = statement.order_by(
                desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)
            )

        if offset is not None:
            statement = statement.offset(offset)

        if limit is not None:
            statement = statement.limit(limit)

        result = await self.session.exec(statement=statement)
        return [r for r in result]

    async def update(self, entry_id: int, payload: UpdateSchemaType) -> ModelType:
        access = cast(ModelType, await self.get(entry_id, strict=True))
        values = payload.model_dump(exclude_unset=True)

        for k, v in values.items():
            setattr(access, k, v)

        self.session.add(access)
        await self.session.commit()
        await self.session.refresh(access)

        return access

    async def delete(self, entry_id: int) -> None:
        await self.get(entry_id, strict=True)
        statement = delete(self.model).where(self.model.id == entry_id)

        await self.session.exec(statement=statement)  # type: ignore[call-overload]
        await self.session.commit()

    async def get_in(self, list_: List[Any], field_name: str) -> List[ModelType]:
        statement = select(self.model).where(getattr(self.model, field_name).in_(list_))  # type: ignore[var-annotated]
        results = await self.session.exec(statement)
        return results.all()
