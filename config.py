#local_experiment
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb

#Vector DB와 관련된 설정
CATALOG_CHROMA_DATA_PATH = "vector_db"
CATALOG_CHROMA_HTTP_HOST = ""
CATALOG_CHROMA_HTTP_PORT = "8000"
CATALOG_CHROMA_HTTP_HEADERS = ""
CATALOG_CHROMA_HTTP_SSL = "false"
CATALOG_CHROMA_TENANT = chromadb.DEFAULT_TENANT
CATALOG_CHROMA_DATABASE = chromadb.DEFAULT_DATABASE

CATALOG_MILVUS_URL = "http://localhost:19530"

CATALOG_USE = True
CATALOG_DB_TYPE = "chroma" #milvus

#Object Storage와 관련된 설정
#MINIO_ENDPOINT = "minio:9000" #localhost:9000 => http://75.13.2.185:31008/browser/llm-model
MINIO_ENDPOINT = "75.13.2.185:30009"
MINIO_ACCESS = "minio"
MINIO_SECRET = "minio123"
BUCKET_NAME = "info-schema"

#임베딩 function
RAG_EMBEDDING_ENGINE = ""
RAG_EMBEDDING_MODEL = "model/multilingual-e5-large"
sentence_transformer_ef = "model/multilingual-e5-large"
# RAG_EMBEDDING_MODEL = "model/all-MiniLM-L6-v2"
# sentence_transformer_ef = "model/all-MiniLM-L6-v2"
OPENAI_API_KEY = ""
OPENAI_API_BASE_URL = ""
RAG_EMBEDDING_OPENAI_BATCH_SIZE = "1"
RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE = ""
RAG_EMBEDDING_MODEL_DIMENSION = 1024

#SQL만드는 LLM
SQL_LLM_URL = "http://75.13.2.186:11434/api/chat" #http://ollama:11434/api/chat
SQL_LLM_MODEL = "Qwen-2.5-32b:latest" 
# SQL_LLM_MODEL = "Gemma2-27b:latest" 
QUERY_DB_HOST = "75.13.2.185"
QUERY_DB_DBNAME = "cdc_pdsm"
QUERY_DB_USER = "postgres"
QUERY_DB_PASSWORD = "sdi-1974"
QUERY_DB_PORT = "30004"

#LLM
LLM_URL = "http://75.13.2.186:11434" #"http://ollama:11434/api/chat"
LLM_MODEL = "Gemma2-9b:latest"

import os
no_proxy ="localhost,127.0.0.1"
os.environ["NO_PROXY"] = no_proxy