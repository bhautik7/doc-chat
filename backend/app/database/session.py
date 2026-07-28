from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.utils.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    # Create a new database session/connection before handling the request.
    # This code runs first when FastAPI receives a request.
    db = SessionLocal()
    try:
# "yield" pauses this function and sends the database session
        # to the API route that requested it.
        #
        # Example:
        # def get_users(db: Session = Depends(get_db)):
        #     db.query(User).all()
        #
        # The route uses this database session while processing the request.
             yield db
    except Exception:
        # Roll back so a failed request never leaves a dirty session behind
        # (a pooled connection with a half-applied transaction).
        db.rollback()
        raise
    finally:
        # This code runs after the request is completed.
        # FastAPI executes this even if the API throws an exception.
        #
        # Closing the session releases the database connection back to
        # the connection pool and prevents connection leaks.
      
        db.close()