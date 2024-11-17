from llama_index.core.workflow import Event

class JokeEvent(Event):
    joke: str