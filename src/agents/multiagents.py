from dotenv import load_dotenv 

from llama_agents import (
    ControlPlaneServer,
    SimpleMessageQueue,
    AgentOrchestrator, 
    AgentService
)

from llama_index.llms.openai import OpenAI 
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_agents import LocalLauncher, ServerLauncher, CallableMessageConsumer

import logging 

load_dotenv()

logging.getLogger("llama_agent").setLevel(logging.INFO)

# setup infrastructure: message queue + control plane 
message_queue = SimpleMessageQueue()
control_plane = ControlPlaneServer(message_queue=message_queue,
                                    orchestrator=AgentOrchestrator(llm=OpenAI()))


#define the agent with it's corresponding tools 

def get_the_secret_fact() -> str:
    """Returns the secret fact."""
    return "The secret fact is: A baby llama is called a 'Cria'."

tool = FunctionTool.from_defaults(fn=get_the_secret_fact)

worker1 = FunctionCallingAgentWorker.from_tools([tool], llm=OpenAI())
worker2 = FunctionCallingAgentWorker.from_tools([], llm=OpenAI())



agent1 = worker1.as_agent()
agent2 = worker2.as_agent()




# now define an agent as a deployable service 
agent_service1 = AgentService(
    agent=agent1,
    message_queue=message_queue,
    description="Useful for getting the secret fact.",
    service_name="secret_fact_agent",
    host="localhost",
    port="8003"
)


agent_service2 = AgentService(
    agent=agent2,
    message_queue=message_queue,
    description="Useful for getting random dumb fact.",
    service_name="dumb_fact_agent",
    host="localhost",
    port="8004"
)

def handle_result(message)-> str:
    return f"Got result: {message.data}"


human_consumer = CallableMessageConsumer(
    handler=handle_result, message_type="human"
)






#Deployment: for prod 
launcher = ServerLauncher(
    [agent_service1, agent_service2],
    message_queue=message_queue,
    control_plane=control_plane,
    additional_consumers=[human_consumer]
)


launcher.launch_servers()