from database_handler import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=True, default="")
    price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Product {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price
        }