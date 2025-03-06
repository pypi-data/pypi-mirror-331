import joblib
import uvicorn
from fastapi import FastAPI
from typing import Dict, Any
import pandas as pd

def start_api():
    """Launch FastAPI for real-time predictions."""
    app = FastAPI()

    model = joblib.load("model.pkl")

    @app.get("/predict/")
    def predict(data: Dict[str, Any]):
        """Serve predictions via an API endpoint."""
        df = pd.DataFrame([data])
        prediction = model.predict(df)[0]
        return {"prediction": prediction}

    print("API running at: http://127.0.0.1:8000/predict?feature1=value1&feature2=value2")
    uvicorn.run(app, host="127.0.0.1", port=8000)
