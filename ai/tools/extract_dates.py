from langchain_core.tools import tool
from datetime import datetime, date
import requests

@tool
def verify_and_extract_dates(dates: list, bearer_token: str) -> dict:
    
    """
    Verify dates against holidays, vacations, prohibited periods, and exclude past dates including today.
    Return a dictionary with allowed dates as keys and their corresponding day of the week as values.
    If the dictionary is empty, all requested dates are blocked.
    Only use this if the user is requesting vacation days or absence days.
    Only use this if the user mentions dates in the request.

    Args:
        dates (list): List of date strings in YYYY-MM-DD format.
        bearer_token (str): Bearer token for authentication.

    Returns:
        dict: Allowed dates with corresponding day of the week.
              and a list of removed dates with the reasons for removal.
    """

    # Fetch User Info

    
    response=requests.get(
        "https://api-dev.hrstudium.pt/users",
        headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
    )
    if response.status_code == 200:
        user_basic_data = response.json()
        user_id = user_basic_data["id"]
    else:
        print("Failed to fetch basic user data:", response.status_code)
        

    response=requests.get(
        "https://api-dev.hrstudium.pt/users/info/" + str(user_id),
        headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
    )
    if response.status_code == 200:
        user_data= response.json()
    else:
        print("Failed to fetch user data:", response.status_code)




    # Fetch holidays
    holiday_dates = []
    response = requests.get(
        "https://api-dev.hrstudium.pt/holidays",
        headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
    )
    if response.status_code == 200:
        all_holidays= response.json().get("data", [])
        holiday_dates = []

        for holiday in all_holidays:
             if any(e["id_empresa"] == user_data["id_empresa"] for e in holiday["ferias_feriados_empresas"]) \
                or any(est["id_estabelecimento"] == user_data["id_estabelecimento"] for est in holiday["ferias_feriados_estabelecimentos"]):
                    holiday_dates.append(holiday["data"])
    else:
        print("Failed to fetch holidays data:", response.status_code)

    # Fetch vacations and absences
    requested_dates = []
    response = requests.get(
        "https://api-dev.hrstudium.pt/vacations",
        headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
    )
    if response.status_code == 200:
        vacation_data = response.json()
        for vac_request in vacation_data.get("pedidos_ferias", []):
            for d in vac_request.get("ferias_users_pedidos_datas", []):
                requested_dates.append(d["data"])
        for abs_request in vacation_data.get("pedidos_ausencias", []):
            for d in abs_request.get("ausencias_users_pedidos_datas", []):
                requested_dates.append(d["data"])
    else:
        print("Failed to fetch vacations data:", response.status_code)

    # Fetch prohibited periods
    prohibited_dates = []
    response = requests.get(
        "https://api-dev.hrstudium.pt/vacations/prohibited-periods",
        headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
    )
    if response.status_code == 200:
        for period in response.json().get("data", []):
            excecoes_user_ids = {e["id_user"] for e in period["ferias_periodos_proibidos_excecoes"]}
        
            
            if user_data["id"] in excecoes_user_ids:
                continue

            if period["aplicado_toda_empresa"] == 1:
                for day in period["ferias_periodos_proibidos_dias"]:
                    prohibited_dates.append(day["data"])

            else:
                setor_ids = {s["id_setor"] for s in period["ferias_periodos_proibidos_setores"]}
                if user_data["id_setor"] in setor_ids:
                    for day in period["ferias_periodos_proibidos_dias"]:
                        prohibited_dates.append(day["data"])
    else:
        print("Failed to fetch prohibited periods data:", response.status_code)

    # Combine all blocked dates
    blocked_dates = set(holiday_dates + requested_dates + prohibited_dates)

    # Verify and extract weekdays for allowed dates
    print("Dates to verify:", dates)
    allowed_dates = {}
    removed_dates = []

    for date_str in dates:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Check if date is in the past or today
            if date_obj <= date.today():
                removed_dates.append({"date": date_str, "reason": "Data passada ou hoje"})
                continue

            # Check if date is blocked
            if date_str not in blocked_dates:
                day_of_week = date_obj.strftime("%A")
                if day_of_week not in ["Saturday", "Sunday"]:
                    allowed_dates[date_str] = day_of_week
                else:
                    removed_dates.append({"date": date_str, "reason": "Fim de semana"})
            else:
                reason = ""
                if date_str in holiday_dates:
                    reason = "Feriado"
                elif date_str in requested_dates:
                    reason = "Data já pedida"
                elif date_str in prohibited_dates:
                    reason = "Período Proibido"
                elif date_obj.strftime("%A") in ["Saturday", "Sunday"]:
                    reason = "Fim de semana"
                else:
                    reason = "No reason"

                removed_dates.append({"date": date_str, "reason": reason})

        except ValueError:
            print(f"Invalid date format: {date_str}")
            continue

    print("Allowed Dates:", allowed_dates)
    print("Removed Dates:", removed_dates)
    return {
        "allowed_dates": allowed_dates,
        "removed_dates": removed_dates
    }
