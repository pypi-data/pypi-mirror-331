from .base import Base, HumanIDMixin
from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import (
    TEXT,
    JSONB,
    INTEGER,
    BOOLEAN,
    TIMESTAMP,
    FLOAT,
)


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(TEXT, primary_key=True)
    name = Column(TEXT, nullable=False)

    # Relationships
    inverters = relationship("Inverter", back_populates="integration")
    tokens = relationship("Token", back_populates="integration")


class Location(Base, HumanIDMixin):
    __tablename__ = "locations"
    __prefix__ = "loc"
    __id_length__ = 16

    id = Column(TEXT, primary_key=True)
    latitude = Column(FLOAT, nullable=False)
    longitude = Column(FLOAT, nullable=False)

    inverters = relationship("Inverter", back_populates="location")


class Inverter(Base, HumanIDMixin):
    __tablename__ = "inverters"
    __prefix__ = "inv"
    __id_length__ = 16

    id = Column(TEXT, primary_key=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    name = Column(TEXT, nullable=False)
    external_id = Column(TEXT, nullable=False)
    rated_power = Column(INTEGER, nullable=False)
    data = Column(JSONB, nullable=False)

    # Foreign Keys
    token_id = Column(
        TEXT,
        ForeignKey("token_vault.tokens.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    location_id = Column(
        TEXT,
        ForeignKey("locations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    integration_id = Column(
        TEXT,
        ForeignKey("integrations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    # Relationships
    integration = relationship("Integration", back_populates="inverters")
    token = relationship("Token", back_populates="inverters")
    measurements = relationship("InverterMeasurement", back_populates="inverter")
    location = relationship("Location", back_populates="inverters")


class InverterMeasurement(Base):
    __tablename__ = "inverter_measurements"

    inverter_id = Column(
        TEXT,
        ForeignKey("inverters.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    time = Column(TIMESTAMP(timezone=True), primary_key=True)
    power = Column(INTEGER, nullable=False)

    inverter = relationship("Inverter", back_populates="measurements")


class SolarModelType(Base):
    __tablename__ = "solar_model_types"

    id = Column(TEXT, primary_key=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    name = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    is_main = Column(BOOLEAN, nullable=False, default=False)
    models = relationship("SolarModel", back_populates="model_type")


class SolarModel(Base, HumanIDMixin):
    __tablename__ = "solar_models"
    __prefix__ = "sm"
    __id_length__ = 16

    id = Column(TEXT, primary_key=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    name = Column(TEXT, nullable=False)
    params = Column(JSONB, nullable=False)
    inverter_id = Column(
        TEXT,
        ForeignKey("inverters.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    model_type_id = Column(
        TEXT,
        ForeignKey("solar_model_types.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    model_type = relationship("SolarModelType", back_populates="models")
