from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
import torch
import logging
from ..utils.config import Settings

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        self.settings = Settings()
        self.model = None
        self.tokenizer = None
        self._is_ready = False
        
        # Common model initialization parameters
        self._model_kwargs = {
            "revision": self.settings.model.revision,
            "trust_remote_code": True,
            "token": self.settings.auth.huggingface_token
        }
        
        # Default generation parameters
        self._default_generation_config = {
            "max_length": self.settings.params.max_sequence_length,
            "temperature": self.settings.params.default_temperature,
            "do_sample": True,
            "top_p": 0.9,
        }

    async def initialize(self):
        """Initialize the model and tokenizer"""
        logger.info(f"Loading model {self.settings.model.name}")
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.settings.model.name,
                **self._model_kwargs
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.settings.model.name,
                **self._model_kwargs,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            self._is_ready = True
            logger.info(f"Model loaded successfully on {device}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self._is_ready = False
            raise

    def is_ready(self) -> bool:
        """Check if the model is ready for inference"""
        return self._is_ready

    def _format_prompt(self, prompt: str) -> str:
        """Format the prompt with consistent instructions"""
        return f"""
You are a helpful AI assistant. Answer the following question accurately and concisely.

Question: {prompt}

Answer:"""

    def _extract_response(self, full_response: str, prompt: str) -> str:
        """Extract the actual response from the model output"""
        if "Answer:" in full_response:
            return full_response.split("Answer:")[1].strip()
        return full_response.replace(prompt, "").strip()

    def _get_generation_config(self, **kwargs) -> dict:
        """Get generation config with overrides from kwargs"""
        config = self._default_generation_config.copy()
        config.update({k: v for k, v in kwargs.items() if k in config})
        return config

    async def generate(self, prompt: str, **kwargs):
        """Generate text based on the prompt"""
        if not self.is_ready():
            logger.error("Model not initialized!")
            raise RuntimeError("Model not initialized")

        try:
            formatted_prompt = self._format_prompt(prompt)
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)
            
            generation_config = self._get_generation_config(**kwargs)
            outputs = self.model.generate(**inputs, **generation_config)
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return self._extract_response(full_response, formatted_prompt)
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise 