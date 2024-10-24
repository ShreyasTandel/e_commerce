from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify

def handle_exceptions(logger):
    """Decorator to handle exceptions and log them."""
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SQLAlchemyError as e:
                logger.error(f"Database error occurred: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return jsonify({"error": "An unexpected error occurred"}), 500
        return decorated_function
    return decorator

