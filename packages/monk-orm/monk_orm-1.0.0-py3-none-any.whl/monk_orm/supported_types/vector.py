"""
## Origin
This module is based on the corresponding pgvector implementation
by Andrew Kane. Thank you.

The MIT License (MIT)
Copyright (c) 2021-2023 Andrew Kane
https://github.com/pgvector/pgvector-python
"""

import typing as t

if t.TYPE_CHECKING:
    import numpy.typing as npt  # pragma: no cover

import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ColumnElement, literal

__all__ = [
    "from_db",
    "knn_match",
    "to_db",
    "FloatVector",
]


def from_db(value: t.Iterable) -> t.Optional["npt.ArrayLike"]:
    """
    Convert a database representation of a vector to a NumPy array.

    This function is used to process the data retrieved from the database
    and convert it into a NumPy array, which is a more convenient format
    for numerical operations in Python.

    Args:
        value (t.Iterable): The vector data retrieved from the database.

    Returns:
        t.Optional["npt.ArrayLike"]: A NumPy array representing the vector,
            or None if the input value is None.

    Example:
        ```
        import numpy as np

        # Assume you have retrieved a vector from the database as a list
        vector_from_db = [1.0, 2.0, 3.0]

        # Convert it to a NumPy array
        numpy_vector = from_db(vector_from_db)

        assert isinstance(numpy_vector, np.ndarray)
        assert numpy_vector.dtype == np.float32
        ```
    """
    import numpy as np

    # from `pgvector.utils`
    # could be ndarray if already cast by lower-level driver
    if value is None or isinstance(value, np.ndarray):
        return value

    return np.array(value, dtype=np.float32)


def to_db(value: t.Any, dim: t.Optional[int] = None) -> t.Optional[t.List]:
    """
    Convert a vector (NumPy array or list) to a database-compatible list.

    This function is used to process vector data before it is inserted
    or updated in the database. It converts NumPy arrays to Python lists
    and validates the dimensions of the vector.

    Args:
        value (t.Any): The vector data to be stored in the database.
                         It can be a NumPy array or a list.
        dim (t.Optional[int]): The expected number of dimensions of the vector.
                                If specified, the function will raise a ValueError
                                if the vector does not have the expected dimensions.

    Returns:
        t.Optional[t.List]: A Python list representing the vector,
            or None if the input value is None.

    Raises:
        ValueError: If the input value is a NumPy array with more than one dimension,
            or if the data type of the NumPy array is not numeric,
            or if the vector does not have the expected dimensions specified by the `dim` parameter.

    Example:
        ```
        import numpy as np

        # Example with a NumPy array
        numpy_vector = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        db_vector = to_db(numpy_vector, dim=3)
        assert isinstance(db_vector, list)
        assert db_vector == [1.0, 2.0, 3.0]

        # Example with a Python list
        python_list = [4.0, 5.0, 6.0]
        db_vector = to_db(python_list, dim=3)
        assert isinstance(db_vector, list)
        assert db_vector == [4.0, 5.0, 6.0]
        ```
    """
    import numpy as np

    # from `pgvector.utils`
    if value is None:
        return value

    if isinstance(value, np.ndarray):
        if value.ndim != 1:
            raise ValueError("expected ndim to be 1")

        if not np.issubdtype(value.dtype, np.integer) and not np.issubdtype(
            value.dtype, np.floating
        ):
            raise ValueError("dtype must be numeric")

        value = value.tolist()

    if dim is not None and len(value) != dim:
        raise ValueError("expected %d dimensions, not %d" % (dim, len(value)))

    return value


class FloatVector(sa.TypeDecorator):
    """
    SQLAlchemy `FloatVector` data type for MonkDB.

    This class allows you to define a column in your SQLAlchemy model that
    stores a vector of floating-point numbers. It handles the conversion
    between Python lists/NumPy arrays and the format expected by MonkDB.

    Example:
        ```
        from sqlalchemy import create_engine, Column, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        Base = declarative_base()

        class Item(Base):
            __tablename__ = 'items'
            id = Column(Integer, primary_key=True)
            embedding = Column(FloatVector(dimensions=128))  # Vector of 128 dimensions

        engine = create_engine('monkdb://user:password@host:port/database')
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Insert a new item with a vector embedding
        new_item = Item(embedding=[0.1, 0.2, ..., 0.128])
        session.add(new_item)
        session.commit()
        ```
    """

    cache_ok = False

    __visit_name__ = "FLOAT_VECTOR"

    _is_array = True

    zero_indexes = False

    impl = sa.ARRAY

    def __init__(self, dimensions: int = None):
        """
        Construct a new `FloatVector` column type.

        Args:
            dimensions (int, optional): The number of dimensions in the vector.
                                         If specified, the database will enforce
                                         that all vectors in this column have the
                                         specified number of dimensions.
        """
        super().__init__(sa.FLOAT, dimensions=dimensions)

    def as_generic(self, allow_nulltype=False):
        """
        Return a generic `sa.ARRAY` type with `sa.FLOAT` as the item type.
        """
        return sa.ARRAY(item_type=sa.FLOAT)

    @property
    def python_type(self):
        """
        Return the Python type associated with this data type (list).
        """
        return list

    def bind_processor(self, dialect: sa.engine.Dialect) -> t.Callable:
        """
        Return a function to process values before binding to the database.

        This function uses the `to_db` function to convert Python lists/NumPy
        arrays to a database-compatible format.

        Args:
            dialect (sa.engine.Dialect): The SQLAlchemy dialect being used.

        Returns:
            t.Callable: A function that takes a Python list/NumPy array and
                returns a database-compatible list.
        """
        def process(value: t.Iterable) -> t.Optional[t.List]:
            return to_db(value, self.dimensions)

        return process

    def result_processor(self, dialect: sa.engine.Dialect, coltype: t.Any) -> t.Callable:
        """
        Return a function to process values after retrieval from the database.

        This function uses the `from_db` function to convert the database
        representation of the vector to a NumPy array.

        Args:
            dialect (sa.engine.Dialect): The SQLAlchemy dialect being used.
            coltype (t.Any): The column type of the result.

        Returns:
            t.Callable: A function that takes the database representation of
                the vector and returns a NumPy array.
        """
        def process(value: t.Any) -> t.Optional["npt.ArrayLike"]:
            return from_db(value)

        return process


class KnnMatch(ColumnElement):
    """
    Wrap MonkDB's `KNN_MATCH` function into an SQLAlchemy function.

    This class allows you to use MonkDB's `KNN_MATCH` function in your
    SQLAlchemy queries to perform k-nearest neighbors (k-NN) search on vectors.

    Example:
        ```
        from sqlalchemy import create_engine, Column, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import func

        Base = declarative_base()

        class Item(Base):
            __tablename__ = 'items'
            id = Column(Integer, primary_key=True)
            embedding = Column(FloatVector(dimensions=128))

        engine = create_engine('monkdb://user:password@host:port/database')
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Find the 5 nearest neighbors of a given vector
        search_vector = [0.3, 0.4, ..., 0.1]  # Your search vector
        nearest_neighbors = session.query(Item).order_by(
            func.knn_match(Item.embedding, search_vector, 5)
        ).limit(5).all()
        ```
    """

    inherit_cache = True

    def __init__(self, column, term, k=None):
        """
        Construct a new `KnnMatch` expression.

        Args:
            column: A reference to a column containing vector data.
            term: The vector to search for nearest neighbors.
            k (int, optional): The number of nearest neighbors to return.
                                 If None, the database's default value is used.
        """
        super().__init__()
        self.column = column
        self.term = term
        self.k = k

    def compile_column(self, compiler):
        """
        Compile the column reference.
        """
        return compiler.process(self.column)

    def compile_term(self, compiler):
        """
        Compile the search term (vector).
        """
        return compiler.process(literal(self.term))

    def compile_k(self, compiler):
        """
        Compile the number of nearest neighbors (k).
        """
        return compiler.process(literal(self.k))


def knn_match(column, term, k):
    """
    Generate a match predicate for vector search.

    This function creates a `KnnMatch` object, which represents a call
    to MonkDB's `KNN_MATCH` function.  You can use this function in your
    SQLAlchemy queries to perform k-nearest neighbors (k-NN) search on vectors.

    Args:
        column: A reference to a column or an index.
        term: The term to match against. This is an array of floating point
            values, which is compared to other vectors using a HNSW index search.
        k: The `k` argument determines the number of nearest neighbours to
           search in the index.

    Returns:
        KnnMatch: A `KnnMatch` object representing the k-NN search expression.
    """
    return KnnMatch(column, term, k)


@compiles(KnnMatch)
def compile_knn_match(knn_match, compiler, **kwargs):
    """
    Clause compiler for `KNN_MATCH`.

    This function is called by SQLAlchemy to compile the `KnnMatch` object
    into a SQL expression that can be executed by MonkDB.

    Args:
        knn_match (KnnMatch): The `KnnMatch` object to compile.
        compiler: The SQLAlchemy compiler object.
        **kwargs: Additional keyword arguments.

    Returns:
        str: A SQL expression representing the `KNN_MATCH` function call.
    """
    return "KNN_MATCH(%s, %s, %s)" % (
        knn_match.compile_column(compiler),
        knn_match.compile_term(compiler),
        knn_match.compile_k(compiler),
    )
