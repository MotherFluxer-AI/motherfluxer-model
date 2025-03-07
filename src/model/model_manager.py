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
            
            # Format prompt with better instructions
            formatted_prompt = f"""
You are a helpful AI assistant. Answer the following question accurately and concisely.

Question: {prompt}

Answer:"""
            
            logger.info(f"Formatted prompt: {formatted_prompt}")
            
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)
            logger.info("Tokenization successful")
            
            # Set default parameters
            generation_config = {
                "max_length": kwargs.get("max_length", self.settings.max_sequence_length),
                "temperature": kwargs.get("temperature", self.settings.default_temperature),
                "do_sample": True,
                "top_p": kwargs.get("top_p", 0.9),
            }
            logger.info(f"Generation config: {generation_config}")
            
            outputs = self.model.generate(
                **inputs,
                **generation_config
            )
            logger.info("Generation successful")
            
            # Extract only the generated response, removing the prompt
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the answer part
            if "Answer:" in response:
                response = response.split("Answer:")[1].strip()
            else:
                # If the model didn't follow the format, try to extract anything after the prompt
                response = response.replace(formatted_prompt, "").strip()
            
            logger.info(f"Final response: {response}")
            
            return response
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise 