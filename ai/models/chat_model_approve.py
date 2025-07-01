from operator import itemgetter
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json


from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from prompts.system_prompts import coworker_system_approve_prompt

from langchain_community.chat_message_histories import StreamlitChatMessageHistory


import requests
from datetime import datetime


from tools.check_approve_requests import check_requests_to_approve
from tools.request_decision import request_decision






def get_chat_model_approve(bearer_token,user_input,history):

    
    llm=ChatOpenAI(model="gpt-4.1-mini")
    llm_with_tools=llm.bind_tools([check_requests_to_approve,request_decision])

    history.add_user_message(user_input)

    chat_prompt=ChatPromptTemplate(
        [
            ("system",coworker_system_approve_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human","{input}")
        ]
    )

    

    chain=  {"input": itemgetter("input"),"history": itemgetter("history"),}  | chat_prompt | llm_with_tools
    
    chain_response={"input": itemgetter("input"),"history": itemgetter("history"),}  | chat_prompt | llm

    
    first_response=chain.invoke({
                  "input":user_input,
                  "history": history.messages
                })
    


    
    if first_response.content:
        history.add_ai_message(first_response.content)
        print(first_response.content)
        return first_response.content

    if first_response.tool_calls:
        print("Used tools!")
        for tool_call in first_response.tool_calls:

            tool_name=tool_call["name"]
            tool_args = tool_call["args"]
            tool_args["bearer_token"] = bearer_token


            if tool_name=="check_requests_to_approve":
                
                
                
                tool_result = check_requests_to_approve.invoke(tool_args)
                print(tool_result)
                print(f"Tool used : {tool_name}")
                follow_up_input= f"Here are the requests: {tool_result}. If there's any dates, ALWAYS CREATE AND SNED an JSON with the keys 'message', and 'dates' with the dates that exist. Each entry must contain the keys 'id','nome_completo', 'data', e 'tipo'."
                


            elif tool_name=="request_decision":
                
                
                tool_result = request_decision.invoke(tool_args)
                print(f"Tool used : {tool_name}")     
                follow_up_input=f"The message submitting the request was : {tool_result}."      


                
            

            second_response = chain_response.invoke({
                        "input": follow_up_input,
                        "history": history.messages,
                    
            })
                

                
            try:
                    content_dict = json.loads(second_response.content)
                    content_dict["tipo"] = "approve_table"  
                    final_response = json.dumps(content_dict, ensure_ascii=False)  
            except Exception as e:
                    print("Error parsing response content:", e)
                    final_response = second_response.content 

            history.add_ai_message(final_response)
            print(final_response)
            return final_response
            
          

               
           
            

            



        return "Não consegui processar os resultados da tool"
           

    else:
        print("Didn't use tools!")
        return first_response.content
    
    

