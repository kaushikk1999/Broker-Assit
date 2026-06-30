import sys
import os
import json
from unittest.mock import patch, MagicMock

# Ensure the app module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.adapters.hf_cloud import HuggingFaceEmbedding

def test_hugging_face_adapter():
    print("Starting in-depth test of HuggingFaceEmbedding...\n")
    
    # Initialize the adapter with a dummy key and model
    adapter = HuggingFaceEmbedding(
        base_url="https://api-inference.huggingface.co",
        api_key="hf_dummy_key",
        model="BAAI/bge-small-en-v1.5",
        timeout=5,
        retries=2
    )
    
    print(f"✅ Adapter initialized with model: {adapter.model}")

    # Mock httpx.post
    with patch("httpx.post") as mock_post:
        # 1. Test standard document embedding (single string)
        # BGE-small should output 384 dimensions. We'll simulate a small response.
        mock_response_doc = MagicMock()
        mock_response_doc.status_code = 200
        mock_response_doc.json.return_value = [0.1] * 384  # simulate a list of floats
        mock_post.return_value = mock_response_doc
        
        doc_text = "This is a company financial document."
        res = adapter.embed(doc_text, is_query=False)
        
        # Verify the POST request
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["inputs"] == doc_text
        assert len(res) == 384
        print(f"✅ Document embedding test passed. (Output dimension: {len(res)})")
        
        # 2. Test query embedding (single string)
        # BGE models should get a prefix when is_query=True
        mock_response_query = MagicMock()
        mock_response_query.status_code = 200
        mock_response_query.json.return_value = [0.2] * 384
        mock_post.return_value = mock_response_query
        
        query_text = "What is the revenue for NALCO?"
        res_query = adapter.embed(query_text, is_query=True)
        
        # Verify the POST request has the prefix
        args, kwargs = mock_post.call_args
        expected_prefixed = "Represent this sentence for searching relevant passages: What is the revenue for NALCO?"
        assert kwargs["json"]["inputs"] == expected_prefixed
        assert len(res_query) == 384
        print(f"✅ Query embedding test passed. Prefix correctly added: '{kwargs['json']['inputs'][:50]}...'")

        # 3. Test batch document embedding
        mock_response_batch = MagicMock()
        mock_response_batch.status_code = 200
        mock_response_batch.json.return_value = [[0.1]*384, [0.15]*384]
        mock_post.return_value = mock_response_batch
        
        batch_docs = ["Document 1", "Document 2"]
        res_batch = adapter.embed_batch(batch_docs, is_query=False)
        
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["inputs"] == batch_docs
        assert len(res_batch) == 2
        assert len(res_batch[0]) == 384
        print(f"✅ Batch document embedding test passed. Processed {len(res_batch)} items.")

        # 4. Test 503 retry behavior (Model Loading)
        mock_503 = MagicMock()
        mock_503.status_code = 503
        mock_503.json.return_value = {"error": "Model is loading", "estimated_time": 0.1} # use a fast sleep
        
        mock_200 = MagicMock()
        mock_200.status_code = 200
        mock_200.json.return_value = [0.9] * 384
        
        # side_effect allows sequential responses: first 503, then 200 OK
        mock_post.side_effect = [mock_503, mock_200]
        
        # Patch time.sleep to not actually wait during our test, but verify it was called
        with patch("time.sleep") as mock_sleep:
            res_retry = adapter.embed("Wait for it...", is_query=False)
            assert len(res_retry) == 384
            mock_sleep.assert_called_once_with(0.1)
            print("✅ Retry behavior (503 Model Loading) test passed. Script successfully waited and retried.")

    print("\n🎉 All adapter logic tests passed successfully!")
    print("\nTo perform a REAL network test against Hugging Face, run:")
    print("  export BA_HF_API_KEY=\"your_key_here\"")
    print("  python apps/backend/app/tests/run_real_hf_test.py")

if __name__ == "__main__":
    test_hugging_face_adapter()
