__version__ = "dev"


import functools
import os
import reprlib
import time
import traceback
from pprint import pformat

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    CSVLoader,
    DirectoryLoader,
    JSONLoader,
    PyPDFLoader,
    TextLoader,
    WebBaseLoader,
)
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import FAISS, DocArrayInMemorySearch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama, OllamaLLM
from transformers import AutoTokenizer

loaders_map = {
    ".csv": CSVLoader,
    ".json": JSONLoader,
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
    ".ini": TextLoader,
}

vectorstore_map = {
    "Chroma": Chroma,
    "FAISS": FAISS,
    "DocArrayInMemorySearch": DocArrayInMemorySearch,
}


def clock(func):
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        arg_list = []
        arg_types = str, int, float, complex, tuple, list, dict, set
        if args and len(args) > 1:
            arg_list.append(
                ", ".join(repr(arg) for arg in args if isinstance(arg, (arg_types)))
            )
        if kwargs:
            pairs = [f"{k}={w}" for k, w in sorted(kwargs.items())]
            arg_list.append(", ".join(pairs))
        arg_str = ", ".join(arg_list)
        print(
            "[%0.4fs] %s(%s) -> %r "
            % (elapsed, func.__name__, arg_str, reprlib.repr(result))
        )
        return result

    return clocked


def aclock(func):
    @functools.wraps(func)
    async def clocked(*args, **kwargs):
        t0 = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - t0
        arg_list = []
        arg_types = str, int, float, complex, tuple, list, dict, set
        if args and len(args) > 1:
            arg_list.append(
                ", ".join(repr(arg) for arg in args if isinstance(arg, (arg_types)))
            )
        if kwargs:
            pairs = [f"{k}={w}" for k, w in sorted(kwargs.items())]
            arg_list.append(", ".join(pairs))
        arg_str = ", ".join(arg_list)
        print(
            "[%0.4fs] %s(%s) -> %r "
            % (elapsed, func.__name__, arg_str, reprlib.repr(result))
        )
        return result

    return clocked


def execute(func):
    """
    Note: Used in testing python scripts, not in pytest, to test different models in options dictionary
    Decorator used in executing a function
    options: embedding, model, models, repeatcnt
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        options = kwargs
        # This is needed to work with pytest
        if "options" in options:
            options = options["options"]
        elapsed = None
        if options["model"] is not None:
            options["models"] = [options["model"]]
        for i in range(options["repeatcnt"]):
            for model in options["models"]:
                options["model"] = model
                print(
                    f"\n\n\n{'=' * 80}\ni {i}: model: {model} embedding: {options['embedding']}\n{'-' * 80}"
                )
                try:
                    t0 = time.time()
                    result = func(options)
                    elapsed = time.time() - t0
                except Exception as e:
                    print(f"\n\n\n>>>-error<<<: {e}")
                    traceback.print_exception(type(e), e, e.__traceback__)
                    result = None
                print(
                    f"\n{'-' * 80}\ni {i}: model: {model} embedding: {options['embedding']} {elapsed} seconds\n{'=' * 80}\n\n\n"
                )
        return result

    return wrapper


@clock
def get_llm(options):
    """
    Create an instance of llm using Ollama based on the name of the model
    options: model, llm_type, temperature
    """
    if options["llm_type"] == "llm":
        llm = OllamaLLM(
            model=options["model"],
            temperature=options["temperature"],
            callbacks=[StreamingStdOutCallbackHandler()],
        )
    elif options["llm_type"] == "chat":
        llm = ChatOllama(
            model=options["model"],
            temperature=options["temperature"],
            callbacks=[StreamingStdOutCallbackHandler()],
        )
    return llm


@clock
def get_documents_by_path(pathname):
    """
    Retrieve the documents based on pathname
    options: pathname
    """
    print(f"1 pathname {pathname}")
    if os.path.isdir(pathname):
        docs = _get_documents_by_dir(pathname)
    elif os.path.isfile(pathname):
        loader = [loaders_map[key] for key in loaders_map if pathname.endswith(key)][0]
        loader = loader(pathname)
        docs = loader.load_and_split()
    elif pathname.startswith("http:") or pathname.startswith("https:"):
        loader = WebBaseLoader(pathname)
        docs = loader.load()
    return docs


@clock
def create_memory_vectordb(options):
    """
    Store the documents in an in-mmeory vectorstore based on the pathname
    options: embedding, embedmodel, pathname, persist_directory, vectorstore
    """
    if "documents" in options:
        documents = options["documents"]
    else:
        documents = get_documents_by_path(options["pathname"])
    embeddings = get_embeddings(options)
    vectorstore = vectorstore_map[options["vectorstore"]]
    vectordb = vectorstore.from_documents(documents, embeddings)
    return vectordb


@clock
def create_disk_vectordb(options, index_flag=False):
    """
    Store the documents in an in-disk vectorstore based on the pathnamehuggingface/tokenizers: The current process just got forked, after parallelism has already been used. Disabling parallelism to avoid deadlocks...

    options: embedding, embedmodel, pathname, persist_directory, vectorstore, documents
    """
    # Use the documents if provided
    if "documents" in options:
        documents = options["documents"]
    else:
        documents = get_documents_by_path(options["pathname"])
    embeddings = get_embeddings(options)
    persist_directory = f"{options['persist_directory']}_{options['embedding']}"
    vectorstore = options["vectorstore"]
    vectorstore_cls = vectorstore_map[vectorstore]
    if vectorstore == "Chroma":
        index = VectorstoreIndexCreator(
            vectorstore_cls=vectorstore_cls,
            embedding=embeddings,
            vectorstore_kwargs={"persist_directory": persist_directory},
        ).from_documents(documents)
    elif vectorstore == "FAISS":
        index = VectorstoreIndexCreator(
            vectorstore_cls=vectorstore_cls,
            embedding=embeddings,
        ).from_documents(documents)
        index.vectorstore.save_local(persist_directory)
    if not index_flag:
        vectordb = index.vectorstore
        return vectordb
    else:
        return index


@clock
def create_vectordb(options, index_flag=False):
    """
    Create a vectordb with data pointed to by pathname.
    The supported vectordb_type is disk or memory.
    On default return the newly created vectordb or we can return the index if index_flag is set to True.
    """
    vectordb_type = options["vectordb_type"]
    return (
        create_disk_vectordb(options, index_flag)
        if vectordb_type == "disk"
        else create_memory_vectordb(options)
    )


@clock
def create_vectordb_all(options, index_flag=False):
    """
    Create all vectordb with data pointed to by embeddings and pathname. Supported embeddings are: chroma, gpt4all.
    """
    vectordbs = []
    for embedding in options["embeddings"]:
        options["embedding"] = embedding
        vectordb = create_vectordb(options)
        vectordbs.append(vectordb)
    return vectordbs


@clock
def get_vectordb(options):
    """
    Return the vectordb based on the embedding and embedmodel
    options: embedding, embedmodel, persist_directory
    """
    embeddings = get_embeddings(options)
    persist_directory = f"{options['persist_directory']}_{options['embedding']}"
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    return vectordb


@clock
def get_embeddings(options):
    """
        Retrieve the model embedding based on the embedding type
        options: embedding, embedmodel
    #           else GPT4AllEmbeddings(model_name=embedmodel)
    """
    embedding = options["embedding"]
    embedmodel = options["embedmodel"]
    if embedding == "chroma":
        embedding = (
            HuggingFaceEmbeddings()
            if embedmodel is None
            else HuggingFaceEmbeddings(model_name=embedmodel)
        )
    elif embedding == "gpt4all":
        embedmodel = "all-MiniLM-L6-v2.gguf2.f16.gguf"
        gpt4all_kwargs = {"allow_download": "True"}
        embedding = (
            GPT4AllEmbeddings()
            if embedmodel is None
            else GPT4AllEmbeddings(model_name=embedmodel, gpt4all_kwargs=gpt4all_kwargs)
        )
    elif embedding == "huggingface":
        embedding = (
            HuggingFaceEmbeddings()
            if embedmodel is None
            else HuggingFaceEmbeddings(
                model_name=embedmodel, model_kwargs={"device": "cuda"}
            )
        )
    else:
        print(f"Error: Unsupported embedding {embedding}")
        os._exit(1)
    return embedding


@clock
def get_loaders_by_dir(dir_path):
    """
    Retrieve the loader for pdf, csv and txt
    """
    loaders = [
        DirectoryLoader(dir_path, glob=f"**/*{key}", loader_cls=loaders_map[key])
        for key in loaders_map
    ]
    return loaders


@clock
def _get_documents_by_dir(dir_path):
    """
    Retrieve the list of documents based on the file path of the directory
    Returns a list of Document
    """
    loaders = [
        DirectoryLoader(dir_path, glob=f"**/*{key}", loader_cls=loaders_map[key])
        for key in loaders_map
    ]
    documents = [loader.load() for loader in loaders]
    docs = []
    for doc in documents:
        docs.extend(doc)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, chunk_overlap=100, separators=["\n\n", "\n", "\\. ", " ", ""]
    )
    texts = text_splitter.split_documents(documents=docs)
    return texts


def printit(label, values):
    try:
        print(
            f"\n{'#' * 80}\n{'-' * 80}\nlabel: >>>{label}<<<:\nvalues: >>>>>>{str(pformat(values))}<<<<<<\nlen: {len(values)}\n{'-' * 80}\n{'#-' * 40}\n"
        )
    except:
        print(
            f"\n{'#' * 80}\n{'-' * 80}\nlabel: >>>{label}<<<:\nvalues: >>>>>>{str(pformat(values))}<<<<<<\n{'-' * 80}\n{'#-' * 40}\n"
        )


@clock
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_persist_directory(options):
    return f"{options['persist_directory']}_{options['embedding']}"


@clock
def count_tokens(values):
    """
    Count the number of tokens
    """
    tokenizer = AutoTokenizer.from_pretrained("google/flan-ul2")
    if isinstance(values, str):
        cnt = len(tokenizer.tokenize(values))
    elif isinstance(values, dict):
        cnt = len(tokenizer.tokenize(values["result"]))
    else:
        raise RuntimeError("count_token received Bad value")
    return cnt
