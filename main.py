import uvicorn
from app import app 

if __name__ == "__main__":
    try:
        # Start the FastAPI app using uvicorn
        uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
