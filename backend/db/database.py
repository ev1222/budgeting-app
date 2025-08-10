from typing import Any, Optional, Type, Union

from contextlib import contextmanager
from sqlmodel import create_engine, Session, select, SQLModel, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from config import DB_URL
from logs.logger_config import configure_logging

engine = create_engine(DB_URL) # Define engine here for reuse

logger = configure_logging()


@contextmanager
def get_db_session():
    """
    Creates a database session using SQLAlchemy for executing
    database operations within a context manager.

    This function manages the lifecycle of a database session,
    ensuring that it is properly closed after use, even if an
    error occurs during the session's operations. It yields the
    active session to the context, allowing for safe database
    interactions.

    Returns
    -------
    Session
        An active SQLAlchemy session object for database operations.

    Raises
    ------
    SQLAlchemyError
        If an error occurs while creating the session.

    Notes
    -----
    It is important to use this function within a `with` statement
    to ensure the session is properly closed after operations.
    
    Ex.) with get_db_session() as session:
    """
    try:
        session = Session(engine)
        yield session
    except SQLAlchemyError as e:
        logger.error(f"Error creating DB session: {e}")
        raise
    finally:
        session.close()


def save_data(data: list[dict] | dict, model: Type[SQLModel]):
    """
    Saves data to selected table.

    Parameters
    ----------
    data : list[dict] | dict
        Dict or list of dicts of data to add to table. Keys must match table fields and values must match field types.
    model : SQLModel
        The ORM to which to write the data.

    Returns
    -------
    None

    Raises
    ------
    IntegrityError
        If the data being added violates a table restriction.
    Exception
        If there's an unexpected error writing the data.
    """
    if isinstance(data, list):
        data = [model(**d) for d in data]
    else:
        data = model(**data)

    with get_db_session() as session:
        try:
            session.add_all(data) if isinstance(data, list) else session.add(data)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error occurred during commit to {model.__tablename__}: {e}.")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error committing to {model.__tablename__}: {e}.")
            raise


def query_data(
    model: Type[SQLModel],
    filters: Optional[dict[str, Union[Any, tuple[str, Any]]]] = None,
    columns: Optional[list[str]] = None,
    reading_pk: bool = False,
    count_only: bool = False,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Union[list[SQLModel], Optional[SQLModel], tuple, Any]:
    """
    Retrieves entry/entries from the specified table based on filters.

    Parameters
    ----------
    secret_dict : dict[str, str]
        A dictionary containing the database connection parameters.
    model : Type[SQLModel]
        The model representing the table from which to read.
    filters : Optional[dict[str, Union[Any, tuple[str, Any], list[tuple[str, Any]]]]]
        Dictionary of column:value pairs to filter on.
        For IN clauses, pass a list/tuple as the value.\\
        For conditional filtering, pass a tuple or list of tuples of (operator, value) where operator can be:
        '>', '<', '>=', '<=', '==', '!='\\
        Example: {\\
            "status": ["active", "pending"],                # IN clause\\
            "user_id": 123,                                 # Equality\\
            "age": ('>', 18),                               # Greater than\\
            "price": ('<=', 100.00)                         # Less than or equal\\
            "date": [('>=', start_date), ('<=', end_date)]  # List of filters\\
        }
    columns : Optional[List[str]]
        List of column names to retrieve. If None, all columns are retrieved.
        Example: ["id", "name"]
    reading_pk : bool
        Flag that indicates if the query is on a primary key.
        Default is False.
    count_only : bool
        Flag to only retrieve count of would-be retrieved elements.
        Can be used with 'limit' and 'offset' for pagination.
    limit : Optional[int]
        Limits amount of responses fetched.
        Default is None (i.e., return all available responses).
    offset : Optional[int]
        Amount of offset to use in fetching responses; typically used in conjunction with 'limit'.
        Default is None.

    Returns
    -------
    Union[List[SQLModel], Optional[SQLModel], tuple, Any]
        List of results or unique result or tuple of column data or the raw column data if just one column is selected.
        Will be empty list or None if no results are found.

    Raises
    ------
    UniqueViolation
        If a query on a primary key returns more than one result.
    SQLAlchemyError
        If there's an error in connecting to the database or querying the data.
    ValueError
        If invalid column names or operators are provided.
    """
    VALID_OPERATORS = {
        ">": lambda col, val: col > val,
        "<": lambda col, val: col < val,
        ">=": lambda col, val: col >= val,
        "<=": lambda col, val: col <= val,
        "==": lambda col, val: col == val,
        "!=": lambda col, val: col != val,
    }

    with get_db_session() as session:
        try:
            # Modify select statement to include only specified columns and applying count flag
            if columns:
                selected_columns = [getattr(model, col) for col in columns]
                stmt = (
                    select(func.count(*selected_columns))
                    if count_only
                    else select(*selected_columns)
                )
            else:
                stmt = select(func.count(model)) if count_only else select(model)

            # Apply filters
            if filters:
                for column, value in filters.items():
                    column_attr = getattr(model, column)
                    conditions = []

                    # Normalize value to a list of filter conditions
                    if isinstance(value, list) and all(
                        isinstance(v, tuple) and len(v) == 2 and isinstance(v[0], str)
                        for v in value
                    ):
                        # List of operator filters: [(">=", x), ("<=", y)]
                        conditions = value
                    elif isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], str):
                        # Single operator filter: (">=", x)
                        conditions = [value]
                    elif isinstance(value, (list, tuple)):
                        # IN clause: ["a", "b", "c"]
                        stmt = stmt.where(column_attr.in_(value))
                        continue
                    else:
                        # Default, equality: x
                        stmt = stmt.where(column_attr == value)
                        continue
                
                # Apply operator filters
                for operator, operator_value in conditions:
                    if operator not in VALID_OPERATORS:
                        raise ValueError(
                            f"Invalid operator: {operator}. Valid operators are: {VALID_OPERATORS}"
                        )
                    stmt = stmt.where(VALID_OPERATORS[operator](column_attr, operator_value))

            if count_only:
                return session.exec(stmt).one()

            # Apply limit and/or offset
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)

            if reading_pk:
                result: SQLModel = session.exec(stmt).first()
                # need to bind result to new instance of model to avoid lazy-loading
                # and the ORM from going out of scope from the DB session
                return model(**result.model_dump()) if result else None
            elif columns:
                return session.exec(stmt).all()
            else:
                results: list[SQLModel] = session.exec(stmt).all()
                return [model(**r.model_dump()) for r in results]

        except AttributeError as e:
            logger.error(f"Invalid column name: {e}")
            raise ValueError(f"Invalid column name: {e}")
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Failed to read entry from {model.__tablename__}: {e}")
            raise