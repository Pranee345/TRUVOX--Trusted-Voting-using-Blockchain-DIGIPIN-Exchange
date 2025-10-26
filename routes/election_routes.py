# routes/election_routes.py
from fastapi import APIRouter, HTTPException
from models.election_model import Election
from database.connection import election_collection
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
import datetime

router = APIRouter(prefix="/election", tags=["Election"])

@router.post("/create")
def create_election(election: Election):
    try:
        # Option 1 (preferred): convert election_date (datetime.date) -> datetime.datetime (UTC, start of day)
        # Pydantic gives election.election_date as a datetime.date object.
        data = jsonable_encoder(election)  # turns Pydantic model into JSON-safe dict (dates -> ISO strings)
        
        # But convert the ISO string or date field to a datetime.datetime for BSON
        # If jsonable_encoder converted date to string, parse it back; else handle date object
        ed = election.election_date
        if isinstance(ed, datetime.date) and not isinstance(ed, datetime.datetime):
            # combine to datetime at midnight (naive). If you want timezone-aware, adjust accordingly.
            data["election_date"] = datetime.datetime.combine(ed, datetime.time.min)
        else:
            # if jsonable_encoder returned a string (e.g., "2025-12-15"), convert to datetime
            try:
                if isinstance(data.get("election_date"), str):
                    data["election_date"] = datetime.datetime.fromisoformat(data["election_date"])
            except Exception:
                # fallback: leave as-is (string). But preferred to raise an error or handle formats you expect.
                pass

        result = election_collection.insert_one(data)
        return {"message": "Election created successfully!", "election_id": str(result.inserted_id)}
    except Exception as e:
        # log error server-side (print for now)
        print("Error creating election:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
