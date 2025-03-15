# routes/main_routes.py

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from services.ads_service import get_ads_data
from services.pixel_service import get_pixel_pageviews
from services.date_service import calcular_periodo  # <-- Importa aqui

main_bp = Blueprint("main_bp", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/data")
def get_data():
    period = request.args.get("period", "last_7d")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if period == "custom" and start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        # Agora você chama sua função auxiliar
        start_date, end_date = calcular_periodo(period)

    ads_data = get_ads_data(start_date, end_date)
    # pixel_data = get_pixel_pageviews(start_date, end_date)  # se precisar

    return jsonify(ads_data)
