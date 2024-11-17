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


class InputEvent(Event):
    input: str 

class SetupEvent(Event):
    error: bool 

class QueryEvent(Event):
    query: str 


class CollectExampleFlow(Workflow):
    @step
    async def setup(self, ctx: Context, ev: StartEvent) -> SetupEvent:
        # generically start everything up
        if not hasattr(self, "setup") or not self.setup:
            self.setup = True
            print("I got set up")
        return SetupEvent(error=False)

    @step
    async def collect_input(self, ev: StartEvent) -> InputEvent:
        if hasattr(ev, "input"):
            # perhaps validate the input
            print("I got some input")
            return InputEvent(input=ev.input)

    @step
    async def parse_query(self, ev: StartEvent) -> QueryEvent:
        if hasattr(ev, "query"):
            # parse the query in some way
            print("I got a query")
            return QueryEvent(query=ev.query)

    @step
    async def run_query(
        self, ctx: Context, ev: InputEvent | SetupEvent | QueryEvent
    ) -> StopEvent | None:
        ready = ctx.collect_events(ev, [QueryEvent, InputEvent, SetupEvent])
        if ready is None:
            print("Not enough events yet")
            return None

        # run the query
        print("Now I have all the events")
        print(ready)

        result = f"Ran query '{ready[0].query}' on input '{ready[1].input}'"
        return StopEvent(result=result)





    

