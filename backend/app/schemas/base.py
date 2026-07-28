from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base schema for responses serialized from SQLAlchemy models."""

    model_config = ConfigDict(from_attributes=True)
