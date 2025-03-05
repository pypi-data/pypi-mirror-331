from transformers import AutoModelForCausalLM, AutoConfig
import torch
import numpy as np

class ModelLoader:
    def __init__(self, model_name):
        self.model_name = model_name
        self.config = AutoConfig.from_pretrained(model_name)
        self.model = None
        
    def load(self, device_map="auto", torch_dtype=torch.float16):
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map=device_map,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True
        )
        return self.model.eval()
    
    def get_layers(self):
        """Dynamically detect model architecture"""
        if "llama" in self.config.model_type:
            return self.model.model.layers
        elif "mistral" in self.config.model_type:
            return self.model.model.layers
        # Add other architectures here
        raise ValueError(f"Unsupported model type: {self.config.model_type}")