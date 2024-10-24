import json
import logging
from flask import Flask, request, jsonify
from models import Product
from database_handler import DatabaseHandler, db  # Import db from DatabaseHandler
import custom_dacorator as cust_deco
from validators import ProductValidator

class ProductAPI:
    def __init__(self, db_handler):
        self.app = Flask(__name__)
        self.db_handler = db_handler
        self.validator = ProductValidator()
        self.setup_logging()
        self.setup_routes()

        # Initialize the app with the database handler
        self.db_handler.initialize_app(self.app)

        # Ensure the database exists
        with self.app.app_context():
            self.db_handler.create_database_if_not_exists()

    def setup_logging(self):
        logging.basicConfig(
            filename='app.log',
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("App initialized and logger configured.")

    def setup_routes(self):
        self.app.route('/products', methods=['GET'])(cust_deco.handle_exceptions(self.logger)(self.get_products))
        self.app.route('/products/<int:id>', methods=['GET'])(cust_deco.handle_exceptions(self.logger)(self.get_product))
        self.app.route('/products', methods=['POST'])(cust_deco.handle_exceptions(self.logger)(self.create_product))
        self.app.route('/products/<int:id>', methods=['PUT'])(cust_deco.handle_exceptions(self.logger)(self.update_product))
        self.app.route('/products/<int:id>', methods=['DELETE'])(cust_deco.handle_exceptions(self.logger)(self.delete_product))

    def get_products(self):
        self.logger.info("GET /products called")

        # Get limit and skip parameters from the query string
        limit = request.args.get('limit', default=10, type=int)  # Default to 10 if not provided
        skip = request.args.get('skip', default=0, type=int)    # Default to 0 if not provided

        # Fetch products with limit and offset
        products = Product.query.offset(skip).limit(limit).all()

        result = [{'id': p.id, 'title': p.title, 'description': p.description, 'price': p.price} for p in products]
        self.logger.debug(f"Retrieved products: {result}")
        return jsonify(result)

    def get_product(self, id):
        self.logger.info(f"GET /products/{id} called")
        product = db.session.get(Product, id)
        
        # Handle case where product is not found
        if product is None:
            self.logger.error(f"Product with id {id} not found.")
            return jsonify({"error": "Product not found"}), 404
        
        result = {
            'id': product.id, 
            'title': product.title, 
            'description': product.description, 
            'price': product.price}
        self.logger.debug(f"Retrieved product: {result}")
        return jsonify(result)

    def create_product(self):
        self.logger.info("POST /products called")
        data = request.get_json()
        validated_data, errors = self.validator.validate(data)
        if errors:
            return jsonify({'error': 'Invalid input', 'messages': errors}), 400
        
        # if same title is already exist then considering product already exist
        existing_product = Product.query.filter_by(title=validated_data['title']).first()
        if existing_product:
            self.logger.error(f"Product with title '{validated_data['title']}' already exists.")
            return jsonify({'error': 'Product with this title already exists.'}), 400

        new_product = Product(**validated_data)
        db.session.add(new_product)
        db.session.commit()
        self.logger.debug(f"Created product: {new_product.to_dict()}")
        return jsonify(new_product.to_dict()), 201

    def update_product(self, id):
        self.logger.info(f"PUT /products/{id} called")
        product = db.session.get(Product, id)
        
        # Handle case where product is not found
        if product is None:
            self.logger.error(f"Product with id {id} not found.")
            return jsonify({"error": "Product not found"}), 404
        
        data = request.get_json()

        validated_data, errors = self.validator.validate(data)
        if errors:
            return jsonify({'error': 'Invalid input', 'messages': errors}), 400

        product.title = validated_data['title']
        product.description = validated_data.get('description', product.description)
        product.price = validated_data['price']
        db.session.commit()
        self.logger.debug(f"Updated product: {product.to_dict()}")
        return jsonify(product.to_dict())

    def delete_product(self, id):
        self.logger.info(f"DELETE /products/{id} called")
        # Fetch product by id
        product = db.session.get(Product, id)
        
        # Handle case where product is not found
        if product is None:
            self.logger.error(f"Product with id {id} not found.")
            return jsonify({"error": "Product not found"}), 404
        
        db.session.delete(product)
        db.session.commit()
        self.logger.debug(f"Deleted product with id {id}")
        return jsonify({'message': 'Product deleted successfully'})

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    with open('config.json', 'r') as file:
        config = json.load(file)
        username = config.get('username')
        password = config.get('password')
    if not username or not password:
        raise ValueError("Username and password must not be empty.")
    db_uri = 'mysql://{}:{}@localhost/ecommerce_db'.format(username, password)
    database = DatabaseHandler(db_uri)
    api = ProductAPI(database)
    api.run()