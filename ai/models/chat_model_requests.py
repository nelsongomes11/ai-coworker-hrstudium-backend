from operator import itemgetter
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from prompts.system_prompts import coworker_system_prompt

from langchain_community.chat_message_histories import StreamlitChatMessageHistory


import requests
from datetime import datetime


from tools.extract_dates import verify_and_extract_dates
from tools.add_request import add_request
from tools.check_requests import check_requests
from tools.check_user import check_user






def get_chat_model(bearer_token,user_input,uploaded_files,history):

    absence_types=requests.get('https://api-dev.hrstudium.pt/vacations/absences/types',
            headers={
                "company":"dev",
                "Authorization":"Bearer "+bearer_token

        })

    absence_types=absence_types.json() 

    filtered_absence_types = [
            {"id": item["id"], "description": item["description"], "active": item["active"],"document_required": item["documento_obrigatorio"]}
            for item in absence_types if item.get("active") == 1
        ]
    


    llm=ChatOpenAI(model="gpt-4.1-mini")

    llm_with_tools=llm.bind_tools([verify_and_extract_dates,add_request,check_requests,check_user])


    history.add_user_message(user_input)

   

    chat_prompt=ChatPromptTemplate(
        [
            ("system",coworker_system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human","{input}")
        ]
    )

    

    chain=  {"input": itemgetter("input"),"filtered_absence_types":itemgetter("filtered_absence_types"),"date": itemgetter("date"),"uploaded_files":itemgetter("uploaded_files"),"history": itemgetter("history"),}  | chat_prompt | llm_with_tools

    chain_response=  {"input": itemgetter("input"),"filtered_absence_types":itemgetter("filtered_absence_types"),"date": itemgetter("date"),"uploaded_files":itemgetter("uploaded_files"),"history": itemgetter("history"),}  | chat_prompt | llm


    first_response=chain.invoke({"input":user_input,
                  "filtered_absence_types": f"{filtered_absence_types}",
                  "date": f"{datetime.now().strftime('%Y-%m-%d')}, {datetime.now().strftime('%A')}",
                  "uploaded_files": f"{uploaded_files}",
                  "history": history.messages
                })

    if first_response.content:
        history.add_ai_message(first_response.content)
        print(first_response.content)
        return first_response.content,None
    
   

    if first_response.tool_calls:
        print("Used tools!")
        for tool_call in first_response.tool_calls:

            tool_name=tool_call["name"]
            tool_args = tool_call["args"]
            tool_args["bearer_token"] = bearer_token
            tool_args["files"] = uploaded_files


            if tool_name=="verify_and_extract_dates":
                
                tool_result = verify_and_extract_dates.invoke(tool_args)
                print(f"Tool used : {tool_name}")
                check_true = bool(tool_result.get("allowed_dates"))
                
                follow_up_input=f"The available days are: {tool_result}.NOW if the date is available ASK the user to confirm if he wishes to submit the request (add_request tool).!."

            elif tool_name=="add_request":

                tool_result = add_request.invoke(tool_args)
                print(f"Tool used : {tool_name}")
                follow_up_input= f"The message when submitting the request was : {tool_result}."
            
            elif tool_name=="check_requests":

                tool_result = check_requests.invoke(tool_args)
                print(f"Tool used : {tool_name}")
                follow_up_input= f"Here are the requests: {tool_result}.If there's any dates, ALWAYS CREATE AND SEND an JSON with the keys 'message', and 'dates' with the dates that exist. Each entry must contain the keys 'date', 'type', 'hora_inicio', 'hora_fim', e 'estado'."

            elif tool_name=="check_user":
                tool_result = check_user.invoke(tool_args)
                print(f"Tool used : {tool_name}")
                follow_up_input= f"Here is the user info: {tool_result}."
                

            second_response = chain_response.invoke({
                            "input": follow_up_input,
                            "filtered_absence_types": f"{filtered_absence_types}",
                            "date": f"{datetime.now().strftime('%Y-%m-%d')}, {datetime.now().strftime('%A')}",
                            "uploaded_files": f"{uploaded_files}",
                            "history": history.messages,
                        })  
                
            try:
                    content_dict = json.loads(second_response.content)
                    content_dict["tipo"] = "requests_table"  
                      #content_dict= {"tipo" : "requests_table",**content_dict}
                    final_response = json.dumps(content_dict, ensure_ascii=False)  
            except Exception as e:
                    
                    final_response = second_response.content 

            history.add_ai_message(final_response)
            if (tool_name=="verify_and_extract_dates" and check_true) or (tool_name=="add_request") or (tool_name=="check_requests"):
                print(final_response,tool_name)
                return final_response,tool_name
            else:
                return final_response,None
                 
                
            
           
        

                
               

        
                
                
                

            

            



        return "Não consegui processar os resultados da tool",None
           

    else:
        print("Didn't use tools!")
        return first_response.content,None
    
    

