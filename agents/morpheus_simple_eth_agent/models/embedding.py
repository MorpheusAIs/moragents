import os

from llama_index import ServiceContext, VectorStoreIndex, load_index_from_storage, StorageContext
from llama_index.embeddings import OllamaEmbedding as LlamaIndexOllamaEmbeddings

from langchain.embeddings import OllamaEmbeddings as LangChainOllamaEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore

from config import OLLAMA_BASE_URL

cache_dir_parent_path = "./cache_dirs"

llama_index_contracts_metadata_cache_dir = os.path.join(cache_dir_parent_path,
                                                        'contracts_metadata_cache')

langchain_cache_dir = os.path.join(cache_dir_parent_path, 'langchain_cache')
langchain_store = LocalFileStore(langchain_cache_dir)


def langchain_embeddings_factory():
    return LangChainOllamaEmbeddings(base_url=OLLAMA_BASE_URL)  # uses llama2


def langchain_cached_embeddings_factory():
    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        langchain_embeddings_factory(),
        langchain_store,
        namespace=langchain_embeddings_factory().model
    )

    return cached_embedder


def build_llamaindex_index(documents):
    service_context = ServiceContext.from_defaults(
        embed_model=LlamaIndexOllamaEmbeddings(model_name="llama2", base_url=OLLAMA_BASE_URL),
        llm=None, chunk_size=4096
    )

    if os.path.isdir(llama_index_contracts_metadata_cache_dir):
        # rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir=llama_index_contracts_metadata_cache_dir)
        # load index
        index = load_index_from_storage(storage_context, service_context=service_context, index_id="vector_index")
    else:
        index = VectorStoreIndex.from_documents(
            documents,
            service_context=service_context,
        )
        index.set_index_id("vector_index")
        index.storage_context.persist(llama_index_contracts_metadata_cache_dir)

    return index
