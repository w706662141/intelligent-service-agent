from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os

_model = None
_compress_model = None
_validator_model = None
_router_model = None
load_dotenv()


def get_model():
    global _model
    if _model is None:
        _model = ChatOpenAI(
            max_retries=3,  # ⭐ 重试
            # model="mistralai/mistral-7b-instruct",
            model="arcee-ai/trinity-large-preview:free",
            openai_api_key=os.getenv('OPENROUTER_API_KEY'),
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0,
        )

    return _model


def get_compress_model():
    global _compress_model
    if _compress_model is None:
        _compress_model = ChatOpenAI(
            max_retries=3,  # ⭐ 重试
            # model='qwen/qwen3-coder:free',
            model="arcee-ai/trinity-large-preview:free",
            # model="z-ai/glm-4.5-air:free",
            openai_api_key=os.getenv('OPENROUTER_API_KEY'),
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0,
        )
    return _compress_model


def get_router_model():
    global _router_model
    if _router_model is None:
        _router_model = ChatOpenAI(
            max_retries=3,  # ⭐ 重试
            model="arcee-ai/trinity-large-preview:free",
            openai_api_key=os.getenv('OPENROUTER_API_KEY'),
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0,
        )
    return _router_model

def get_validator_model():
    global _validator_model
    if not _validator_model:
        _validator_model = ChatGroq(
            api_key=os.getenv('GROQ_API_KEY'),
            model_name="llama-3.3-70b-versatile",
            temperature=0,
            max_retries=2,
        )

    return _validator_model
