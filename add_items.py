from app import db, Item

# Create sample items
item1 = Item(barcode='1234567890123', name='Item One', price=10.99)
item2 = Item(barcode='9876543210987', name='Item Two', price=15.49)

# Add and commit to the database
db.create_all()  # Ensure the database and tables are created
db.session.add(item1)
db.session.add(item2)
db.session.commit()

print("Sample items added to the database.")