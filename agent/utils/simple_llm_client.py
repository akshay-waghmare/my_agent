"""
Simplified LLM Client with support for Groq function calling.

This module provides a client that supports both OpenAI and Groq providers,
with special handling for function calling formats.
"""

import os
from typing import Dict, Any, Optional, List, Union
import json
from openai import OpenAI

class SimpleLLMClient:
    """
    Simple LLM client that supports both OpenAI and Groq
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
    
    def get_model_name(self) -> str:
        """
        Get the model name for the current provider
        
        Returns:
            Model name string
        """
        if self.provider == "openai":
            return self.llm_config.get("openai", {}).get("model", "gpt-4")
        elif self.provider == "groq":
            return self.llm_config.get("groq", {}).get("model", "compound-beta")
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
            
            # Add special configuration for Groq function calling
            base_config["config_list"] = [
                {
                    "model": self.get_model_name(),
                    "api_key": os.getenv(api_key_env),
                    "base_url": api_base,
                    "temperature": self.llm_config.get("temperature", 0.2),
                    "max_tokens": self.llm_config.get("max_tokens", 2000),
                }
            ]
        
        return base_config
    
    def create_chat_completion(self, messages: list, functions=None, **kwargs) -> Any:
        """
        Create a chat completion using the configured provider
        
        Args:
            messages: List of message dictionaries
            functions: Optional list of function definitions
            **kwargs: Additional parameters for the completion
            
        Returns:
            Chat completion response
        """
        # Merge default parameters with provided kwargs
        params = {
            "model": self.get_model_name(),
            "temperature": self.llm_config.get("temperature", 0.2),
            "max_tokens": self.llm_config.get("max_tokens", 2000),
            **kwargs
        }
        
        # Handle functions differently based on provider
        if functions and self.provider == "groq":
            # Groq uses tools format for function calling
            tools = [
                {
                    "type": "function",
                    "function": func
                } for func in functions
            ]
            return self.client.chat.completions.create(
                messages=messages,
                tools=tools,
                **params
            )
        elif functions:
            # OpenAI format
            return self.client.chat.completions.create(
                messages=messages,
                functions=functions,
                **params
            )
        else:
            # No functions
            return self.client.chat.completions.create(
                messages=messages,
                **params
            )
    
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


def create_simple_llm_client(config: Dict[str, Any]) -> SimpleLLMClient:
    """
    Factory function to create an LLM client
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized SimpleLLMClient instance
    """
    return SimpleLLMClient(config)
