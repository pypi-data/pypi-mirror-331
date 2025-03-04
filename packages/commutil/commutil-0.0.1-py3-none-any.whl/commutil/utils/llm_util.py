from typing import Dict, Optional, Union, Iterator, List, Any
import functools
from datetime import datetime
from .import_util import lazy_load



class OpenLLMChat:
    """A chat interface for large language models with optimized lazy loading."""

    def __init__(
            self,
            model_name: str,
            device: str = None,
            # Generation parameters
            temperature: float = 1.0,
            max_new_tokens: int = 50,
            top_p: float = 1.0,
            top_k: int = 50,
            num_beams: int = 1,
            num_return_sequences: int = 1,
            do_sample: bool = False,
            # Quantization and performance params
            quantization: Optional[str] = None,
            use_flash_attention: bool = False,
            # Other parameters
            system_prompt: str = None,
            trust_remote_code: bool = True,
            verbose: bool = True,
            **kwargs
    ):
        """Initialize OpenLLMChat with lazy-loaded components"""
        self.verbose = verbose
        self._log("Initializing model: %s", model_name)
        self.start_time = datetime.now()

        # Store initialization parameters
        self.model_name = model_name
        self.device = device
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.top_p = top_p
        self.top_k = top_k
        self.num_beams = num_beams
        self.num_return_sequences = num_return_sequences
        self.do_sample = do_sample
        self.quantization = quantization
        self.use_flash_attention = use_flash_attention
        self.system_prompt = system_prompt
        self.trust_remote_code = trust_remote_code
        self.extra_config = kwargs
        self.history = []

    def _log(self, message: str, *args) -> None:
        """Configurable logging function"""
        if not self.verbose:
            return

        try:
            from ..constants import YELLOW, RESET
            print(f"{YELLOW}[LLM] {message % args}{RESET}")
        except ImportError:
            print(f"[LLM] {message % args}")

    @lazy_load
    def torch(self):
        """Lazy load PyTorch"""
        try:
            import torch
            self._log("PyTorch loaded successfully")
            return torch
        except ImportError:
            raise ImportError("PyTorch is required but not installed")

    @lazy_load
    def tokenizer(self):
        """Lazy load tokenizer"""
        try:
            from transformers import AutoTokenizer
            self._log("Loading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=self.trust_remote_code,
                **self.extra_config.get("tokenizer_kwargs", {})
            )
            self._log("Tokenizer loaded successfully")
            return tokenizer
        except ImportError:
            raise ImportError("Transformers library is required")

    @lazy_load
    def model(self):
        """Lazy load model"""
        try:
            from transformers import (
                AutoModelForCausalLM,
                BitsAndBytesConfig,
                GPTQConfig
            )

            # Set device if not specified
            if self.device is None:
                self.device = self._get_default_device()

            self._log("Loading model: device=%s, quantization=%s", self.device, self.quantization)

            # Build kwargs
            kwargs = {
                "trust_remote_code": self.trust_remote_code,
                **(self.extra_config.get("model_kwargs", {}))
            }

            # Configure Flash Attention if requested
            if self.use_flash_attention:
                kwargs["use_flash_attention_2"] = True
                self._log("Enabled Flash Attention 2.0")

            # Apply quantization if specified
            if self.quantization:
                if self.quantization == "8bit":
                    kwargs["load_in_8bit"] = True
                    kwargs["device_map"] = "auto"
                    kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
                    self._log("Using 8-bit quantization")
                elif self.quantization == "4bit":
                    kwargs["load_in_4bit"] = True
                    kwargs["device_map"] = "auto"
                    kwargs["quantization_config"] = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=self.torch.float16,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True
                    )
                    self._log("Using 4-bit quantization")
                elif self.quantization == "gptq":
                    kwargs["device_map"] = "auto"
                    kwargs["quantization_config"] = GPTQConfig(bits=4)
                    self._log("Using GPTQ quantization")

            # Load the model
            model = AutoModelForCausalLM.from_pretrained(self.model_name, **kwargs)

            # Move to device if needed
            if not self.quantization and self.device != "auto":
                model = model.to(self.device)

            model.eval()
            self._log("Model loaded successfully, took: %.2f seconds",
                      (datetime.now() - self.start_time).total_seconds())

            return model

        except ImportError as e:
            raise ImportError(f"Required library not found: {str(e)}")
        except Exception as e:
            self._log("Error loading model: %s", str(e))
            raise

    def _get_default_device(self) -> str:
        """Determine the best available device"""
        if self.torch.cuda.is_available():
            return "cuda"
        elif hasattr(self.torch.backends, "mps") and self.torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def chat(
            self,
            prompt: str,
            system_prompt: str = None,
            stream: bool = False,
            **kwargs
    ) -> Union[str, Iterator[str]]:
        """Chat with the model using the transformers chat template"""
        # Prepare messages
        messages = []
        if system_prompt or self.system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt or self.system_prompt
            })
        messages.append({"role": "user", "content": prompt})

        try:
            # Use official chat template API
            chat_text = self.tokenizer.apply_chat_template(messages, tokenize=False)

            # Encode and move to device
            inputs = self.tokenizer(chat_text, return_tensors="pt")
            if self.device != "auto":
                # inputs = {k: v.to(self.device) for k, v in inputs.items()}
                inputs = inputs.to(self.device)

            # Set generation parameters
            gen_kwargs = {
                "temperature": self.temperature,
                "max_new_tokens": self.max_new_tokens,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "num_beams": self.num_beams,
                "num_return_sequences": self.num_return_sequences,
                "do_sample": self.do_sample,
                "pad_token_id": self.tokenizer.eos_token_id,
            }
            gen_kwargs.update(kwargs)

            # Generate response
            output = self.model.generate(**inputs, **gen_kwargs)

            # Extract generated part
            input_length = inputs.input_ids.shape[1]
            generated_output = output[0, input_length:]

            return self.tokenizer.decode(generated_output, skip_special_tokens=True)

        except Exception as e:
            self._log("Generation error: %s", str(e))
            return f"Error: {str(e)}"

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "quantization": self.quantization,
            "parameters": {
                "temperature": self.temperature,
                "max_new_tokens": self.max_new_tokens,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "num_beams": self.num_beams,
            },
            "history_length": len(self.history)
        }