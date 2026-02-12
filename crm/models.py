from datetime import datetime

from . import db


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rentals = db.relationship("Rental", back_populates="client", cascade="all, delete-orphan")


class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(64), nullable=False, unique=True)
    model_name = db.Column(db.String(120), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    rentals = db.relationship("Rental", back_populates="bike", cascade="all, delete-orphan")


class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    bike_id = db.Column(db.Integer, db.ForeignKey("bike.id"), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default="active")

    client = db.relationship("Client", back_populates="rentals")
    bike = db.relationship("Bike", back_populates="rentals")

    def close(self, finished_at: datetime):
        self.finished_at = finished_at
        hours = max((finished_at - self.started_at).total_seconds() / 3600, 1)
        self.total_cost = round(hours * self.bike.price_per_hour, 2)
        self.status = "closed"
        self.bike.is_available = True
