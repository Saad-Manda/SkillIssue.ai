from fastapi import HTTPException

def health_check(req, res):
    try:
        res.json({"message": "health check passed"}).status(200).end()
    except Exception as e:
        raise HTTPException(status_code = 500, detail = {"error": f"Server error {e}"})