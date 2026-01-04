import sys
import os

print("--- Verification Script ---")

# 1. Check imports
try:
    import ollama
    print("✓ ollama imported")
except ImportError:
    print("✗ ollama NOT imported")

try:
    from google.adk.agents import Agent
    print("✓ google-adk (Agent) imported")
except ImportError:
    print("✗ google-adk (Agent) NOT imported")
    # Let's check what's available in google-adk
    try:
        import google.adk
        print(f"  Note: google.adk available, but agents not found. Dir: {dir(google.adk)}")
    except ImportError:
        print("  Note: google.adk itself not found.")

# 2. Check environment variables
ollama_host = os.environ.get("OLLAMA_HOST", "Unknown")
print(f"OLLAMA_HOST: {ollama_host}")

# 3. Check Ollama connectivity
try:
    from ollama import Client
    client = Client(host=ollama_host)
    
    print("Testing text generation...")
    text_resp = client.generate(model="qwen3-vl:8b", prompt="say hello", stream=False)
    print(f"✓ Text generation response: {text_resp.get('response', '')}")

    models = client.list()
    print("✓ Successfully connected to Ollama")
    print(f"  Available models: {[m['name'] for m in models.get('models', [])]}")
    
    # Check if qwen3-vl:8b is present
    target_model = "qwen3-vl:8b"
    found = False
    for m in models.get('models', []):
        # Handle cases where m might be a string or a dict with different keys
        if isinstance(m, dict):
            name = m.get('name', m.get('model', ''))
            if name.startswith(target_model):
                found = True
                break
        elif isinstance(m, str) and m.startswith(target_model):
            found = True
            break
            
    if found:
        print(f"✓ Target model {target_model} found!")
    else:
        print(f"⚠️ Target model {target_model} NOT found in Ollama list.")
except Exception as e:
    print(f"✗ Failed to connect to Ollama or list models: {e}")

print("--- End of Verification ---")
