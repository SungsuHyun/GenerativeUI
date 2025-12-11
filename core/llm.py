import os
from openai import AsyncOpenAI
import google.generativeai as genai
import httpx
from typing import Optional, Literal
from loguru import logger

# Set API keys (get from environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def _get_provider(model_name: str) -> Literal["gemini", "gpt"]:
    """Parses the model name string to return either 'gemini' or 'gpt' provider."""
    model_name_lower = model_name.lower()
    if "gemini" in model_name_lower:
        return "gemini"
    elif "gpt" in model_name_lower or "o3" in model_name_lower or "o4" in model_name_lower:
        return "gpt"
    else:
        logger.error(f"Could not determine the provider from model name: {model_name}")
        raise ValueError(f"Could not determine the provider (gemini or gpt) from the model name '{model_name}'.")

def read_prompt(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

async def call_gemini(prompt: str, model_name: str):
    logger.info(f"Calling Gemini model: {model_name}")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name)
    
    generation_config = genai.types.GenerationConfig(
        temperature=0.1
    )
    
    response = await model.generate_content_async(
        prompt,
        generation_config=generation_config
    )
    logger.info("Gemini call successful.")
    return response.text

async def call_gpt(prompt: str, model_name: str):
    logger.info(f"Calling GPT model: {model_name}")
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    response = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ],
        # temperature=0.2
    )
    logger.info(f"GPT call successful. {response.choices[0].message.content}")
    return response.choices[0].message.content

async def call_llm(prompt: str, model_name: Optional[str] = None):
    """
    Calls the LLM with the specified prompt and model name.
    """
    if not model_name:
        logger.error("model_name argument not provided.")
        raise ValueError("The model_name argument must be provided.")

    logger.info(f"Determining provider for model: {model_name}")
    provider = _get_provider(model_name)
    logger.info(f"Provider determined: {provider}")

    if provider == "gemini":
        return await call_gemini(prompt, model_name)
    elif provider == "gpt":
        return await call_gpt(prompt, model_name) 