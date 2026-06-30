import sys
import os
import argparse

# Ensure the app module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.adapters.hf_cloud import HuggingFaceEmbedding

def run_real_test(api_key: str):
    print("Running REAL network test against Hugging Face Inference API...\n")
    print("This will send real data to Hugging Face and consume a tiny bit of your rate limit.\n")

    adapter = HuggingFaceEmbedding(
        base_url="https://api-inference.huggingface.co",
        api_key=api_key,
        model="BAAI/bge-small-en-v1.5",
        timeout=10,
        retries=3
    )

    # Test 1: Single Document Embedding
    doc = "BrokerAssist is an AI assistant for the Indian stock market."
    print(f"1. Embedding document chunk:\n   '{doc}'")
    try:
        res = adapter.embed(doc, is_query=False)
        print(f"   ✅ Success! Returned {len(res)} dimensional vector. First 3 values: {res[:3]}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 2: Single Query Embedding
    query = "What is the NALCO dividend?"
    print(f"\n2. Embedding search query:\n   '{query}'")
    try:
        res_query = adapter.embed(query, is_query=True)
        print(f"   ✅ Success! Returned {len(res_query)} dimensional vector. First 3 values: {res_query[:3]}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 3: Batch Embedding
    batch = [
        "First test document about TCS.",
        "Second test document about Infosys."
    ]
    print(f"\n3. Batch embedding {len(batch)} documents...")
    try:
        res_batch = adapter.embed_batch(batch, is_query=False)
        print(f"   ✅ Success! Returned {len(res_batch)} vectors of size {len(res_batch[0])}.")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    key = os.environ.get("BA_HF_API_KEY")
    if not key:
        print("❌ Error: BA_HF_API_KEY environment variable is not set.")
        print("Usage:")
        print("  export BA_HF_API_KEY=\"your_hf_token\"")
        print("  python apps/backend/app/tests/run_real_hf_test.py")
        sys.exit(1)
        
    run_real_test(key)
