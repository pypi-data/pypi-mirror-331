# -*- coding: utf-8; -*-
#
# Licensed to MonkDB Labs Private Limited (MonkDB) under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  MonkDB licenses
# this file to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch

import sqlalchemy as sa

from monk_orm.sql_alchemy_version import SQL_ALCHEMY_2_0, SQL_ALCHEMY_VERSION

logger = logging.getLogger(__name__)


def insert_bulk(pd_table, conn, keys, data_iter):
    """
    Insert multiple rows into a MonkDB table using bulk operations.

    This function leverages MonkDB's "bulk operations" endpoint to efficiently 
    insert a large number of records into a specified table. It bypasses 
    SQLAlchemy's standard row-by-row insertion method by compiling the 
    insert statement and executing it directly with the raw DBAPI connection.

    Args:
        pd_table (SQLAlchemy Table): The SQLAlchemy table object representing 
                                      the target table in MonkDB.
        conn (Connection): The SQLAlchemy connection object to the MonkDB database.
        keys (list): A list of column names corresponding to the data being inserted.
        data_iter (iterable): An iterable yielding rows of data to be inserted 
                              (e.g., a list of tuples).

    Example:
        ```
        from sqlalchemy import create_engine, MetaData, Table

        # Create an engine and connect to MonkDB
        engine = create_engine('monkdb://user:password@host:port/dbname')
        connection = engine.connect()

        # Define your table
        metadata = MetaData(bind=engine)
        my_table = Table('my_table', metadata, autoload_with=engine)

        # Prepare data for bulk insert
        data_to_insert = [
            (1, 'Alice', 30),
            (2, 'Bob', 25),
            (3, 'Charlie', 35)
        ]

        # Insert using insert_bulk
        insert_bulk(my_table, connection, ['id', 'name', 'age'], data_to_insert)

        # Close the connection
        connection.close()
        ```

    Note:
        Ensure that the `data_iter` yields rows in the same order as specified in `keys`.
    """

    # Compile SQL statement and materialize batch.
    sql = str(pd_table.table.insert().compile(bind=conn))
    data = list(data_iter)

    # For debugging and tracing the batches running through this method.
    if logger.level == logging.DEBUG:
        logger.debug(f"Bulk SQL:     {sql}")
        logger.debug(f"Bulk records: {len(data)}")

    # Invoke bulk insert operation.
    cursor = conn._dbapi_connection.cursor()
    cursor.execute(sql=sql, bulk_parameters=data)
    cursor.close()


@contextmanager
def table_kwargs(**kwargs):
    """
    Context manager to add SQLAlchemy dialect-specific options at runtime.

    This context manager allows you to dynamically add options specific to 
    the MonkDB dialect when creating tables using SQLAlchemy. It is useful 
    in scenarios where you cannot directly pass these options during table 
    creation due to framework limitations.

    Args:
        **kwargs: Additional keyword arguments representing dialect-specific 
                  options for table creation.

    Example:
        ```
        from sqlalchemy import create_engine, MetaData, Table

        engine = create_engine('monkdb://user:password@host:port/dbname')

        with table_kwargs(monkey_option='value'):
            metadata = MetaData()
            my_table = Table('my_table', metadata,
                             sa.Column('id', sa.Integer(), primary_key=True),
                             sa.Column('name', sa.String()),
                             sa.Column('age', sa.Integer()))
            metadata.create_all(engine)  # This will apply the monkey_option

        # The created table will now include the specified dialect-specific options.
        ```

    Note:
        The context manager modifies the behavior of `sa.Table()` during its 
        execution. Ensure that any code creating tables is placed within this 
        context to apply your custom options.
    """

    if SQL_ALCHEMY_VERSION < SQL_ALCHEMY_2_0:
        _init_dist = sa.sql.schema.Table._init

        def _init(self, name, metadata, *args, **kwargs_effective):
            kwargs_effective.update(kwargs)
            return _init_dist(self, name, metadata, *args, **kwargs_effective)

        with patch("sqlalchemy.sql.schema.Table._init", _init):
            yield

    else:
        new_dist = sa.sql.schema.Table._new

        def _new(cls, *args: Any, **kw: Any) -> Any:
            kw.update(kwargs)
            table = new_dist(cls, *args, **kw)
            return table

        with patch("sqlalchemy.sql.schema.Table._new", _new):
            yield
