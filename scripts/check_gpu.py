"""Report CUDA availability and Ollama's loaded model placement."""
import os
import requests
try:
    import torch
    print({"cuda_available": torch.cuda.is_available(),
           "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
           "vram_total_gb": round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2) if torch.cuda.is_available() else None})
except Exception as exc:
    print({"torch_error": str(exc)})
host = os.getenv("OLLAMA_HOST", "http://ollama:11434").rstrip("/")
try:
    print("ollama_ps", requests.get(host + "/api/ps", timeout=10).json())
except Exception as exc:
    print({"ollama_error": str(exc)})
