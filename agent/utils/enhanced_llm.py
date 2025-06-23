"""
Enhanced LLM Client with support for multiple providers.

This module extends the base LLM client with support for
more providers including Anthropic, HuggingFace, and local models.
"""

import os
from typing import Dict, Any, Optional, List, Union
import json
import importlib
from .llm_client import LLMClient, create_llm_client

class EnhancedLLMClient(LLMClient):
    """
    Enhanced LLM client with support for multiple providers
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the enhanced LLM client
        
        Args:
            config: Configuration dictionary containing LLM settings
        """
        super().__init__(config)
        self.additional_providers = self._load_additional_providers()
    
    def _load_additional_providers(self) -> Dict[str, Any]:
        """
        Load additional provider modules if available
        
        Returns:
            Dict of provider modules
        """
        providers = {}
        
        # Try to import optional provider modules
        try:
            # Check for Anthropic
            try:
                import anthropic
                providers["anthropic"] = anthropic
                if self.config.get("agent", {}).get("verbose", True):
                    print("Anthropic provider module loaded")
            except ImportError:
                pass
                
            # Check for HuggingFace
            try:
                import huggingface_hub
                providers["huggingface"] = huggingface_hub
                if self.config.get("agent", {}).get("verbose", True):
                    print("HuggingFace provider module loaded")
            except ImportError:
                pass
                
            # Check for vLLM (local models)
            try:
                import vllm
                providers["vllm"] = vllm
                if self.config.get("agent", {}).get("verbose", True):
                    print("vLLM provider module loaded (local models)")
            except ImportError:
                pass
                
            # Check for Azure OpenAI
            try:
                # The OpenAI package also supports Azure via base_url
                providers["azure"] = "available"
                if self.config.get("agent", {}).get("verbose", True):
                    print("Azure OpenAI provider module loaded")
            except ImportError:
                pass
                
        except Exception as e:
            if self.config.get("agent", {}).get("verbose", True):
                print(f"Error loading additional providers: {e}")
        
        return providers
    
    def _initialize_client(self):
        """
        Initialize the appropriate LLM client based on provider
        
        Returns:
            Initialized client instance
        """
        if self.provider == "openai":
            return self._initialize_openai_client()
        elif self.provider == "groq":
            return self._initialize_groq_client()
        elif self.provider == "anthropic" and "anthropic" in self.additional_providers:
            return self._initialize_anthropic_client()
        elif self.provider == "azure":
            return self._initialize_azure_client()
        elif self.provider == "huggingface" and "huggingface" in self.additional_providers:
            return self._initialize_huggingface_client()
        elif self.provider == "vllm" and "vllm" in self.additional_providers:
            return self._initialize_vllm_client()
        else:
            # Fall back to the base client for unsupported providers
            return super()._initialize_client()
    
    def _initialize_anthropic_client(self):
        """Initialize Anthropic Claude client"""
        if "anthropic" not in self.additional_providers:
            raise ImportError("Anthropic module not installed. Please install it with 'pip install anthropic'")
        
        anthropic_config = self.llm_config.get("anthropic", {})
        api_key_env = anthropic_config.get("api_key_env", "ANTHROPIC_API_KEY")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(f"API key not found in environment variable: {api_key_env}")
        
        return self.additional_providers["anthropic"].Anthropic(api_key=api_key)
    
    def _initialize_azure_client(self):
        """Initialize Azure OpenAI client"""
        # Azure OpenAI uses the same client but with different configuration
        azure_config = self.llm_config.get("azure", {})
        api_key_env = azure_config.get("api_key_env", "AZURE_OPENAI_API_KEY")
        api_key = os.getenv(api_key_env)
        api_base = azure_config.get("api_base", None)
        api_version = azure_config.get("api_version", "2023-05-15")
        
        if not api_key:
            raise ValueError(f"API key not found in environment variable: {api_key_env}")
        
        if not api_base:
            raise ValueError("Azure OpenAI requires api_base to be set in config")
        
        # Use the OpenAI client with Azure configuration
        from openai import OpenAI
        return OpenAI(
            api_key=api_key,
            base_url=f"{api_base}/openai/deployments?api-version={api_version}"
        )
    
    def _initialize_huggingface_client(self):
        """Initialize HuggingFace client"""
        if "huggingface" not in self.additional_providers:
            raise ImportError("HuggingFace module not installed. Please install it with 'pip install huggingface_hub'")
        
        hf_config = self.llm_config.get("huggingface", {})
        api_key_env = hf_config.get("api_key_env", "HUGGINGFACE_API_TOKEN")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(f"API key not found in environment variable: {api_key_env}")
        
        return self.additional_providers["huggingface"].InferenceClient(token=api_key)
    
    def _initialize_vllm_client(self):
        """Initialize vLLM client for local models"""
        if "vllm" not in self.additional_providers:
            raise ImportError("vLLM module not installed. Please install it with 'pip install vllm'")
        
        vllm_config = self.llm_config.get("vllm", {})
        model_path = vllm_config.get("model_path", None)
        
        if not model_path:
            raise ValueError("vLLM requires model_path to be set in config")
        
        return self.additional_providers["vllm"].LLM(model=model_path)
    
    def get_model_name(self) -> str:
        """
        Get the model name for the current provider
        
        Returns:
            Model name string
        """
        provider_config = self.llm_config.get(self.provider, {})
        default_models = {
            "openai": "gpt-4",
            "groq": "llama-3.1-70b-versatile",
            "anthropic": "claude-3-sonnet-20240229",
            "azure": "gpt-4",
            "huggingface": "meta-llama/Llama-2-70b-chat-hf",
            "vllm": "local-model"
        }
        
        return provider_config.get("model", default_models.get(self.provider, "gpt-4"))

    def create_completion(self, messages, functions=None, function_call=None):
        """Create a chat completion with optional function calling."""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
            }
            
            if functions:
                kwargs["functions"] = functions
                if function_call:
                    kwargs["function_call"] = function_call

            response = self.client.chat.completions.create(**kwargs)
            return response
        
        except Exception as e:
            print(f"Error in create_completion: {str(e)}")
            raise

def create_enhanced_llm_client(config: Dict[str, Any]) -> Union[EnhancedLLMClient, LLMClient]:
    """
    Factory function to create an enhanced LLM client
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized LLMClient instance
    """
    try:
        return EnhancedLLMClient(config)
    except Exception as e:
        if config.get("agent", {}).get("verbose", True):
            print(f"Failed to create enhanced LLM client, falling back to base client: {e}")
        return create_llm_client(config)
