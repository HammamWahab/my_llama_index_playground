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
import os 

load_dotenv()

class OpenAIGenerator(Workflow):
    @step 
    async def generate(self, ev: StartEvent) -> StopEvent:
        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await llm.acomplete(ev.query)
        return StopEvent(result=str(response))
    
# async def main():
#     draw_all_possible_flows(OpenAIGenerator, filename="open_ai_generator_all.html")

#     w = OpenAIGenerator()
#     result = await w.run(query="Hi, how are you?")
#     draw_most_recent_execution(w, filename="open_ai_generator_recent.html")
#     print(result)
