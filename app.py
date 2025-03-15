import logging
import requests
import time
import os
from flask import Flask, jsonify, render_template, request
from datetime import datetime, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.DEBUG,  # Pode ajustar para INFO ou WARNING em produção
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info("Teste: configuração do logging funcionando!")

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__, static_folder='static')

# Configurações seguras
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("AD_ACCOUNT_ID")
FacebookAdsApi.init(access_token=ACCESS_TOKEN)

def calcular_periodo(period):
    hoje = datetime.today()
    period_mapping = {
        "today": (hoje, hoje),
        "yesterday": (hoje - timedelta(days=1), hoje - timedelta(days=1)),
        "last_7d": (hoje - timedelta(days=7), hoje),
        "last_14d": (hoje - timedelta(days=14), hoje),
        "last_30d": (hoje - timedelta(days=30), hoje),
        "this_month": (hoje.replace(day=1), hoje),
        "last_month": ((hoje.replace(day=1) - timedelta(days=1)).replace(day=1), hoje.replace(day=1) - timedelta(days=1)),
        "max": (datetime(2022, 2, 12), hoje)
    }
    return period_mapping.get(period, (hoje - timedelta(days=7), hoje))


def get_pixel_pageviews(start_date, end_date):
    try:
        pixel_id = os.getenv("PIXEL_ID")  
        if not pixel_id:
            logging.error("⚠️ [ERRO] PIXEL_ID não foi encontrado no .env")
            return 0

        # 🔹 Converte as datas para formato UNIX timestamp
        since_unix = int(time.mktime(start_date.timetuple()))
        until_unix = int(time.mktime(end_date.timetuple()))

        url = f"https://graph.facebook.com/v22.0/{pixel_id}/stats"
        params = {
            "aggregation": "event",  # 🔹 Mantemos a agregação correta
            "since": since_unix,
            "until": until_unix,
            "access_token": os.getenv("ACCESS_TOKEN")
        }
        
        response = requests.get(url, params=params)

        if response.status_code != 200:
            logging.error("Erro ao acessar API do Pixel. Status: %s, Resposta: %s", response.status_code, response.text)
            return 0

        data = response.json()
        logging.debug("📊 [DEBUG] Resposta da API do Pixel: %s", data)  # Log para depuração

        total_pageviews = 0  # Variável para armazenar o total

        if "data" in data:
            for event_group in data["data"]:
                if "data" in event_group:
                    for event in event_group["data"]:
                        if event.get("value") == "PageView":
                            total_pageviews += int(event.get("count", 0))  # Somando corretamente

        logging.info(f"✅ [INFO] Total de PageViews calculado: {total_pageviews}")
        return total_pageviews  
    except Exception as e:
        logging.error(f"❌ [ERRO] Erro ao buscar PageViews: {e}")
        return 0


def get_ads_data(start_date, end_date):
    try:
        logging.debug(f"📅 [DEBUG] Buscando dados de anúncios de {start_date} até {end_date}")
        
        account = AdAccount(AD_ACCOUNT_ID)
        fields = [
            "spend", "cpm", "inline_link_click_ctr", "inline_link_clicks",
            "cost_per_inline_link_click", "actions", "purchase_roas", 
            "impressions"
        ]
        params = {
            "time_range": {"since": start_date.strftime("%Y-%m-%d"), "until": end_date.strftime("%Y-%m-%d")},
            "level": "adset",
            "limit": 1000
        }
        ads_data = account.get_insights(fields=fields, params=params)

        logging.debug("📊 [DEBUG] Resposta da API de Ads: %s", ads_data)

        if not ads_data:
            return {"error": "Nenhum dado retornado para este período."}

        total_spend = total_clicks = total_impressions = total_purchases = total_pageviews = 0
        total_roas = 0  

        for ad in ads_data:
            total_spend += float(ad.get("spend", 0))
            total_clicks += int(ad.get("inline_link_clicks", 0))
            total_impressions += int(ad.get("impressions", 0))

            # 🔹 Extraindo `purchase_roas` corretamente
            roas_data = ad.get("purchase_roas", [])
            if isinstance(roas_data, list):
                for roas in roas_data:
                    total_roas += float(roas.get("value", 0))  # Somando corretamente

            # 🔹 Extraindo `landing_page_views`
            actions = ad.get("actions", [])
            for action in actions:
                if action.get("action_type") == "landing_page_view":
                    total_pageviews += int(action.get("value", 0))  # Somando os PageViews corretamente

                if action.get("action_type") == "purchase":
                    total_purchases += int(action.get("value", 0))

        cpm = (total_spend * 1000 / total_impressions) if total_impressions > 0 else 0
        cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0

        logging.info(f"✅ [INFO] Total de ROAS calculado: {total_roas}")
        logging.info(f"✅ [INFO] Total de PageViews calculado: {total_pageviews}")

        return {
            "gasto": round(total_spend, 2),
            "cpm": round(cpm, 2),
            "ctr": round(ctr, 2),
            "cliques": total_clicks,
            "cpc": round(cpc, 2),
            "roas": round(total_roas, 2),  # 🔹 Agora corrigido para somar valores corretamente
            "resultados": total_purchases,
            "valor_conversao": round(total_spend * total_roas, 2) if total_roas > 0 else 0,
            "pageviews": total_pageviews  # 🔹 Agora exibe corretamente os PageViews
        }
    except Exception as e:
        return {"error": str(e)}










@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    period = request.args.get("period", "last_7d")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    if period == "custom" and start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        start_date, end_date = calcular_periodo(period)

    logging.debug(f"📅 [DEBUG] Período: {period} | De: {start_date} Até: {end_date}")  # Log para verificar as datas

    data = get_ads_data(start_date, end_date)
    
    logging.debug(f"📊 [DEBUG] Dados retornados: {data}")  # Log para verificar o que está vindo da API
    
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


