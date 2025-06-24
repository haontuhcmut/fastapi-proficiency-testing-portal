from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi_pagination.ext.sqlmodel import apaginate
from fastapi_pagination import Page
from typing import Annotated
from fastapi_filter import FilterDepends
from fastapi_pagination import Params
from fastapi import Depends
from fastapi_pagination.ext.sqlmodel import apaginate

from app.db.model import PTScheme, Category
from app.pt_scheme.schema import CreatePTSchemeModel, PTSchemesFilter
from app.error import (
    PTSchemeAlreadyExist,
    InvalidIDFormat,
    CategoryNotFound,
    PTSChemeNotFound,
)


class PTSchemeService:
    async def get_all_pt_scheme(self, session: AsyncSession) -> Page[PTScheme]:
        statement = select(PTScheme).order_by(PTScheme.pt_scheme_code)
        return await apaginate(session, statement)

    async def get_scheme_item(self, scheme_id: str, session: AsyncSession):
        try:
            scheme_uuid = UUID(scheme_id)
        except ValueError:
            raise InvalidIDFormat()

        statement = (
            select(PTScheme, Category.name.label("category_name"))
            .join(Category, PTScheme.category_id == Category.id)
            .where(PTScheme.id == scheme_uuid)
        )
        result = await session.exec(statement)
        row = result.first()
        if row is None:
            return None
        scheme, category_name = row
        return scheme, category_name

    async def create_scheme(
        self, scheme_data: CreatePTSchemeModel, session: AsyncSession
    ):
        category = await session.get(Category, scheme_data.category_id)
        if category is None:
            CategoryNotFound()
        statement = select(PTScheme).where(
            PTScheme.pt_scheme_code == scheme_data.pt_scheme_code
        )
        result = await session.exec(statement)
        scheme = result.first()
        if scheme is not None:
            raise PTSchemeAlreadyExist()

        data_dict = scheme_data.model_dump()
        new_scheme = PTScheme(**data_dict)
        session.add(new_scheme)
        await session.commit()
        return new_scheme, category.name

    async def update_scheme(
        self, scheme_id: str, data_update: CreatePTSchemeModel, session: AsyncSession
    ):
        try:
            scheme_uuid = UUID(scheme_id)
        except ValueError:
            raise InvalidIDFormat()

        # uuid checking
        scheme = await session.get(PTScheme, scheme_uuid)
        if scheme is None:
            PTSChemeNotFound()

        category = await session.get(Category, data_update.category_id)
        if category is None:
            CategoryNotFound()

        # unique checking
        if scheme.pt_scheme_code != data_update.pt_scheme_code:
            existing_scheme = (
                await session.exec(
                    select(PTScheme).where(
                        PTScheme.pt_scheme_code == data_update.pt_scheme_code,
                        PTScheme.id != scheme_uuid,
                    )
                )
            ).first()
            if existing_scheme:
                raise PTSchemeAlreadyExist()
        for key, value in data_update.model_dump(exclude_unset=True).items():
            setattr(scheme, key, value)

        await session.commit()
        return scheme, category.name

    async def delete_scheme(self, scheme_id: str, session: AsyncSession):
        try:
            scheme_uuid = UUID(scheme_id)
        except ValueError:
            raise InvalidIDFormat()

        scheme_to_delete = await session.get(PTScheme, scheme_uuid)
        if scheme_to_delete is not None:
            await session.delete(scheme_to_delete)
            await session.commit()
            return scheme_to_delete
        return None

    async def pt_schemes_filter(
        self,
        pt_schemes_filter: Annotated[PTSchemesFilter, FilterDepends(PTSchemesFilter)],
        _params: Annotated[Params, Depends()],
        session: AsyncSession,
    ) -> Page[PTScheme]:
        statement = select(PTScheme).join(Category.name)
        filter_query = pt_schemes_filter.filter(statement)
        return await apaginate(session, filter_query, _params)  