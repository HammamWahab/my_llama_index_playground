from typing import Any, List 

from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step
from llama_index.core.llms import ChatMessage
from llama_index.core.llms.function_calling import FunctionCallingLLM 
from llama_index.core.tools import ToolSelection,ToolOutput
from llama_index.core.tools.types import BaseTool
from llama_index.core.memory import ChatMemoryBuffer 
from llama_index.llms.openai import OpenAI 



from dotenv import load_dotenv

load_dotenv()

class InputEvent(Event):
    input: List[ChatMessage]

class ToolCallEvent(Event):
    tool_calls: List[ToolSelection]

class FunctionOutputEvent(Event):
    output: ToolOutput





class FunctionCallingAgent(Workflow):
    """ prepare chat history 
    handle input and add tools 
    prepare tool calling 
    get response from llms """

    def __init__(self, 
                 *args: Any , 
                 llm: FunctionCallingLLM | None = None,
                 tools: List[BaseTool] | None = None,
                 **kwargs: Any 
                 )-> None:
        """
        for function calling agent, you need to have the following compontents: 
        - a set of tools that you can later call and execute them
        - the LLM with it's : 
            - chat history, by including memory buffer 
            - sources which includes the outouts of the executed tools  


        """
        super().__init__(*args, **kwargs)
        self.tools = tools  or []
        self.llm = llm or OpenAI()
        assert self.llm.metadata.is_function_calling_model

        self.memory = ChatMemoryBuffer.from_defaults(llm=self.llm)
        self.sources = []
    
    @step 
    async def prepare_chat_history(self, ev: StartEvent) -> InputEvent:

        """ 
        Here, we take user input, and restructure it in llama index's chat message format.
        We also pack all chat history in a list and return it in the input event. 

        """

        self.sources = []

        user_message = ev.input 

        user_message = ChatMessage(role="user", content=user_message)

        self.memory.put(user_message)

        chat_history = self.memory.get()

        return InputEvent(input=chat_history)
       
    @step 
    async def handle_llm_input(self, ev: InputEvent) -> ToolCallEvent | StopEvent:
        """ 
        Here, we handle the chat history, exctract tool call prompts,
        pack them again in history, then return the extracted tool calls
        for execution (if any)..  
        """
        chat_history = ev.input 

        response = await self.llm.achat_with_tools(
            tools = self.tools, 
            chat_history=chat_history
        )

        self.memory.put(response.message) #appearantly response.messagne returns a ChatMessage


        tool_calls = self.llm.get_tool_calls_from_response(
            response=response, 
            error_on_no_tool_call=False 
        )


        if not tool_calls:
            return StopEvent(result={
                "response": response, 
                "sources": [*self.sources]
            })
        
        else: 
            return ToolCallEvent(tool_calls=tool_calls)
        
    @step 
    async def handle_tool_calls(self, ev: ToolCallEvent) -> InputEvent:

        """ 
        Here, we execute the tools that we previously defined, 
        we check if they exist in our tools pool, then we try to execute them. 
        we try to handle error outcomes as well.

        Eventually, we pack outputs in chat format and share it as InputEvent 
        """
        tools_msgs = []


        #tools selected from llm 
        tool_calls = ev.tool_calls

        # all tools 
        tools_by_name = {tool.metadata.get_name(): tool for tool in self.tools}


        #iterate through tool_calls 
        for tool_call in tool_calls:
            tool = tools_by_name.get(tool_call.tool_name)
            additional_kwargs={
                "tool_call_id": tool_call.tool_id,
                "name": tool.metadata.get_name() # should this be the same as tool_call.tool_name
            }

            #if tool does not exist, add info to chat messages list, and continue to next tool
            if not tool:
                tools_msgs.append(
                    ChatMessage(
                        role="tool",
                        content=f"Tool {tool_call} does not exist.",
                        additional_kwargs=additional_kwargs
                    )
                )

                continue 
            
            try: 
                tool_output = tool(**tool_call.tool_kwargs)
                self.sources.append(tool_output)

                tools_msgs.append(
                    ChatMessage(
                        role="tool",
                        content=tool_output.content,
                        additional_kwargs=additional_kwargs
                    )
                )
            except Exception as e: 
                tools_msgs.append(
                    ChatMessage(
                        role="tool",
                        content=f"Error while executing {tool_call.tool_name}: {e}",
                        additional_kwargs=additional_kwargs
                    )
                )

        
        for msg in tools_msgs:
            self.memory.put(msg)

        chat_history = self.memory.get()

        return InputEvent(input=chat_history)





# from llama_index.core.tools import FunctionTool
# from llama_index.llms.openai import OpenAI


# def add(x: int, y: int) -> int:
#     """Useful function to add two numbers."""
#     return x + y


# def multiply(x: int, y: int) -> int:
#     """Useful function to multiply two numbers."""
#     return x * y


# tools = [
#     FunctionTool.from_defaults(add),
#     FunctionTool.from_defaults(multiply),
# ]

# agent = FuncationCallingAgent(
#     llm=OpenAI(model="gpt-4o-mini"), tools=tools, timeout=120, verbose=True
# )

# ret = await agent.run(input="Hello!")





            








        return 
        





    


