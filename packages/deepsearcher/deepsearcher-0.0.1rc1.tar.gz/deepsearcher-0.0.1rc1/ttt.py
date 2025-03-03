from deepsearcher.configuration import Configuration, init_config
from deepsearcher.online_query import query

config = Configuration()

# config.set_provider_config("web_crawler", "Crawl4AICrawler", {})#TODO

# Customize your config here,
# more configuration see the Configuration Details section below.
# config.set_provider_config("llm", "OpenAI", {"model": "gpt-4o-mini"})
config.set_provider_config("llm", "OpenAI", {"model": "o1-mini"})
# config.set_provider_config("llm", "OpenAI", {"model": "o1"})
# config.set_provider_config("llm", "OpenAI", {"model": "xdeepseekr1", "api_key": "sk-Lu1O8IvaPbbouvfk729dAb48B9644306Ab267714B21b070b", "base_url": "https://maas-api.cn-huabei-1.xf-yun.com/v1" })
# config.set_provider_config("llm", "OpenAI", {"model": "xdeepseekv3", "api_key": "sk-Lu1O8IvaPbbouvfk729dAb48B9644306Ab267714B21b070b", "base_url": "https://maas-api.cn-huabei-1.xf-yun.com/v1" })
# config.set_provider_config("llm", "OpenAI", {"model": "deepseek/deepseek-r1-distill-llama-70b:free", "api_key": "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", "base_url": "https://openrouter.ai/api/v1" })
# config.set_provider_config("llm", "SiliconFlow", {"model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"})
# config.set_provider_config("llm", "AzureOpenAI", {
#     "model": "zilliz-gpt-4o-mini",
#     "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT_BAK"),
#     "api_key": os.getenv("AZURE_OPENAI_API_KEY_BAK"),
#     "api_version": "2023-05-15"
# })
# config.set_provider_config("llm", "AzureOpenAI", {
#     # "model": "zilliz-gpt-4o-mini",
#     "model": "zilliz-gpt-35-turbo",
#     "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
#     "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
#     "api_version": "2023-05-15"
# })

config.set_provider_config("embedding", "OpenAIEmbedding", {"model_name": "text-embedding-ada-002"})
config.set_provider_config(
    "vector_db", "Milvus", {"uri": "http://10.100.30.11:19530", "db": "ds_test"}
)
init_config(config=config)

# Load your local data
# load_from_local_files(paths_or_directory='./examples/data/deepseek-r1.pdf', force_new_collection=True)
# load_from_local_files(paths_or_directory='./examples/data/deepseek-v3.pdf')
# load_from_website(urls="https://docs.crawl4ai.com/core/installation/")
# load_from_website(urls="https://sebastianraschka.com/blog/2025/understanding-reasoning-llms.html", force_new_collection=True)

# Query
# question = """Write a report about DeepSeek-R1"""
# question = "Which film has the director who is older, God'S Gift To Women or Aldri annet enn bråk."
# question = "Who was born first out of Aivar Kuusmaa and Andy Summers?"
question = "Where was the composer of film Billy Elliot born?"
result, retrieved_res, token_num = query(question)
# naive_result, _ = naive_rag_query(question)
# print(naive_result)
print(token_num)
