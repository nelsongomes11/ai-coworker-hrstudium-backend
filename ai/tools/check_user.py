import json
from langchain_core.tools import tool
from datetime import datetime, timedelta
import requests
from typing_extensions import TypedDict,Annotated



@tool
def check_user(bearer_token: str) -> str:
    """

    Check the status of user vacation info in the HR system.
    ONLY use this when the user SPECIFICALLY asks for their vacation/absence info.
    Use this to check the user info related to vacation/absence available number of days, number of pendent days, number of booked days.
    

    Args:
        bearer_token (str): Bearer token for authentication.
       
    
    Returns:
        str: List of requested vacation dates in YYYY-MM-DD format with "type","hora_inicio","hora_fim","estado".

    

    """

    print("User Info Check")
    user_info = []
    
    response = requests.get(
        "https://api-dev.hrstudium.pt/vacations",
        headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
    )
    print(2)
    if response.status_code == 200:
        vacation_data = response.json()
        user_info = ({
                    "dias_transitados": vacation_data["horas_transitadas"]/8,
                    "dias_ano_atual": vacation_data["horas_ano_atual"]/8,
                    "dias_totais": vacation_data["horas_totais"]/8,
                    "dias_pendentes": vacation_data["horas_pendentes"]/8,
                    "dias_aprovados": vacation_data["horas_aprovadas"]/8,
                    "saldo":vacation_data["horas_por_marcar"]/8,
                })

        
    else:
        print("Failed to fetch user info:", response.status_code)

    print(3)
    return user_info if user_info else "No vacation info available for this user."