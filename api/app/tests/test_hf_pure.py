import json
import urllib.request
import urllib.error
import time
import sys

import os

API_KEY = os.environ.get("BA_HF_API_KEY", "")
MODEL = "BAAI/bge-small-en-v1.5"
URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL}"

def query(payload):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(URL, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        return {"error": e.code, "message": error_msg}
    except Exception as e:
        return {"error": str(e)}

def run_test():
    print("==================================================")
    print(f"Testing Hugging Face Embeddings with model: {MODEL}")
    print("==================================================\n")

    # 1. Test Single Document (No prefix)
    print("1. Testing Single Document Embedding...")
    doc_payload = {"inputs": "This is a test document for the BrokerAssist application."}
    
    # We may need to retry once if the model is loading (503)
    res = query(doc_payload)
    if isinstance(res, dict) and res.get("error") == 503:
        msg = json.loads(res.get("message", "{}"))
        wait_time = msg.get("estimated_time", 5)
        print(f"   [!] Model is currently loading on HF servers. Waiting {wait_time:.1f} seconds...")
        time.sleep(wait_time)
        res = query(doc_payload)

    if isinstance(res, list):
        # res could be a list of floats, or a list of list of floats
        vector = res[0] if isinstance(res[0], list) else res
        print(f"   ✅ Success! Received {len(vector)}-dimensional vector.")
        print(f"   Sample values: {vector[:3]}")
    else:
        print(f"   ❌ Failed: {res}")
        sys.exit(1)
        
    print()

    # 2. Test Query (With BGE Prefix)
    print("2. Testing Search Query Embedding (with BGE Prefix)...")
    query_payload = {"inputs": "Represent this sentence for searching relevant passages: What is the NALCO dividend?"}
    res2 = query(query_payload)
    if isinstance(res2, list):
        vector2 = res2[0] if isinstance(res2[0], list) else res2
        print(f"   ✅ Success! Received {len(vector2)}-dimensional vector.")
        print(f"   Sample values: {vector2[:3]}")
    else:
        print(f"   ❌ Failed: {res2}")
        sys.exit(1)
        
    print()

    # 3. Test Batch Embedding
    print("3. Testing Batch Embedding (Multiple documents)...")
    batch_payload = {"inputs": ["First batch doc.", "Second batch doc."]}
    res3 = query(batch_payload)
    if isinstance(res3, list) and len(res3) > 0 and isinstance(res3[0], list):
        print(f"   ✅ Success! Received {len(res3)} vectors, each of {len(res3[0])} dimensions.")
    else:
        print(f"   ❌ Failed: {res3}")
        sys.exit(1)

    print("\n==================================================")
    print("🎉 ALL TESTS PASSED! Your Hugging Face API key is working perfectly.")
    print("==================================================")

if __name__ == "__main__":
    run_test()
