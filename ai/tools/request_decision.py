import json
from langchain_core.tools import tool
from datetime import datetime, timedelta
import requests
from typing_extensions import TypedDict,Annotated

class dateClass(TypedDict):
      data:Annotated[str,...,"The day in YYYY-MM-DD format"]
      aprovada:Annotated[str,...,"S for approved, N for rejected"]


      


    

@tool
def request_decision(bearer_token:str,dates: list[dateClass], id_pedido:int, type_requests:str) -> str:
    """
        
        Only use this tool when the user explicitly confirms he wants to approve or reject dates from a specific request.
        The request might be either "vacation" or "absence"
        Use this after the user asks to approve or reject dates.
        Approves or rejects requests for vacations in the HR system.
        

    Args:
        dates (list): List of dictionaries, each with date,aprovada("S" for approved, "N" for rejected).
        id_pedido (int): ID of the request to be approved or rejected.
        bearer_token (str): Bearer token for authentication.
        type_requests (str): Type of decision, either "vacation" requests or "absence" requests.

    Returns:
        str: Response from the HR system.

    """

    if type_requests=="vacation":

        print("https://api-dev.hrstudium.pt/vacations/request/"+str(id_pedido))
        response=requests.get(
            "https://api-dev.hrstudium.pt/vacations/request/"+str(id_pedido),
            headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
        )
        if response.status_code == 200:
            request_data= response.json()

            formatted_dates=[]

            datas_list=request_data.get("ferias_users_pedidos_datas",[])

        


            for date in dates:
                    match_date=next((item for item in datas_list if item["data"] == date["data"]), None)

                    if match_date:
                        formatted_dates.append(
                            {
                                    "id":match_date["id"],
                                    "id_user_pedido":id_pedido,
                                    "data": date["data"],
                                    "estado": "A",
                                    "aprovada": date["aprovada"],
                                    "hora_inicio": match_date["hora_inicio"],
                                    "hora_fim": match_date["hora_fim"],
                                    "horas" : match_date["horas"],
                                    
                            }
                        )
            
            print(formatted_dates)

            formatted_request={
                "id_user": request_data["id_user"],
                "observacoes": "",
                "etapas": request_data["etapas"],
                "datas": formatted_dates
            }

            
        
            response=requests.put(
                "https://api-dev.hrstudium.pt/vacations/request/"+str(id_pedido),
                headers={"company": "dev", "Authorization": "Bearer " + bearer_token},
                json=formatted_request
            )

            if response.status_code == 200:
                return "Request successful: " + str(response.json())
            else:
                    return f"Request failed with status {response.status_code}: {response.text}"

        else:
            return f"Failed to fetch request data with status {response.status_code}: {response.text}"  

    elif type_requests=="absence":
        

        print("https://api-dev.hrstudium.pt/vacations/request-absence/"+str(id_pedido))
        response=requests.get(
            "https://api-dev.hrstudium.pt/vacations/request-absence/"+str(id_pedido),
            headers={"company": "dev", "Authorization": "Bearer " + bearer_token}
        )
        if response.status_code == 200:
            request_data= response.json()

            formatted_dates=[]

            datas_list=request_data.get("ausencias_users_pedidos_datas",[])

        


            for date in dates:
                    match_date=next((item for item in datas_list if item["data"] == date["data"]), None)

                    if match_date:
                        formatted_dates.append(
                            {
                                    "id":match_date["id"],
                                    "id_user_pedido":id_pedido,
                                    "data": date["data"],
                                    "estado": "A",
                                    "aprovada": date["aprovada"],
                                    "hora_inicio": match_date["hora_inicio"],
                                    "hora_fim": match_date["hora_fim"],
                                    "horas" : match_date["horas"],
                                    
                            }
                        )
            
            print(formatted_dates)

            formatted_request={
                "id_user": request_data["id_user"],
                "observacoes": "",
                "etapas": request_data["etapas"],
                "datas": formatted_dates
            }

            
        
            response=requests.put(
                "https://api-dev.hrstudium.pt/vacations/request-absence/"+str(id_pedido),
                headers={"company": "dev", "Authorization": "Bearer " + bearer_token},
                json=formatted_request
            )

            if response.status_code == 200:
                return "Request successful: " + str(response.json())
            else:
                    return f"Request failed with status {response.status_code}: {response.text}"

        else:
            return f"Failed to fetch request data with status {response.status_code}: {response.text}"  
        

            

        


    




  
    