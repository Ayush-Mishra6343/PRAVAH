import uvicorn
import webbrowser
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting PRAVAHA Crisis Intelligence System on http://127.0.0.1:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
