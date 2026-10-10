from fastapi import FastAPI
from pydantic import BaseModel,Field
import pandas as pd
import joblib
from preprocessing import dropper,NumericalImputer,ordinalencoder,OHEEncoder

app = FastAPI(
    title="Airline passenger satisfaction prediction",
    description="API for predicting airline passenger satisfaction",
    version="1.0.0"
)

model=joblib.load("air_plane.pkl")

class PassengerInput(BaseModel):
    Age: int = Field(ge=0, le=120)
    Flight_Distance: int = Field(
        alias="Flight Distance", ge=0
    )
    Inflight_wifi_service: int = Field(
        alias="Inflight wifi service", ge=0, le=5
    )
    Departure_Arrival_time_convenient: int = Field(
        alias="Departure/Arrival time convenient", ge=0, le=5
    )
    Ease_of_Online_booking: int = Field(
        alias="Ease of Online booking", ge=0, le=5
    )
    Gate_location: int = Field(
        alias="Gate location", ge=0, le=5
    )
    Food_and_drink: int = Field(
        alias="Food and drink", ge=0, le=5
    )
    Online_boarding: int = Field(
        alias="Online boarding", ge=0, le=5
    )
    Seat_comfort: int = Field(
        alias="Seat comfort", ge=0, le=5
    )
    Inflight_entertainment: int = Field(
        alias="Inflight entertainment", ge=0, le=5
    )
    On_board_service: int = Field(
        alias="On-board service", ge=0, le=5
    )
    Leg_room_service: int = Field(
        alias="Leg room service", ge=0, le=5
    )
    Baggage_handling: int = Field(
        alias="Baggage handling", ge=0, le=5
    )
    Checkin_service: int = Field(
        alias="Checkin service", ge=0, le=5
    )
    Cleanliness: int = Field(
        alias="Cleanliness", ge=0, le=5
    )
    Departure_Delay: float = Field(
        alias="Departure Delay in Minutes", ge=0
    )
    Arrival_Delay: float = Field(
        alias="Arrival Delay in Minutes", ge=0
    )
    Gender: str
    Customer_Type: str = Field(
        alias="Customer Type"
    )
    Type_of_Travel: str = Field(
        alias="Type of Travel"
    )
    Class: str



@app.get("/")
def home():
    return{"message":"API is running"}

@app.post("/predict")
def predict(data: PassengerInput):
    input_dict = data.model_dump(by_alias=True)
    input_dict["id"] = 1
    input_data = pd.DataFrame([input_dict])
    prediction = int(model.predict(input_data)[0])
    probabilities = model.predict_proba(input_data)[0]
    classes = list(model.classes_)
    probability = probabilities[classes.index(1)]
    result = (
        "Satisfied"
        if prediction == 1
        else "Neutral or dissatisfied"
    )
    return {
        "prediction": result,
        "probability": round(float(probability), 4)
    }
