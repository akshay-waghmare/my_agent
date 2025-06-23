"""
Unified LLM Client Wrapper

This module provides a unified interface for different LLM providers,
allowing easy switching between OpenAI, Groq, and other providers
through configuration.
"""

import os
from typing import Dict, Any, Optional
from openai import OpenAI


class LLMClient:
    """
    Unified LLM client that abstracts different providers
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM client based on configuration
        
        Args:
            config: Configuration dictionary containing LLM settings
        """
        self.config = config
        self.llm_config = config.get("llm", {})
        self.provider = self.llm_config.get("provider", "openai").lower()
          # Initialize the appropriate client
        self.client = self._initialize_client()
        
    def _initialize_client(self) -> OpenAI:
        """
        Initialize the appropriate LLM client based on provider
        
        Returns:
            Initialized client instance
        """
        if self.provider == "openai":
            return self._initialize_openai_client()
        elif self.provider == "groq":
            return self._initialize_groq_client()
        elif self.provider == "lmstudio":
            return self._initialize_lmstudio_client()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _initialize_openai_client(self) -> OpenAI:
        """Initialize OpenAI client"""
        openai_config = self.llm_config.get("openai", {})
        api_key_env = openai_config.get("api_key_env", "OPENAI_API_KEY")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(f"API key not found in environment variable: {api_key_env}")
        
        return OpenAI(api_key=api_key)
    
    def _initialize_groq_client(self) -> OpenAI:
        """Initialize Groq client (uses OpenAI-compatible interface)"""
        groq_config = self.llm_config.get("groq", {})
        api_key_env = groq_config.get("api_key_env", "GROQ_API_KEY")
        api_key = os.getenv(api_key_env)
        api_base = groq_config.get("api_base", "https://api.groq.com/openai/v1")
        
        if not api_key:
            raise ValueError(f"API key not found in environment variable: {api_key_env}")
        
        return OpenAI(
            api_key=api_key,
            base_url=api_base
        )
    
    def _initialize_lmstudio_client(self) -> OpenAI:
        """Initialize LM Studio client (uses OpenAI-compatible interface)"""
        lmstudio_config = self.llm_config.get("lmstudio", {})
        api_base = lmstudio_config.get("api_base", "http://localhost:1234/v1")
        
        # LM Studio doesn't actually need an API key, but we'll use a dummy one for consistency
        api_key = "lm-studio-dummy-key"
        api_key_env = lmstudio_config.get("api_key_env", "LMSTUDIO_API_KEY")
        if os.getenv(api_key_env):
            api_key = os.getenv(api_key_env)
        
        return OpenAI(
            api_key=api_key,
            base_url=api_base
        )
    def get_model_name(self) -> str:
        """
        Get the model name for the current provider
        
        Returns:
            Model name string
        """
        if self.provider == "openai":
            return self.llm_config.get("openai", {}).get("model", "gpt-4")
        elif self.provider == "groq":
            return self.llm_config.get("groq", {}).get("model", "llama-3.1-70b-versatile")
        elif self.provider == "lmstudio":
            return self.llm_config.get("lmstudio", {}).get("model", "default")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def get_autogen_config(self) -> Dict[str, Any]:
        """
        Get configuration dict for AutoGen agents
        
        Returns:
            Configuration dictionary compatible with AutoGen
        """
        base_config = {
            "model": self.get_model_name(),
            "temperature": self.llm_config.get("temperature", 0.2),
            "max_tokens": self.llm_config.get("max_tokens", 2000),
        }
          # Add provider-specific configuration
        if self.provider == "openai":
            openai_config = self.llm_config.get("openai", {})
            api_key_env = openai_config.get("api_key_env", "OPENAI_API_KEY")
            base_config["api_key"] = os.getenv(api_key_env)
            
        elif self.provider == "groq":
            groq_config = self.llm_config.get("groq", {})
            api_key_env = groq_config.get("api_key_env", "GROQ_API_KEY")
            api_base = groq_config.get("api_base", "https://api.groq.com/openai/v1")
            
            base_config["api_key"] = os.getenv(api_key_env)
            base_config["base_url"] = api_base
            
        elif self.provider == "lmstudio":
            lmstudio_config = self.llm_config.get("lmstudio", {})
            api_base = lmstudio_config.get("api_base", "http://localhost:1234/v1")
            
            # LM Studio doesn't need an API key, but we'll use a dummy one
            base_config["api_key"] = "lm-studio-dummy-key"
            base_config["base_url"] = api_base
        
        return base_config
    def create_chat_completion(self, messages: list, **kwargs) -> Any:
        """
        Create a chat completion using the configured provider
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters for the completion.
                     For function calling, pass 'functions' and optionally 'function_call'
            
        Returns:
            Chat completion response
        """
        # Merge default parameters with provided kwargs
        params = {
            "model": self.get_model_name(),
            "temperature": self.llm_config.get("temperature", 0.2),
            "max_tokens": self.llm_config.get("max_tokens", 2000),
        }
          # Handle function calling parameters
        if "functions" in kwargs:
            params["tools"] = [{"type": "function", "function": f} for f in kwargs["functions"]]
            if "function_call" in kwargs:
                # Handle string parameter (auto/none)
                if isinstance(kwargs["function_call"], str):
                    params["tool_choice"] = kwargs["function_call"]
                # Handle object parameter ({name: "function_name"})
                elif isinstance(kwargs["function_call"], dict) and "name" in kwargs["function_call"]:
                    params["tool_choice"] = {
                        "type": "function",
                        "function": {"name": kwargs["function_call"]["name"]}
                    }
            # Remove original function calling params to avoid conflicts
            kwargs.pop("functions", None)
            kwargs.pop("function_call", None)
            
        # Add remaining kwargs
        params.update(kwargs)
        
        # Make the API call
        response = self.client.chat.completions.create(
            messages=messages,
            **params
        )
          # Add compatibility layer for function/tool calls
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            # Create custom function_call attribute with proper access methods
            class FunctionCall:
                def __init__(self, tool_call):
                    self.tool_call = tool_call
                    
                @property
                def name(self):
                    return self.tool_call.function.name
                    
                @property
                def arguments(self):
                    return self.tool_call.function.arguments
                    
            # Set function_call property on the message object
            response.choices[0].message.function_call = FunctionCall(response.choices[0].message.tool_calls[0])
        
        return response
    
    def get_provider_info(self) -> Dict[str, str]:
        """
        Get information about the current provider and model
        
        Returns:
            Dictionary with provider information
        """
        return {
            "provider": self.provider,
            "model": self.get_model_name(),
            "api_base": self.client.base_url if hasattr(self.client, 'base_url') else "default"
        }


def create_llm_client(config: Dict[str, Any]) -> LLMClient:
    """
    Factory function to create an LLM client
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized LLMClient instance
    """
    return LLMClient(config)
