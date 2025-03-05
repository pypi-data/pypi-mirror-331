from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings

from shared_libraries.core.config import app_common_config

DEPLOYMENT_NAME_DIAL_GEMINI_PRO = "gemini-1.5-pro-preview-0409"
DEPLOYMENT_NAME_DIAL_GPT_4 = "gpt-4o-2024-11-20"
DEPLOYMENT_NAME_DIAL_LLAMA_3 = "llama-3-70b-instruct-awq"
DEPLOYMENT_NAME_DIAL_CLAUDE_V3_OPUS = "anthropic.claude-v3-opus"


# DEPLOYMENT_NAME_DIAL_CLAUDE_V3_SONNET = "anthropic.claude-v3-sonnet"
# DEPLOYMENT_NAME_DIAL_CLAUDE_V3_HAIKU = "anthropic.claude-v3-haiku"

# models/gemini-1.0-pro
# models/gemini-1.0-pro-001
# models/gemini-1.0-pro-latest
# models/gemini-1.0-pro-vision-latest
# models/gemini-1.5-pro-latest
# models/gemini-pro
# models/gemini-pro-vision


def get_llm_google(temperature: float = app_common_config.temperature_gemini_text,
                   # convert_system_message_to_human: bool = True,
                   deployment_name: str = app_common_config.deployment_name_gemini) -> ChatGoogleGenerativeAI:
    new_llm = ChatGoogleGenerativeAI(
        google_api_key=app_common_config.google_gemini_api_key,
        model=deployment_name,
        max_output_tokens=8192,
        temperature=temperature,
        # convert_system_message_to_human=convert_system_message_to_human
    )
    return new_llm


the_list_of_models_prefixes_whithout_temperature_support = [
    "o3-mini",
    "o1-mini"
]


def get_llm_dial(deployment_name: str = app_common_config.deployment_name_4o_mini,
                 temperature: float = None,
                 response_type: str = "text") -> AzureChatOpenAI:
    if deployment_name == app_common_config.deployment_name_128k:
        model_kwargs = {"response_format": {"type": response_type}}
    else:
        model_kwargs = {}

    if any(deployment_name.startswith(prefix) for prefix in the_list_of_models_prefixes_whithout_temperature_support):
        llm = AzureChatOpenAI(deployment_name=deployment_name,
                              model_name=deployment_name,
                              openai_api_version=app_common_config.openai_api_version,
                              openai_api_key=app_common_config.openai_api_key,
                              azure_endpoint=app_common_config.azure_endpoint,
                              model_kwargs=model_kwargs)
    else:
        temperature = temperature or app_common_config.temperature_open_ai_text
        llm = AzureChatOpenAI(deployment_name=deployment_name,
                              model_name=deployment_name,
                              openai_api_version=app_common_config.openai_api_version,
                              openai_api_key=app_common_config.openai_api_key,
                              azure_endpoint=app_common_config.azure_endpoint,
                              temperature=temperature,
                              model_kwargs=model_kwargs)
    return llm


# def get_llm_babylon(
#         deployment_name: str = app_common_config.deployment_name_128k,
#         temperature: float = app_common_config.temperature_open_ai_text,
# ) -> AzureChatOpenAI:
#     llm = AzureChatOpenAI(
#         deployment_name=deployment_name,
#         openai_api_version=app_common_config.openai_api_version,
#         openai_api_key=app_common_config.babylon_key,
#         azure_endpoint=app_common_config.babylon_gpt_endpoint,
#         temperature=temperature
#     )
#     return llm


def get_embeddings() -> OpenAIEmbeddings:
    embeddings = AzureOpenAIEmbeddings(deployment='text-embedding-ada-002',
                                       azure_endpoint=app_common_config.azure_endpoint,
                                       openai_api_key=app_common_config.openai_api_key)
    return embeddings


def get_embeddings_google() -> GoogleGenerativeAIEmbeddings:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=app_common_config.google_gemini_api_key
    )
    return embeddings
