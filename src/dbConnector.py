from sqlalchemy import create_engine, Column, String, DateTime, Integer, func as sqlfunc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import logging

# Base class for models
Base = declarative_base()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Singleton Class for Database Connection Management"""

    _engine = None
    _Session = None

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.session = None

        # Initialize the engine only once
        if DatabaseConnection._engine is None:
            DatabaseConnection._engine = create_engine(
                self.connection_string,
                pool_size=10,  # Max connections in the pool
                max_overflow=5,  # Extra connections beyond pool_size
                pool_timeout=30,  # Wait time for connection before timeout
                pool_recycle=1800,  # Recycle connections every 30 minutes
                echo=False,  # Set to True for SQL query logs
            )
            DatabaseConnection._Session = scoped_session(
                sessionmaker(
                    bind=DatabaseConnection._engine,
                    autocommit=False,  # Manage commits manually
                    autoflush=False,  # Prevent auto-flush issues
                )
            )

    def __enter__(self):
        self.session = DatabaseConnection._Session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                logger.error(f"Database Error: {exc_val}")
                self.session.rollback()
        finally:
            self.session.close()


# Define Orders Table
class OrdersDB(Base):
    __tablename__ = "TransportOrders"

    OrderID = Column(Integer, primary_key=True, autoincrement=True)
    TransportRequestID = Column(String(255), nullable=False, unique=True)
    CustomerID = Column(String(255), nullable=True)
    CustomerName = Column(String(255), nullable=True)
    CreateTime = Column(DateTime, default=sqlfunc.now(), nullable=False)
    EstimatedPickupTime = Column(String(255), nullable=True)
    EstimatedDropoffTime = Column(String(255), nullable=True)
    JobPrice = Column(String(255), nullable=True)
    CarrierCost = Column(String(255), nullable=True)
    Status = Column(String(255), nullable=True)
    PickupLocation = Column(String(255), nullable=True)
    DropoffLocation = Column(String(255), nullable=True)
    ActualPickupTime = Column(DateTime, nullable=True)
    ActualDeliveryTime = Column(DateTime, nullable=True)
    CarrierName = Column(String(255), nullable=True)
    CarrierID = Column(String(255), nullable=True)
    DearlerAtPickup = Column(String(255), nullable=True)
    DearlerAtDropoff = Column(String(255), nullable=True)
    ContactDropoff	= Column(String(255), nullable=True)
    ContactPickup = Column(String(255), nullable=True)