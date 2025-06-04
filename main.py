import uvicorn
from app import app 

if __name__ == "__main__":
    try:
        uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
