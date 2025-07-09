import json
from langchain_core.tools import tool
from datetime import datetime, timedelta
import requests
from typing_extensions import TypedDict,Annotated


@tool
def check_requests_to_approve(bearer_token: str,type_requests: str) -> str:
    """

    Check the status of requests to approve in the HR system.
    Only use this when the user SPECIFICALLY asks to see the vacation  and absence requests they have to approve.
    

    Args:
        bearer_token (str): Bearer token for authentication.
        type_requests (str): Type of requests to check, either "vacation" or "absence".
    
    Returns:
        list: List of requests to approve, including the request ID and dates.

    
    """
    
    

    
    if type_requests=="vacation":

        ## Fetch requests to approve
        response = requests.get(
            "https://api-dev.hrstudium.pt/vacations/requests-to-approve",
            headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
        )
        if response.status_code == 200:
            

            data= response.json()
            print(data)

            filtered_requests=[
                {
                    "id:": item["id"],
                    "full_name":item["criador"]["full_name"],
                    "datas": [
                            {
                                "data": d["data"],
                                "hora_inicio": d["hora_inicio"],
                                "hora_fim": d["hora_fim"]
                            }
                            for d in item["datas"]
                    ],
                    "tipo": "Férias"

                }
                for item in data
            ]
            print(1)
            return "Vacations requests", json.dumps(filtered_requests)
        else:
            print(2)
            print("Failed to fetch requests to approve:", response.status_code)
            return("No requests to approve")
    
    elif type_requests=="absence":

        ## Fetch absence requests to approve

        response = requests.get(
            "https://api-dev.hrstudium.pt/vacations/requests-absences-to-approve",
            headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
        )
        if response.status_code == 200:
            data= response.json()

            filtered_requests=[
                {
                    "id:": item["id"],
                    "full_name":item["criador"]["full_name"],
                    "datas": [
                            {
                                "data": d["data"],
                                "hora_inicio": d["hora_inicio"],
                                "hora_fim": d["hora_fim"]
                            }
                            for d in item["datas"]
                    ],
                    "tipo": item.get("tipo", "Tipo não especificado"),

                }
                for item in data
            ]
            print(1)
            return "Absences requests",json.dumps(filtered_requests)
        else:
            print(2)
            print("Failed to fetch requests to approve:", response.status_code)
            return("No requests to approve")


        
    
    
    