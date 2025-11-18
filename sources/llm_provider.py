import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from logger import Logger, pretty_print

class LLMProvider:
    def __init__(self, provider_name, model, server_ip, is_local):
        self.provider_name = provider_name
        self.model = model
        self.server_ip = server_ip
        self.is_local = is_local
        self.available_providers = {
            "ollama": self.ollama_fn,
            "lm-studio": self.lm_studio_fn,
            "openai": self.openai_fn,
            "deepseek": self.deepseek_fn,
            "together": self.together_fn,
            "google": self.google_fn,
            "huggingface": self.huggingface_fn,
            "dsk_deepseek": self.dsk_deepseek,
            "openrouter": self.openrouter_fn,
            "test": self.test_fn
        }
        self.logger = Logger("provider.log")
        self.api_key = None
        self.internal_url, self.in_docker = self.get_internal_url()
        self.unsafe_providers = ["openai", "deepseek", "dsk_deepseek", "together", "google", "openrouter"]
        if self.provider_name not in self.available_providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        if self.provider_name in self.unsafe_providers and self.is_local == False:
            pretty_print("Warning: you are using an API provider. You data will be sent to the cloud.", color="warning")
            self.api_key = self.get_api_key(self.provider_name)
        elif self.provider_name != "ollama":
            pretty_print(f"Provider: {provider_name} initialized at {self.server_ip}", color="success")

    def get_model_name(self) -> str:
        return self.model

    def get_api_key(self, provider):
        load_dotenv()
        api_key_var = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(api_key_var)
        if not api_key:
            pretty_print(f"API key {api_key_var} not found in .env file. Please add it", color="warning")
            exit(1)
        return api_key  # This was missing!

    def openrouter_fn(self, history, verbose=False):
        """
        Use OpenRouter API to generate text.
        """
        if self.api_key is None:
            raise Exception("API key not set for OpenRouter provider")
            
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        if self.is_local:
            # This case should ideally not be reached if unsafe_providers is set correctly
            # and is_local is False in config for openrouter
            raise Exception("OpenRouter is not available for local use. Change config.ini")
            
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=history,
            )
            if response is None:
                raise Exception("OpenRouter response is empty.")
                
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    # ... rest of the methods remain the same