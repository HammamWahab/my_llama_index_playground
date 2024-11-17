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



class WaitExampleFlow(Workflow):
    @step
    async def setup(self, ctx: Context, ev: StartEvent) -> StopEvent:
        if hasattr(ev, "data"):
            await ctx.set("data", ev.data)
        return StopEvent(result=None)
        
    
    @step
    async def query(self, ctx: Context, ev: StartEvent) -> StopEvent:
        if hasattr(ev, "query"):
            # do we have any data?
            if hasattr(self, "data"):
                data = await ctx.get("data")
                return StopEvent(result=f"Got the data {data}")
            else:
                # there's non data yet
                return None
        else:
            # this isn't a query
            return None

    
