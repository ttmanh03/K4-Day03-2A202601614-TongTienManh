"""
Chạy FastAPI backend ở cổng 8001.

Cổng 8000 đã được `server.py` (bản web UI thuần Python của Role 1) dùng,
nên bản FastAPI + React này dùng 8001 để hai hệ thống chạy song song được.

    python backend/run.py
"""

import os
import sys

import uvicorn

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

PORT = 8001

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)
