from urllib import response
from llama_index.core.workflow import (
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent,
    step,
)
from llama_index.core.schema import NodeWithScore
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.postprocessor.llm_rerank import LLMRerank 
from llama_index.llms.openai import OpenAI
from llama_index.core.response_synthesizers import CompactAndRefine
from dotenv import load_dotenv


load_dotenv()

class RetrieverEvent(Event):
    "Result of running retrieval"
    nodes: list[NodeWithScore]

class RerankEvent(Event):
    "Result of reranking on retrieval nodes"
    nodes: list[NodeWithScore]


class RagWorkflow(Workflow):

    @step
    async def ingest(self, ctx: Context, ev: StartEvent)-> StopEvent:
        """Entry point to ingest a document, triggered by a StartEvent with `dirname`."""
        dirname = ev.get("dirname")
        if not dirname:
            return None 
        
        documents = SimpleDirectoryReader(dirname).load_data()
        index = VectorStoreIndex.from_documents(
            documents=documents,
            embed_model=OpenAIEmbedding(model_name="text-embedding-3-small")
        )

        return StopEvent(result=index)
    
    @step 
    async def retrieve(self, ctx: Context, ev: StartEvent)-> RetrieverEvent:
        "Entry point for RAG, triggered by a StartEvent with `query`."
        query = ev.get("query")
        index = ev.get("index")

        if not query:
            return None
        
        await ctx.set("query", query)


        if index is None:
            print("no index available, load documennts before query")
            return None 
        
        retriever = index.as_retriever(similarity_top_k=2)

        nodes = await retriever.aretrieve(query)

        print(f"Retrieved {len(nodes)} nodes.")

        return RetrieverEvent(nodes=nodes)
    
    @step
    async def rerank(self, ctx: Context, ev: RetrieverEvent) -> RerankEvent:

        ranker = LLMRerank(
            choice_batch_size=5,
            top_n=3,
            llm=OpenAI(model="gpt-4o-mini")
        )   

        new_nodes = ranker.postprocess_nodes(
            nodes=ev.nodes, 
            query_str=await ctx.get("query", default=None)
        )
        print(f"Reranked Nodes to {len(new_nodes)}")

        return RerankEvent(nodes=new_nodes)
    
    @step
    async def synthesize(self, ctx: Context, ev: RerankEvent) -> StopEvent:
        """Return a streaming response using reranked nodes."""
        llm = OpenAI(model="gpt-4o-mini")
        summarizer = CompactAndRefine(
            llm=llm, 
            streaming=True, 
            verbose=True, 
        )

        query = await ctx.get("query", default=True)


        response = await summarizer.asynthesize(query, nodes=ev.nodes)

        return StopEvent(result=response)






# async def main():
#     draw_all_possible_flows(RagWorkflow, filename="RagFlow_all.html")

#     w = RagWorkflow(timeout=10, verbose=True)
#     index = await w.run(dirname="data")
#     result = await w.run(query="What is the summary of this paper?", index=index)
#     async for chunk in result.async_response_gen():
#         print(chunk, end="", flush=True)
#     # result = await w.run(query="What's LlamaIndex?")
#     # if result is None:
#     #     print("No you can't")
#     draw_most_recent_execution(w, filename="RagFlow_recent.html")
#     # print("-------")
#     # result = await w.run(data="Yes you can")
#     # print(result)
#     # print("-------")
#     # result = await w.run(query="What's LlamaIndex?")
#     # print(result)
#     # draw_most_recent_execution(w, filename="wait_workflow_with_data_recent.html")

    



# if __name__ == "__main__":

#     asyncio.run(main())






