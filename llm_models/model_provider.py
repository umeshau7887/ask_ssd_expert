from google.adk.models.lite_llm import LiteLlm

class ModelProvider:
    """A factory class to dynamically provision and configure LLM clients."""
    
    @staticmethod
    def get_model(model_name: str):
        """
        Takes a model identifier string and returns the fully initialised model client.
        
        Supported inputs:
        - 'gemma4': Returns an Ollama Gemma 4 client
        - 'gpt4o': Returns an OpenAI GPT-4o client
        - 'claude': Returns an Anthropic Claude 3.5 Sonnet client
        """
        # Normalise input to lowercase and remove spaces/hyphens
        sanitized_name = model_name.lower().replace("-", "").replace(" ", "")

        if sanitized_name in ["gemma4"]:
            model = LiteLlm(model="ollama_chat/gemma4:latest")
            return model

        else:
            supported = ["gemma4"]
            raise ValueError(f"Unsupported model: '{model_name}'. Choose from: {supported}")