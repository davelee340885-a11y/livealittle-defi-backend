import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from lal_api_server_deploy import app
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting server on port {port}...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
