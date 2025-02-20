from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from base import Base

class Airport(Base):
    __tablename__ = "airports"

    iata_code = Column(String(10), primary_key=True)
    airport = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    state = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)

    flights_origin = relationship("Flight", foreign_keys="[Flight.origin_airport]", back_populates="origin")
    flights_destination = relationship("Flight", foreign_keys="[Flight.destination_airport]", back_populates="destination")

class Airline(Base):
    __tablename__ = "airlines"

    iata_code = Column(String(10), primary_key=True)
    airline = Column(String(255), nullable=False)

    flights = relationship("Flight", back_populates="airline_relation")

class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    airline = Column(String(10), ForeignKey("airlines.iata_code"))
    flight_number = Column(Integer, nullable=False)
    tail_number = Column(String(100))
    origin_airport = Column(String(50), ForeignKey("airports.iata_code"))
    destination_airport = Column(String(50), ForeignKey("airports.iata_code"))
    scheduled_departure = Column(Integer, nullable=False)
    departure_time = Column(Float)
    departure_delay = Column(Float)
    taxi_out = Column(Float)
    wheels_off = Column(Float)
    scheduled_time = Column(Float)
    elapsed_time = Column(Float)
    air_time = Column(Float)
    distance = Column(Integer)
    wheels_on = Column(Float)
    taxi_in = Column(Float)
    scheduled_arrival = Column(Integer)
    arrival_time = Column(Float)
    arrival_delay = Column(Float)
    diverted = Column(Integer, nullable=False)
    cancelled = Column(Integer, nullable=False)
    cancellation_reason = Column(String(255), nullable=True)
    air_system_delay = Column(Float)
    security_delay = Column(Float)
    airline_delay = Column(Float)
    late_aircraft_delay = Column(Float)
    weather_delay = Column(Float)
    
    airline_relation = relationship("Airline", back_populates="flights")
    origin = relationship("Airport", foreign_keys=[origin_airport], back_populates="flights_origin")
    destination = relationship("Airport", foreign_keys=[destination_airport], back_populates="flights_destination")
