from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import draw_all_possible_flows
from llama_index.utils.workflow import draw_most_recent_execution 

from dotenv import load_dotenv 
import random 
import os 

load_dotenv()


class FailedEvent(Event):
    error: str

class QueryEvent(Event):
    query: str 



class LoopExampleFlow(Workflow):
    @step 
    async def answer_query(
            self, ev: StartEvent | QueryEvent, 
    ) ->  FailedEvent | StopEvent :
        
        query = ev.query 

        random_number = random.randint(0,1)

        if random_number == 0:
            return FailedEvent(error="Failed to answer the query")
        else:
            return StopEvent(result="The answer to your query") 
    
    @step
    async def improve_query(self, ev: FailedEvent) -> QueryEvent | StopEvent:
        random_number = random.randint(0,1)
        if random_number == 0:
            return QueryEvent(error="Here is another query")
        else:
            return StopEvent(result="Failed to fix query") 


