import logging
import os

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("AD_ACCOUNT_ID")
FacebookAdsApi.init(access_token=ACCESS_TOKEN)

def get_ads_data(start_date, end_date):
    try:
        logging.debug("📅 [DEBUG] Buscando dados de anúncios de %s até %s", start_date, end_date)

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

        logging.info("✅ [INFO] Total de ROAS calculado: %s", total_roas)
        logging.info("✅ [INFO] Total de PageViews calculado: %s", total_pageviews)


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
        logging.error("Erro ao buscar dados de anúncios: %s", e)
        return {"error": str(e)}



