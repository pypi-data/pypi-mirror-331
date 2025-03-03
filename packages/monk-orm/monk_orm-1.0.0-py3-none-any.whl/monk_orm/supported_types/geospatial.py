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

import geojson
from sqlalchemy import types as sqltypes
from sqlalchemy.sql import default_comparator, operators


class Geopoint(sqltypes.UserDefinedType):
    """
    A custom SQLAlchemy type for representing geographic points using GeoJSON.

    This class allows you to store and retrieve geographic points in a SQL database.
    The points are represented as GeoJSON `Point` objects and are stored in the database
    as coordinates.

    Example:
        To use the Geopoint type in a SQLAlchemy model:

        ```
        from sqlalchemy import Column, Integer, create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        Base = declarative_base()

        class Location(Base):
            __tablename__ = 'locations'
            id = Column(Integer, primary_key=True)
            coordinates = Column(Geopoint)

        # Create an SQLite database in memory
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)

        # Create a new session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Add a new location with GeoJSON Point
        point = geojson.Point((102.0, 0.5))
        new_location = Location(coordinates=point)
        session.add(new_location)
        session.commit()
        ```

    Attributes:
        cache_ok (bool): Indicates whether instances of this type can be cached.

    Methods:
        get_col_spec() -> str: Returns the SQL representation of the column type.
        bind_processor(dialect) -> callable: Returns a function to process values before binding to the database.
        result_processor(dialect, coltype) -> callable: Returns a function to process results after retrieval from the database.
    """

    cache_ok = True

    class Comparator(sqltypes.TypeEngine.Comparator):
        """
        A custom comparator for the Geopoint type that allows indexing operations.

        Example:
            ```
            point_location = new_location.coordinates  # Accessing first coordinate
            ```
        """

        def __getitem__(self, key):
            return default_comparator._binary_operate(self.expr, operators.getitem, key)

    def get_col_spec(self):
        """Returns the SQL representation of the column type."""
        return "GEO_POINT"

    def bind_processor(self, dialect):
        """
        Returns a function to process values before binding to the database.

        Args:
            dialect: The dialect being used.

        Returns:
            callable: A function that processes input values.

        Example:
            ```
            processed_value = bind_processor(dialect)(geojson.Point((102.0, 0.5)))
            ```
        """

        def process(value):
            if isinstance(value, geojson.Point):
                return value.coordinates
            return value

        return process

    def result_processor(self, dialect, coltype):
        """
        Returns a function to process results after retrieval from the database.

        Args:
            dialect: The dialect being used.
            coltype: The column type of the result.

        Returns:
            callable: A function that processes output values.

        Example:
            ```
            result = result_processor(dialect, coltype)(raw_data)
            ```
        """

        return tuple

    comparator_factory = Comparator


class Geoshape(sqltypes.UserDefinedType):
    """
    A custom SQLAlchemy type for representing geographic shapes using GeoJSON.

    This class allows you to store and retrieve complex geographic shapes in a SQL database.
    The shapes are represented as GeoJSON objects and are stored in the database as shapes.

    Example:
        To use the Geoshape type in a SQLAlchemy model:

        ```
        class Area(Base):
            __tablename__ = 'areas'
            id = Column(Integer, primary_key=True)
            shape = Column(Geoshape)

        # Add a new area with GeoJSON Shape
        shape_data = geojson.Polygon([[(30.0, 10.0), (40.0, 40.0), (20.0, 40.0), (10.0, 20.0), (30.0, 10.0)]])
        new_area = Area(shape=shape_data)

        session.add(new_area)
        session.commit()
        ```

    Attributes:
        cache_ok (bool): Indicates whether instances of this type can be cached.

    Methods:
       get_col_spec() -> str: Returns the SQL representation of the column type.
       result_processor(dialect, coltype) -> callable: Returns a function to process results after retrieval from the database.
    """

    cache_ok = True

    class Comparator(sqltypes.TypeEngine.Comparator):
        """
        A custom comparator for the Geoshape type that allows indexing operations.

        Example:
            ```
            shape_coordinates = new_area.shape  # Accessing first coordinate of shape
            ```
        """

        def __getitem__(self, key):
            return default_comparator._binary_operate(self.expr, operators.getitem, key)

    def get_col_spec(self):
        """Returns the SQL representation of the column type."""
        return "GEO_SHAPE"

    def result_processor(self, dialect, coltype):
        """
        Returns a function to process results after retrieval from the database.

        Args:
            dialect: The dialect being used.
            coltype: The column type of the result.

        Returns:
            callable: A function that processes output values.

        Example:
            ```
            processed_shape = result_processor(dialect, coltype)(raw_shape_data)
            ```
        """

        return geojson.GeoJSON.to_instance

    comparator_factory = Comparator
