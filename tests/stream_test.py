
from operator import itemgetter
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ai.prompts.system_prompts import coworker_system_prompt

from langchain_community.chat_message_histories import StreamlitChatMessageHistory


import requests
from datetime import datetime


from ai.tools.extract_dates import verify_and_extract_dates
from ai.tools.add_request import add_request
from ai.tools.check_requests import check_requests

import time





def stream_test(input):

    start_time=time.perf_counter()


    llm=ChatOpenAI(model="gpt-4.1-nano",streaming=True)



    """ response2=llm.invoke(input)
    print("Response 2: ", response2) """

   
    

    

    response=llm.stream(input)

    for chunk in response:
        print(chunk.content, end="", flush=True)
    
    end_time=time.perf_counter()
    print(f"Time taken: {end_time - start_time} seconds")

    



stream_test("Write me a 400 word essay about the movie perfect days by wim wenders.")