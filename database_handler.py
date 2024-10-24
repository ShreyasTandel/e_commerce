from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import text

# Define the SQLAlchemy instance
db = SQLAlchemy()

class DatabaseHandler:
    def __init__(self, db_uri):
        self.db_uri = db_uri
        # Engine without the database for initial connection
        self.engine = create_engine(self.db_uri.rsplit('/', 1)[0])  # Temporary engine for DB creation

    def create_database_if_not_exists(self):
        """Create the database if it doesn't exist."""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("CREATE DATABASE IF NOT EXISTS ecommerce_db"))
                print("Database created or already exists.")
        except ProgrammingError as e:
            print(f"Error occurred: {e}")
        finally:
            self.engine.dispose()

    def initialize_app(self, app):
        """Bind the database to the Flask app."""
        app.config['SQLALCHEMY_DATABASE_URI'] = self.db_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)  # Initialize the app with the SQLAlchemy instance
        with app.app_context():
            db.create_all()  # Create tables if they don't exist
