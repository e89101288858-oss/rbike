from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from . import db
from .models import Bike, Client, Rental

bp = Blueprint("main", __name__)


@bp.route("/")
def dashboard():
    active_rentals = Rental.query.filter_by(status="active").count()
    available_bikes = Bike.query.filter_by(is_available=True).count()
    clients_count = Client.query.count()
    income = db.session.query(db.func.sum(Rental.total_cost)).filter(Rental.status == "closed").scalar() or 0
    return render_template(
        "dashboard.html",
        active_rentals=active_rentals,
        available_bikes=available_bikes,
        clients_count=clients_count,
        income=round(income, 2),
    )


@bp.route("/clients", methods=["GET", "POST"])
def clients():
    if request.method == "POST":
        client = Client(
            full_name=request.form["full_name"],
            phone=request.form["phone"],
            email=request.form.get("email") or None,
        )
        db.session.add(client)
        db.session.commit()
        return redirect(url_for("main.clients"))

    return render_template("clients.html", clients=Client.query.order_by(Client.created_at.desc()).all())


@bp.route("/bikes", methods=["GET", "POST"])
def bikes():
    if request.method == "POST":
        bike = Bike(
            serial_number=request.form["serial_number"],
            model_name=request.form["model_name"],
            price_per_hour=float(request.form["price_per_hour"]),
        )
        db.session.add(bike)
        db.session.commit()
        return redirect(url_for("main.bikes"))

    return render_template("bikes.html", bikes=Bike.query.order_by(Bike.id.desc()).all())


@bp.route("/rentals", methods=["GET", "POST"])
def rentals():
    if request.method == "POST":
        rental = Rental(
            client_id=int(request.form["client_id"]),
            bike_id=int(request.form["bike_id"]),
            started_at=datetime.fromisoformat(request.form["started_at"]),
        )
        bike = Bike.query.get(rental.bike_id)
        bike.is_available = False
        db.session.add(rental)
        db.session.commit()
        return redirect(url_for("main.rentals"))

    active_clients = Client.query.order_by(Client.full_name.asc()).all()
    available_bikes = Bike.query.filter_by(is_available=True).order_by(Bike.model_name.asc()).all()
    all_rentals = Rental.query.order_by(Rental.started_at.desc()).all()
    return render_template(
        "rentals.html",
        clients=active_clients,
        bikes=available_bikes,
        rentals=all_rentals,
    )


@bp.post("/rentals/<int:rental_id>/close")
def close_rental(rental_id: int):
    rental = Rental.query.get_or_404(rental_id)
    if rental.status == "active":
        rental.close(datetime.utcnow())
        db.session.commit()
    return redirect(url_for("main.rentals"))
