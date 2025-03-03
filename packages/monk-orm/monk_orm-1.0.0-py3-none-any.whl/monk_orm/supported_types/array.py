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

# ruff: noqa: A005  # Module `array` shadows a Python standard-library module

import sqlalchemy.types as sqltypes
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.sql import default_comparator, expression, operators


class MutableList(Mutable, list):
    """
    A mutable list class for use with SQLAlchemy.

    This class extends the built-in `list` class and integrates with SQLAlchemy's
    `Mutable` system to allow SQLAlchemy to track changes made to a list that is
    stored as a column in a database table.  Without this, SQLAlchemy wouldn't
    automatically know if the list's contents have changed, and wouldn't save the
    changes to the database.

    Example:
    ::
        from sqlalchemy import create_engine, Column, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy_utils import DatabaseURL
        from sqlalchemy.dialects.postgresql import JSONB
        from sqlalchemy import TypeDecorator
        import os

        # If you use other database, for example sqlite you should
        # inherit it from sqlalchemy.TypeDecorator
        # and sqlalchemy.types.TypeEngine

        # example for postgresql
        class JSONBType(TypeDecorator):
            impl = JSONB

            def __init__(self, *args, **kwargs):
                TypeDecorator.__init__(self, *args, **kwargs)

        Base = declarative_base()

        class SomeModel(Base):
            __tablename__ = 'some_model'

            id = Column(Integer, primary_key=True)
            # You can define ObjectArray and use it,
            # and the content will be tracked for changes and saved to the database
            data = Column(JSONBType, nullable=True)

    """

    @classmethod
    def coerce(cls, key, value):
        """
        Convert plain list to MutableList.

        This method is crucial for SQLAlchemy's `Mutable` system.  It's called
        when SQLAlchemy loads data from the database into an attribute that is
        defined using `MutableList`.

        Its main job is to ensure that the value being assigned to the attribute
        is a `MutableList` instance.

        Args:
            key: The key of the attribute being set (usually the column name).
            value: The value being assigned to the attribute.

        Returns:
            A `MutableList` instance, or `None` if the value is `None`.
        """
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            elif value is None:
                return value
            else:
                return MutableList([value])
        else:
            return value

    def __init__(self, initval=None):
        """
        Initializes a new MutableList instance.

        Args:
            initval: An optional initial value for the list.  Defaults to an empty list.
        """
        list.__init__(self, initval or [])

    def __setitem__(self, key, value):
        """
        Sets an item in the list.

        Overrides the list's `__setitem__` method (used when you assign a value to
        an element in the list, like `my_list[0] = 'new value'`).  After the item
        is set, it calls `self.changed()` to notify SQLAlchemy that the list has
        been modified.

        Args:
            key: The index of the item to set.
            value: The value to set.
        """
        list.__setitem__(self, key, value)
        self.changed()

    def __eq__(self, other):
        """
        Checks if the list is equal to another list.

        Args:
            other: The other list to compare to.

        Returns:
            True if the lists are equal, False otherwise.
        """
        return list.__eq__(self, other)

    def append(self, item):
        """
        Appends an item to the end of the list.

        Args:
            item: The item to append.
        """
        list.append(self, item)
        self.changed()

    def insert(self, idx, item):
        """
        Inserts an item at a given index.

        Args:
            idx: The index at which to insert the item.
            item: The item to insert.
        """
        list.insert(self, idx, item)
        self.changed()

    def extend(self, iterable):
        """
        Extends the list by appending elements from an iterable.

        Args:
            iterable: The iterable to extend the list with.
        """
        list.extend(self, iterable)
        self.changed()

    def pop(self, index=-1):
        """
        Removes and returns an element at a given index.

        Args:
            index: The index of the element to pop.  Defaults to the last element.

        Returns:
            The popped element.
        """
        list.pop(self, index)
        self.changed()

    def remove(self, item):
        """
        Removes the first occurrence of a value.

        Args:
            item: The item to remove.
        """
        list.remove(self, item)
        self.changed()


class Any(expression.ColumnElement):
    """
    Represents the clause ``left operator ANY (right)``.  ``right`` must be an array expression.

    This class is used to construct SQL expressions that check if a value exists
    within an array column. It's commonly used with databases like PostgreSQL
    that have native support for array types.

    .. seealso::

        :class:`sqlalchemy.dialects.postgresql.ARRAY`

        :meth:`sqlalchemy.dialects.postgresql.ARRAY.Comparator.any`
            ARRAY-bound method
    """

    __visit_name__ = "any"
    inherit_cache = True

    def __init__(self, left, right, operator=operators.eq):
        """
        Initializes a new Any instance.

        Args:
            left: The value you're searching for within the array.
            right: The array expression (usually a column in your table that stores an array).
            operator: The comparison operator to use (e.g., `operators.eq` for equals,
                `operators.lt` for less than).  Defaults to `operators.eq`.
        """
        self.type = sqltypes.Boolean()
        self.left = expression.literal(left)
        self.right = right
        self.operator = operator


class _ObjectArray(sqltypes.UserDefinedType):
    """
    A custom SQLAlchemy type for storing arrays (lists) of Python objects in a database column.

    This class handles how the array is stored and retrieved from the database.  It
    also defines custom comparison operations that can be performed on columns of
    this type.

    Example:
    ::
        from sqlalchemy import create_engine, Column, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy_utils import DatabaseURL
        from sqlalchemy.dialects.postgresql import JSONB
        from sqlalchemy import TypeDecorator
        import os

        # If you use other database, for example sqlite you should
        # inherit it from sqlalchemy.TypeDecorator
        # and sqlalchemy.types.TypeEngine

        # example for postgresql
        class JSONBType(TypeDecorator):
            impl = JSONB

            def __init__(self, *args, **kwargs):
                TypeDecorator.__init__(self, *args, **kwargs)

        Base = declarative_base()

        class SomeModel(Base):
            __tablename__ = 'some_model'

            id = Column(Integer, primary_key=True)
            # You can define ObjectArray and use it,
            # and the content will be tracked for changes and saved to the database
            data = Column(JSONBType, nullable=True)

    """

    cache_ok = True

    class Comparator(sqltypes.TypeEngine.Comparator):
        """
        A custom comparator class for `_ObjectArray` columns.

        This class defines custom comparison operations that can be performed on
        `_ObjectArray` columns, such as accessing elements within the array and
        checking if any element in the array satisfies a certain condition.
        """

        def __getitem__(self, key):
            """
            Allows you to access elements within the array column using the `[]` operator.

            Example:
            ::
                # Assuming 'table' is a SQLAlchemy table object and 'data' is a
                # column of type ObjectArray:
                table.c.data[0]  # Accesses the first element of the array.

            Args:
                key: The index of the element to access.

            Returns:
                An expression that represents accessing the element at the given index.
            """
            return default_comparator._binary_operate(self.expr, operators.getitem, key)

        def any(self, other, operator=operators.eq):
            """
            Returns ``other operator ANY (array)`` clause.

            Argument places are switched, because ANY requires array
            expression to be on the right hand-side.

            Example:
            ::
                from sqlalchemy.sql import operators

                # Assuming 'table' is a SQLAlchemy table object and 'data' is a
                # column of type ObjectArray:
                table.c.data.any(7, operator=operators.lt)  # Checks if any
                # element in the 'data' array is less than 7.

            Args:
                other: expression to be compared
                operator: an operator object from the
                 :mod:`sqlalchemy.sql.operators`
                 package, defaults to :func:`.operators.eq`.

            .. seealso::

                :class:`.postgresql.Any`

                :meth:`.postgresql.ARRAY.Comparator.all`

            Returns:
                An `Any` expression.
            """
            return Any(other, self.expr, operator=operator)

    type = MutableList
    """The Python type associated with this SQLAlchemy type."""

    comparator_factory = Comparator
    """The comparator class to use for this SQLAlchemy type."""

    def get_col_spec(self, **kws):
        """
        Returns a string that specifies the column type to be used when creating the table in the database.

        Returns:
            A string representing the column type (e.g., "ARRAY(OBJECT)").
        """
        return "ARRAY(OBJECT)"


ObjectArray = MutableList.as_mutable(_ObjectArray)
"""
A mutable SQLAlchemy type for storing arrays of Python objects.

This is the type you'll actually use when defining columns in your SQLAlchemy
models. It combines the features of `MutableList` and `_ObjectArray` to provide
change tracking and custom comparison operations.
"""
