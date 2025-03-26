from typing import Optional, Dict, Any, List, Union
import asyncio

import asyncpg

from config import config


class AsyncBaseDAO:
    model_table: str = None
    pk_column: str = "id"  # primary key column name

    # connection pool to be initialized at application startup
    _pool: asyncpg.pool.Pool = None

    @classmethod
    async def initialize_pool(cls, dsn: str, **pool_kwargs):
        """Initialize the connection pool (call once at app startup)"""
        cls._pool = await asyncpg.create_pool(dsn, **pool_kwargs)

    @classmethod
    async def close_pool(cls):
        """Close the connection pool (call at app shutdown)"""
        await cls._pool.close()

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int) -> Optional[Dict[str, Any]]:
        async with cls._pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT * FROM {cls.model_table} WHERE {cls.pk_column} = $1",
                data_id
            )
            return dict(row) if row else None

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> Optional[Dict[str, Any]]:
        if not filter_by:
            raise ValueError("At least one filter condition must be provided")

        async with cls._pool.acquire() as conn:
            conditions = " AND ".join([f"{k} = ${i + 1}" for i, k in enumerate(filter_by.keys())])
            values = list(filter_by.values())

            row = await conn.fetchrow(
                f"SELECT * FROM {cls.model_table} WHERE {conditions}",
                *values
            )
            return dict(row) if row else None

    @classmethod
    async def find_all(cls, **filter_by) -> List[Dict[str, Any]]:
        async with cls._pool.acquire() as conn:
            if filter_by:
                conditions = " AND ".join([f"{k} = ${i + 1}" for i, k in enumerate(filter_by.keys())])
                values = list(filter_by.values())
                query = f"SELECT * FROM {cls.model_table} WHERE {conditions}"
            else:
                query = f"SELECT * FROM {cls.model_table}"
                values = []

            rows = await conn.fetch(query, *values)
            return [dict(row) for row in rows]

    @classmethod
    async def add(cls, **values) -> Dict[str, Any]:
        if not values:
            raise ValueError("At least one value must be provided")

        async with cls._pool.acquire() as conn:
            columns = ", ".join(values.keys())
            placeholders = ", ".join([f"${i + 1}" for i in range(len(values))])
            returning_cols = ", ".join(values.keys())

            row = await conn.fetchrow(
                f"INSERT INTO {cls.model_table} ({columns}) "
                f"VALUES ({placeholders}) "
                f"RETURNING {returning_cols}",
                *values.values()
            )
            return dict(row)

    @classmethod
    async def update(cls, data_id: Union[int, str], **values) -> Optional[Dict[str, Any]]:
        """Update record by ID and return the updated record"""
        if not values:
            raise ValueError("At least one value must be provided for update")

        async with cls._pool.acquire() as conn:
            set_clause = ", ".join([f"{k} = ${i + 1}" for i, k in enumerate(values.keys())])
            values_list = list(values.values())

            row = await conn.fetchrow(
                f"UPDATE {cls.model_table} "
                f"SET {set_clause} "
                f"WHERE {cls.pk_column} = ${len(values_list) + 1} "
                f"RETURNING *",
                *values_list, data_id
            )
            return dict(row) if row else None

    @classmethod
    async def delete(cls, data_id: Union[int, str]) -> bool:
        """Delete record by ID, returns True if any row was affected"""
        async with cls._pool.acquire() as conn:
            result = await conn.execute(
                f"DELETE FROM {cls.model_table} WHERE {cls.pk_column} = $1",
                data_id
            )
            return "DELETE 1" in result

class UserDAO(AsyncBaseDAO):
    model_table = "users"
    pk_column = "user_id"


if __name__ == '__main__':
    async def example():
        # at app startup
        dsn = f"postgresql://{config.user}:{config.password}@{config.host}:{config.port}/{config.dbname}"
        await UserDAO.initialize_pool(dsn)

        # example
        users = await UserDAO.find_all()
        for u in users:
            print(u)
        await UserDAO.close_pool()


    asyncio.run(example())
