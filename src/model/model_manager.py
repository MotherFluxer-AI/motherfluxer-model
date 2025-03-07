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

    async def initialize(self):
        """Initialize the model and tokenizer"""
        logger.info(f"Loading model {self.settings.model_name}")
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Initialize tokenizer with Phi-2 specific settings
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.settings.model_name,
                revision=self.settings.model_revision,
                trust_remote_code=True,
                token=self.settings.huggingface_token
            )
            
            # Load model with Phi-2 specific configuration
            self.model = AutoModelForCausalLM.from_pretrained(
                self.settings.model_name,
                revision=self.settings.model_revision,
                trust_remote_code=True,
                token=self.settings.huggingface_token,
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

    async def generate(self, prompt: str, **kwargs):
        """Generate text based on the prompt"""
        if not self.is_ready():
            logger.error("Model not initialized!")
            raise RuntimeError("Model not initialized")

        try:
            logger.info(f"Generating response for prompt: {prompt}")
            # Format prompt according to Phi-2's preferred format
            formatted_prompt = f"Instruct: {prompt}\nOutput:"
            logger.info(f"Formatted prompt: {formatted_prompt}")
            
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)
            logger.info("Tokenization successful")
            
            # Set default parameters based on Phi-2's capabilities
            generation_config = {
                "max_length": self.settings.max_sequence_length,
                "temperature": kwargs.get("temperature", self.settings.default_temperature),
                "do_sample": True,  # Enable sampling for more natural responses
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 50),
                "pad_token_id": self.tokenizer.eos_token_id
            }
            logger.info(f"Generation config: {generation_config}")
            
            # Update with any additional parameters
            generation_config.update(kwargs)
            
            outputs = self.model.generate(
                **inputs,
                **generation_config
            )
            logger.info("Generation successful")
            
            # Extract only the generated response, removing the prompt
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(formatted_prompt, "").strip()
            logger.info(f"Final response: {response}")
            
            return response
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise 