import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Install required libraries
# pip install transformers accelerate

def load_model(checkpoint="HuggingFaceTB/SmolLM2-135M", device="cuda"):
    """Loads the model and tokenizer on the specified device."""
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map="auto", torch_dtype=torch.bfloat16).to(device)
    return model, tokenizer

def generate_text(model, tokenizer, prompt, device="cuda"):
    """Generates text given a prompt."""
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
    outputs = model.generate(inputs)
    return tokenizer.decode(outputs[0])

if __name__ == "__main__":
    model, tokenizer = load_model()
    prompt = input("Enter your prompt: ").strip()
    response = generate_text(model, tokenizer, prompt)
    print("\nGenerated Text:\n", response)
    print(f"\nMemory footprint: {model.get_memory_footprint() / 1e6:.2f} MB")
