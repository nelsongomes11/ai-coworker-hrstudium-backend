import json
from langchain_core.tools import tool
from datetime import datetime, timedelta
import requests
from typing_extensions import TypedDict,Annotated



@tool
def check_requests(bearer_token: str, type_requests: str) -> str:
    """

    Check the status of requests in the HR system.
    ONLY use this when the user SPECIFICALLY asks for their requested vacation or absence days.
    Use this to check the status of vacation or absence requests.
    

    Args:
        bearer_token (str): Bearer token for authentication.
        type_requests (str): Type of requests to check, either "ferias" or "ausencias" or "both".
    
    Returns:
        str: List of requested vacation dates in YYYY-MM-DD format.
        str: List of requested absence dates in YYYY-MM-DD format.
    

    """

    requested_dates_vacations = []
    requested_dates_absences = []
    response = requests.get(
        "https://api-dev.hrstudium.pt/vacations",
        headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
    )
    if response.status_code == 200:
        vacation_data = response.json()
        for vac_request in vacation_data.get("pedidos_ferias", []):
            for d in vac_request.get("ferias_users_pedidos_datas", []):
                requested_dates_vacations.append({"date": d["data"],"type": "Férias"})
        for abs_request in vacation_data.get("pedidos_ausencias", []):

            for d in abs_request.get("ausencias_users_pedidos_datas", []):
                requested_dates_absences.append({"date": d["data"],"type": abs_request["id_tipo_ausencia"]})
    else:
        print("Failed to fetch vacations data:", response.status_code)

    if type_requests == "ferias":
        return f"Vacations requests:, {requested_dates_vacations}"
    elif type_requests == "ausencias":
     return f"Absence requests:{requested_dates_absences}"
    elif type_requests == "both":
        return f"Vacations and Absences: {requested_dates_vacations+requested_dates_absences}"