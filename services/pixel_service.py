import logging
import os
import requests
import time

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

        logging.info(f"✅ [INFO] Total de PageViews calculado %s: total_pageviews")
        return total_pageviews  
    
    except requests.exceptions.RequestException as e:
      logging.error("Erro de requisição: %s", e)
      return 0
    except ValueError as e:
       logging.error("Erro ao converter JSON: %s", e)
       return 0