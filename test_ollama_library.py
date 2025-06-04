#!/usr/bin/env python3
"""
Professional Ollama client for tool use and JSON parsing.
"""

import json
import logging
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import ollama
from ollama import ResponseError


# Configure logging - suppress verbose logs for cleaner output
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Suppress httpx and ollama library logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("ollama").setLevel(logging.WARNING)


@dataclass
class OllamaConfig:
    """Configuration for Ollama client."""
    model: str
    temperature: float = 0.1  # Low for tool use
    top_p: float = 0.95
    timeout: int = 10
    max_retries: int = 2


class OllamaClient:
    """Professional Ollama client with error handling and retry logic."""
    
    def __init__(self, config: OllamaConfig):
        self.config = config
        self._validate_model()
    
    def _validate_model(self) -> None:
        """Verify model exists before using it."""
        try:
            models = ollama.list()
            # Debug: Print the actual structure
            logger.debug(f"Ollama models response: {models}")
            
            # Handle different response formats
            if 'models' in models:
                available = [m.get('name', m.get('model', str(m))) for m in models['models']]
            else:
                available = [str(m) for m in models]
            
            logger.info(f"Available models: {available}")
            
            if self.config.model not in available:
                raise ValueError(f"Model '{self.config.model}' not found. Available: {available}")
            
            logger.info(f"✅ Model '{self.config.model}' validated successfully")
                
        except Exception as e:
            logger.warning(f"Could not validate model: {e}")
            logger.info("Proceeding without validation - model may still work")
    
    def generate(
        self, 
        prompt: str, 
        format_type: Optional[str] = None,
        stream: bool = False
    ) -> str: # type: ignore
        """
        Generate response with retry logic and proper error handling.
        
        Args:
            prompt: Input prompt
            format_type: 'json' for structured output
            stream: Whether to stream response
            
        Returns:
            Generated text response
            
        Raises:
            OllamaError: When generation fails after retries
        """
        options = {
            "temperature": self.config.temperature,
            "top_p": self.config.top_p
        }
        
        for attempt in range(self.config.max_retries):
            try:
                if stream:
                    return self._generate_stream(prompt, format_type, options)
                else:
                    return self._generate_blocking(prompt, format_type, options)
                    
            except ResponseError as e:
                logger.error(f"Ollama error (attempt {attempt + 1}): {e}")
                if attempt == self.config.max_retries - 1:
                    raise OllamaError(f"Failed after {self.config.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                # Don't log here, let the evaluator handle it
                raise OllamaError(f"Unexpected error: {e}")
    
    def _generate_blocking(
        self, 
        prompt: str, 
        format_type: Optional[str], 
        options: Dict[str, Any]
    ) -> str:
        """Generate non-streaming response with proper timeout."""
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": options
        }
        
        if format_type:
            payload["format"] = format_type
        
        logger.info(f"Sending request to model {self.config.model} (timeout: {self.config.timeout}s)...")
        start_time = time.time()
        
        # Use threading to implement timeout
        result: List[Optional[str]] = [None]
        exception: List[Optional[Exception]] = [None]
        
        def target():
            try:
                response = ollama.generate(**payload)
                result[0] = response['response']
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.config.timeout)
        
        elapsed = time.time() - start_time
        
        if thread.is_alive():
            # Timeout occurred - don't log here, let the evaluator handle it
            raise OllamaError(f"Request timed out after {self.config.timeout} seconds")
        
        if exception[0]:
            raise exception[0]
        
        if result[0] is None:
            logger.error(f"❌ Request failed after {elapsed:.2f}s: No response received")
            raise OllamaError("No response received")
        
        logger.info(f"✅ Response received in {elapsed:.2f}s")
        return result[0]
    
    def _generate_stream(
        self, 
        prompt: str, 
        format_type: Optional[str], 
        options: Dict[str, Any]
    ) -> str:
        """Generate streaming response."""
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": True,
            "options": options
        }
        
        if format_type:
            payload["format"] = format_type
        
        stream = ollama.generate(**payload)
        full_response = ""
        
        for chunk in stream:
            if 'response' in chunk:
                full_response += chunk['response']
        
        return full_response
    
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Generate JSON response with validation.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            JSONParseError: When response isn't valid JSON
        """
        # Ensure prompt requests JSON
        if "json" not in prompt.lower():
            prompt += "\n\nRespond in valid JSON format only."
        
        response = self.generate(prompt, format_type="json")
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {response[:200]}...")
            raise JSONParseError(f"Failed to parse JSON: {e}")


class OllamaError(Exception):
    """Base exception for Ollama client errors."""
    pass


class JSONParseError(OllamaError):
    """Exception for JSON parsing failures."""
    pass


def create_client(model: str, **kwargs) -> OllamaClient:
    """Factory function to create configured client."""
    config = OllamaConfig(model=model, **kwargs)
    return OllamaClient(config)


# Example usage and testing
def test_client():
    """Test the professional client."""
    # Use the EXACT model name from ollama list (including ":latest")
    stream=False
    prompt = "Say ONLY the word 'Hello', no other words"
    model_name = "gemma3:1b"
        
    try:
        client = create_client(
            model=model_name,
            temperature=0.1,
            top_p=0.95,
            timeout=60  # Shorter timeout for testing
        )
        
        # Test with simpler prompt first
        logger.info("Testing simple generation...")
        response = client.generate(prompt, stream=stream)
        logger.info(f"Response: {response}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")


if __name__ == "__main__":
    test_client()
