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

import warnings

from sqlalchemy import types as sqltypes
from sqlalchemy.ext.mutable import Mutable


class MutableDict(Mutable, dict):
    """
    A mutable dictionary that tracks changes for SQLAlchemy.

    This class extends SQLAlchemy's `Mutable` and Python's `dict` to provide a
    dictionary that automatically tracks changes made to it or its nested
    dictionaries. It is designed to be used as a column type in SQLAlchemy models.
    Whenever a value is set, deleted, or mutated within the dictionary, the
    object will register a change event with SQLAlchemy, marking the parent object
    as 'dirty' and triggering an update when the session is committed.

    Example:
        ```
        from sqlalchemy import Column, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine

        Base = declarative_base()

        class User(Base):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            data = Column(MutableDict)

        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        user = User(data={'name': 'Alice', 'age': 30})
        session.add(user)
        session.commit()

        user.data['age'] = 31  # This change will be tracked
        session.commit()      # The user's data column will be updated
        ```

    Attributes:
        to_update (MutableDict): A reference to the root `MutableDict` object.
                                 Used for propagating change events up the hierarchy.
        _changed_keys (set): Keeps track of keys that have been changed.
        _deleted_keys (set): Keeps track of keys that have been deleted.
        _overwrite_key (str, optional): A key that overwrites the change detection.
    """

    @classmethod
    def coerce(cls, key, value):
        """
        Convert plain dictionaries to MutableDict.

        This method is called by SQLAlchemy's `Mutable` extension when a value
        is assigned to a column that uses `MutableDict`. It ensures that plain
        dictionaries are converted to `MutableDict` instances, enabling change
        tracking.

        Args:
            key (str): The key of the attribute being set (unused).
            value (dict): The value being assigned.

        Returns:
            MutableDict: If `value` is a dictionary, a new `MutableDict` instance
                         wrapping the dictionary. Otherwise, returns the original
                         `value` if it's already a `MutableDict`, or raises a ValueError.
        """
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __init__(self, initval=None, to_update=None, root_change_key=None):
        """
        Initialize a new MutableDict.

        Args:
            initval (dict, optional): Initial dictionary values. Defaults to {}.
            to_update (MutableDict, optional): The root MutableDict to update.
                                                Defaults to self.
            root_change_key (str, optional): Key that overwrites change detection.
        """
        initval = initval or {}
        self._changed_keys = set()
        self._deleted_keys = set()
        self._overwrite_key = root_change_key
        self.to_update = self if to_update is None else to_update
        for k in initval:
            initval[k] = self._convert_dict(
                initval[k], overwrite_key=k if self._overwrite_key is None else self._overwrite_key
            )
        dict.__init__(self, initval)

    def __setitem__(self, key, value):
        """
        Set an item in the dictionary.

        Wraps the dictionary's `__setitem__` method to track changes. If the
        value being set is a dictionary, it's converted to a `MutableDict`.

        Args:
            key (str): The key to set.
            value (any): The value to set.
        """
        value = self._convert_dict(
            value, key if self._overwrite_key is None else self._overwrite_key
        )
        dict.__setitem__(self, key, value)
        self.to_update.on_key_changed(
            key if self._overwrite_key is None else self._overwrite_key)

    def __delitem__(self, key):
        """
        Delete an item from the dictionary.

        Wraps the dictionary's `__delitem__` method to track changes.

        Args:
            key (str): The key to delete.
        """
        dict.__delitem__(self, key)
        # add the key to the deleted keys if this is the root object
        # otherwise update on root object
        if self._overwrite_key is None:
            self._deleted_keys.add(key)
            self.changed()
        else:
            self.to_update.on_key_changed(self._overwrite_key)

    def on_key_changed(self, key):
        """
        Mark a key as changed.

        This method is called when a nested `MutableDict` has a key changed.

        Args:
            key (str): The key that was changed.
        """
        self._deleted_keys.discard(key)
        self._changed_keys.add(key)
        self.changed()

    def _convert_dict(self, value, overwrite_key):
        """
        Convert a dictionary to a MutableDict.

        If the provided `value` is a dictionary, convert it to a
        `MutableDict`, linking it to the current `MutableDict` for change tracking.

        Args:
            value (dict): The value to convert.
            overwrite_key (str): key that overwrites change detection.

        Returns:
            MutableDict: A `MutableDict` instance if `value` was a dictionary,
                         otherwise the original `value`.
        """
        if isinstance(value, dict) and not isinstance(value, MutableDict):
            return MutableDict(value, self.to_update, overwrite_key)
        return value

    def __eq__(self, other):
        """
        Compare this MutableDict to another object.

        Args:
            other (any): Object to compare to.

        Returns:
            bool: True if dicts are equal.
        """
        return dict.__eq__(self, other)


class ObjectTypeImpl(sqltypes.UserDefinedType, sqltypes.JSON):
    """
    Implementation of the `ObjectType` for SQLAlchemy.

    This class defines the underlying SQL type and behavior for the `ObjectType`.
    It inherits from both `sqltypes.UserDefinedType` and `sqltypes.JSON`,
    allowing it to be used as a custom type and to leverage JSON serialization
    capabilities.

    Attributes:
        cache_ok (bool): Indicates whether instances of this type can be cached.
                         Set to `False` as mutability prevents reliable caching.
        none_as_null (bool): Determines if None values are stored as NULL in the database.
    """

    __visit_name__ = "OBJECT"

    cache_ok = False
    none_as_null = False


# Designated name to refer to. `Object` is too ambiguous.
ObjectType = MutableDict.as_mutable(ObjectTypeImpl)

# Backward-compatibility aliases.
_deprecated_Craty = ObjectType
_deprecated_Object = ObjectType

# https://www.lesinskis.com/deprecating-module-scope-variables.html
deprecated_names = ["Craty", "Object"]


def __getattr__(name):
    """
    Handle deprecated names for backward compatibility.

    This function intercepts attribute access and raises a `DeprecationWarning`
    if a deprecated name (`Craty` or `Object`) is used, redirecting the
    access to the `ObjectType`.

    Args:
        name (str): The name of the attribute being accessed.

    Returns:
        ObjectType: If the attribute is a deprecated name, returns `ObjectType`.

    Raises:
        AttributeError: If the attribute is not found and is not a deprecated name.
    """
    if name in deprecated_names:
        warnings.warn(
            f"{name} is deprecated and will be removed in future releases. "
            f"Please use ObjectType instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return globals()[f"_deprecated_{name}"]
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = deprecated_names + ["ObjectType"]
