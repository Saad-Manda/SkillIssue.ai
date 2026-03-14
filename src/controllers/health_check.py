from fastapi import HTTPException

def health_check():
    try:
        return {"message": "health check passed"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = {"error": f"Server error {e}"})