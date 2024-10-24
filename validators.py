from marshmallow import Schema, fields, validate, ValidationError

# Define the schema for product validation
class ProductSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1))
    description = fields.String(missing='', validate=validate.Length(max=500))
    price = fields.Float(required=True, validate=validate.Range(min=0))

class ProductValidator:
    def __init__(self):
        self.schema = ProductSchema()

    def validate(self, data):
        """Validate the input data for creating/updating products."""
        try:
            validated_data = self.schema.load(data)
            return validated_data, None
        except ValidationError as err:
            return None, err.messages
