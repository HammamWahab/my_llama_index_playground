from src.workflows.function_calling import FunctionCallingAgent
from llama_index.utils.workflow import (
    draw_all_possible_flows,
    draw_most_recent_execution,
)

import asyncio


async def main():
    draw_all_possible_flows(FunctionCallingAgent, filename="FunctionCalling_all.html")
    from llama_index.core.tools import FunctionTool
    from llama_index.llms.openai import OpenAI


    def add(x: int, y: int) -> int:
        """Useful function to add two numbers."""
        return x + y


    def multiply(x: int, y: int) -> int:
        """Useful function to multiply two numbers."""
        return x * y


    tools = [
        FunctionTool.from_defaults(add),
        FunctionTool.from_defaults(multiply),
    ]

    agent = FunctionCallingAgent(
        llm=OpenAI(model="gpt-4o-mini"), tools=tools, timeout=120, verbose=True
    )

    ret = await agent.run(input="what is 4*8 ?")
    print(ret['response'])

    draw_most_recent_execution(agent, filename="FunctionCalling_recent.html")
 



if __name__ == "__main__":

    asyncio.run(main())