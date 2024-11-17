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
from llama_agents import LocalLauncher

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

worker = FunctionCallingAgentWorker.from_tools([tool], llm=OpenAI())

agent = worker.as_agent()


# now define an agent as a deployable service 
agent_service = AgentService(
    agent=agent,
    message_queue=message_queue,
    description="General Purpose Assistant",
    service_name="assistant"
)



#Deployment: with local launcher 
launcher = LocalLauncher(
    [agent_service],
    control_plane,
    message_queue
)

result = launcher.launch_single("can you give me the secret fact?")

print(result)