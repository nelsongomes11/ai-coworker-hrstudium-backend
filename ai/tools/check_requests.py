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
        str: List of requested vacation dates in YYYY-MM-DD format with "type","hora_inicio","hora_fim","estado".
        str: List of requested absence dates in YYYY-MM-DD format with "type","hora_inicio","hora_fim","estado".
    

    """

    print(1)

    requested_dates_vacations = []
    requested_dates_absences = []
    response = requests.get(
        "https://api-dev.hrstudium.pt/vacations",
        headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
    )
    print(2)
    if response.status_code == 200:
        vacation_data = response.json()
        for vac_request in vacation_data.get("pedidos_ferias", []):
            parent_estado = vac_request.get("estado")

            for d in vac_request.get("ferias_users_pedidos_datas", []):
                if parent_estado == "P":
                    estado_str = "Pendente"
                elif parent_estado == "R":
                    estado_str = "Recusada"
                elif parent_estado == "A":
                    d_estado = d.get("estado")
                    estado_str = "Aprovada" if d_estado == "A" else "Recusada"
                else:
                    estado_str = "Desconhecido"

                requested_dates_vacations.append({
                    "date": d["data"],
                    "type": "Férias",
                    "hora_inicio": d["hora_inicio"],
                    "hora_fim": d["hora_fim"],
                    "estado": estado_str
                })

        for abs_request in vacation_data.get("pedidos_ausencias", []):
            parent_estado = abs_request.get("estado")
            tipo = abs_request.get("id_tipo_ausencia", "Desconhecido")

            for d in abs_request.get("ausencias_users_pedidos_datas", []):
                if parent_estado == "P":
                    estado_str = "Pendente"
                elif parent_estado == "R":
                    estado_str = "Recusada"
                elif parent_estado == "A":
                    d_estado = d.get("estado")
                    estado_str = "Aprovada" if d_estado == "A" else "Recusada"
                else:
                    estado_str = "Desconhecido"

                requested_dates_absences.append({
                    "date": d["data"],
                    "type": tipo,
                    "hora_inicio": d["hora_inicio"],
                    "hora_fim": d["hora_fim"],
                    "estado": estado_str
                })
    else:
        print("Failed to fetch vacations data:", response.status_code)

    print(3)
    if type_requests == "ferias":
        return json.dumps(requested_dates_vacations)
    elif type_requests == "ausencias":
     return json.dumps(requested_dates_absences)
    elif type_requests == "both":
        return json.dumps(requested_dates_vacations+requested_dates_absences)