from app import create_app, db
from app.models import User  # Import any model

app = create_app()

with app.app_context():
    try:
        # Test connection
        db.engine.connect()
        print("✓ Database connection successful")
        
        # Test basic query
        User.query.first()
        print("✓ Database query successful")
        
        # Verify tables exist
        print("Tables in database:", db.engine.table_names())
        
    except Exception as e:
        print("✗ Database error:", str(e))