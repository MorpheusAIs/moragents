from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

from llama_index import Document
from llama_index.retrievers import VectorIndexRetriever

from models.embedding import build_llamaindex_index, langchain_embeddings_factory, langchain_cached_embeddings_factory
from rag_assets.contracts_loader import contracts
from models.seq2seq_models import phase2_prompt_template
from config import OLLAMA_BASE_URL

TOP_K_METADATA = 2
TOP_K_ABIS = 5
TOP_K_EXAMPLES = 1


def process_nlq(NLQ):
    # Initialize the data structures and models required for processing the NLQ.
    num_contracts = len(contracts)
    documents_contracts_metadata = [
        Document(text=str(contract[1]["metadata"]),
                 metadata={"fname": contract[0], "abis": contract[1]["abi"]}) for contract in contracts
    ]
    for doc in documents_contracts_metadata:
        doc.excluded_embed_metadata_keys = ["abis", "fname"]
        doc.excluded_llm_metadata_keys = ["abis", "fname"]

    # optim: 41s -> 3s (-38s)
    documents_contracts_metadata_index = build_llamaindex_index(
        documents=documents_contracts_metadata
    )

    documents_contracts_retriever = VectorIndexRetriever(
        index=documents_contracts_metadata_index, similarity_top_k=TOP_K_METADATA
    )

    retrieved_contracts_metadata_with_abis = documents_contracts_retriever.retrieve(NLQ)
    retrieved_contracts_metadata_with_abis = [
        f"The Contract: {contract.node.text}\nThe Contract's ABI:\n{contract.node.metadata['abis']}"
        for contract in retrieved_contracts_metadata_with_abis
    ]

    # slow v (orig: 89s)
    abi_in_memory_vectorstore = FAISS.from_texts(
        retrieved_contracts_metadata_with_abis, embedding=langchain_embeddings_factory())

    abi_retriever = abi_in_memory_vectorstore.as_retriever(search_kwargs={"k": TOP_K_ABIS})

    metamask_examples_loader = DirectoryLoader("rag_assets/metamask_eth_examples", glob="*.txt")
    metamask_examples = metamask_examples_loader.load()

    # slow v (orig: 11s)
    metamask_examples_in_memory_vectorstore = FAISS.from_documents(
        metamask_examples, langchain_embeddings_factory())

    metamask_examples_retriever = metamask_examples_in_memory_vectorstore.as_retriever(
        search_kwargs={"k": TOP_K_EXAMPLES})

    phase2_model = ChatOllama(model="llama2:7b", base_url=OLLAMA_BASE_URL)
    phase2_prompt = ChatPromptTemplate.from_template(phase2_prompt_template)

    setup_and_retrieval = RunnableParallel(
        {
            "nlq": RunnablePassthrough(),
            "context": abi_retriever,
            "metamask_examples": metamask_examples_retriever
        }
    )

    chain = (setup_and_retrieval | phase2_prompt | phase2_model | StrOutputParser())

    val = chain.invoke(NLQ)
    return val
