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


class QueryEvent(Event):
    query: str 



class GloabalExampleFlow(Workflow):

    @step
    async def setup(self, ctx: Context, ev: StartEvent) -> QueryEvent:
        await ctx.set("some_database", [0,1,2])
        return QueryEvent(query=ev.query)
    
    @step 
    async def query(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        data = await ctx.get("some_database")
        result = f"Query {ev.query}: \n The answer to your query is {data[1]}"
        return StopEvent(result=result)
    

