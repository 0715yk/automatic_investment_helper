from fastapi import FastAPI

app = FastAPI()

# Sample data for the API to return
data = {
    "message": "Hello, FastAPI!",
    "status": "success",
    "items": [
        {"id": 1, "name": "Item 1", "price": 100},
        {"id": 2, "name": "Item 2", "price": 150},
        {"id": 3, "name": "Item 3", "price": 200},
    ]
}

@app.get("/api/data", response_model=dict)
def get_data():
    """
    An endpoint to return sample JSON data.
    """
    return data
