import json
from langchain_core.tools import tool
from datetime import datetime, timedelta
import requests
from typing_extensions import TypedDict,Annotated

class dateClass(TypedDict):
      date:Annotated[str,...,"The day in YYYY-MM-DD format"]
      type_day:Annotated[int,...,"1 for full day, 0 for half day"]  
      start_time:Annotated[str,...,"If the user requests a half day, ask for the start time (09:00:00) and inform them that the end time will be 4 hours later"]


    

@tool
def add_request(dates: list[dateClass], bearer_token: str, type_leave: str, id_type_absence:int, files: object) -> str:
    """
        
        Only use this tool when the user explicitly confirms the dates.
        Use this after the user confirms the dates.
        Makes a request to book the dates in the HR system.
        

    Args:
        dates (list): List of dictionaries, each with date, type_day(1=full day,0=half day),start_time.
        bearer_token (str): Bearer token for authentication.
        type_leave (str): Type of leave, either "vacation" or "absence".
        id_type_absence (int): ID of the absence type if applicable.
        files (list): List of file objects to be uploaded.

    Returns:
        str: Response from the HR system.

    """
    

    formatted_dates=[]

    for date in dates:
        if date["type_day"]==1:
                formatted_dates.append(
                      {
                            "data": date["date"],
                            "todo_dia": date["type_day"],
                            "total_horas": 8,
                            "hora_inicio": "09:00:00",
                            "hora_fim": "18:00:00"
                      }
                )
        if date["type_day"]==0:
                
                # Convert start_time string to datetime object

                start_time_str = date["start_time"]
                start_time_dt = datetime.strptime(start_time_str, "%H:%M:%S")
                hora_fim_dt = start_time_dt + timedelta(hours=4)
                hora_fim_str = hora_fim_dt.strftime("%H:%M:%S")

                formatted_dates.append(
                      {
                            "data": date["date"],
                            "todo_dia": date["type_day"],
                            "total_horas": 4,
                            "hora_inicio": date["start_time"],
                            "hora_fim": hora_fim_str,
                      }
                )
              




    if type_leave=="vacation":
        type_absence=None

        response=requests.post(
            "https://api-dev.hrstudium.pt/vacations/requests",
            headers={"company": "dev", "Authorization": "Bearer " + bearer_token},
            json={"datas": formatted_dates}

        )

    if type_leave=="absence":
        print(files)

       
        up_files = [
            (None, (file.name, file.read(), file.type))
            for file in files
        ]

        if not up_files:
              
              up_files.append((None, (None, None, None)))

        print("Files to upload",files)
        response=requests.post(
            "https://api-dev.hrstudium.pt/vacations/requests-absences",
            headers={"company": "dev", "Authorization": "Bearer " + bearer_token,"Connection":"keep-alive","Accept-Encoding":"gzip, deflate, br","Accept":"*/*"},
            data={  
                  
                        "id_tipo_ausencia": str(id_type_absence),
                        "datas": json.dumps(formatted_dates),
                        

            },
            files=up_files
            
        )

    
    if response.status_code == 201:
            return "Request successful: " + str(response.json())
    else:
            return f"Request failed with status {response.status_code}: {response.text}"

    




  
    