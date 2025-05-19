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






def get_chat_model(bearer_token,user_input,uploaded_files,history):

    absence_types=requests.get('https://api-dev.hrstudium.pt/vacations/absences/types',
            headers={
                "company":"dev",
                "Authorization":"Bearer "+bearer_token

        })

    absence_types=absence_types.json() 

    filtered_absence_types = [
            {"id": item["id"], "description": item["description"], "active": item["active"],"documento_obrigatorio": item["documento_obrigatorio"]}
            for item in absence_types if item.get("active") == 1
        ]
    


    llm=ChatOpenAI(model="gpt-4.1-mini")

    llm_with_tools=llm.bind_tools([verify_and_extract_dates,add_request,check_requests])


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
        return first_response.content
    
   

    if first_response.tool_calls:
        print("Used tools!")
        for tool_call in first_response.tool_calls:

            tool_name=tool_call["name"]


            if tool_name=="verify_and_extract_dates":
                
                tool_args = tool_call["args"]
                tool_args["bearer_token"] = bearer_token

                tool_result = verify_and_extract_dates.invoke(tool_args)

                print(f"Tool used : {tool_name}")

            

                second_response = chain_response.invoke({
                        "input": f"Os dias disponíveis são: {tool_result}. Por favor confirme se deseja prosseguir com o agendamento.",
                        "filtered_absence_types": f"{filtered_absence_types}",
                        "date": f"{datetime.now().strftime('%Y-%m-%d')}, {datetime.now().strftime('%A')}",
                        "uploaded_files": f"{uploaded_files}",
                        "history": history.messages,
                    
                    })

                history.add_ai_message(second_response.content)
                print(second_response)
                return second_response.content
            
            elif tool_name=="add_request":

                tool_args = tool_call["args"]
                tool_args["bearer_token"] = bearer_token
                tool_args["files"] = uploaded_files

                tool_result = add_request.invoke(tool_args)

                print(f"Tool used : {tool_name}")

                second_response = chain_response.invoke({
                        "input": f"A mensagem ao submeter pedido foi : {tool_result}.",
                        "filtered_absence_types": f"{filtered_absence_types}",
                        "date": f"{datetime.now().strftime('%Y-%m-%d')}, {datetime.now().strftime('%A')}",
                        "uploaded_files": f"{uploaded_files}",
                        "history": history.messages,
                    
                    })

                history.add_ai_message(second_response.content)
                print(second_response)
                return second_response.content
            
            elif tool_name=="check_requests":

                tool_args = tool_call["args"]
                
                tool_args["bearer_token"] = bearer_token
                tool_args["files"] = uploaded_files

                tool_result = check_requests.invoke(tool_args)

                print(f"Tool used : {tool_name}")
                
            

                second_response = chain_response.invoke({
                        "input": f"Aqui estão os dias marcados: {tool_result}.Se existirem datas, CRIA e envia um objeto com 'mensagem', e 'data' com as datas que existem, se for ausências adiciona o tipo de ausência associado a cada data, sem formatação.",
                        "filtered_absence_types": f"{filtered_absence_types}",
                        "date": f"{datetime.now().strftime('%Y-%m-%d')}, {datetime.now().strftime('%A')}",
                        "uploaded_files": f"{uploaded_files}",
                        "history": history.messages,
                    
                    })
                
                history.add_ai_message(second_response.content)
                print(second_response) 
                return second_response.content

        
                
                
                

            

            



        return "Não consegui processar os resultados da tool",None
           

    else:
        print("Didn't use tools!")
        return first_response.content,None
    
    

