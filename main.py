from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse
from bson.errors import InvalidId
from schemas import DistrictAdminCreate, DistrictAdminOut, StatusUpdateRequest
from crud import create_admin, get_pending_admins, update_admin_status, login_admin
from security import create_access_token

app = FastAPI(title="TRUVOX District Admin API")

# Create new admin
@app.post("/district-admin", response_model=DistrictAdminOut, tags=["DistrictAdmin"])
async def add_district_admin(admin: DistrictAdminCreate):
    created = await create_admin(admin)
    if not created:
        raise HTTPException(status_code=400, detail="Could not create user")
    return created

# List pending admins
@app.get("/district-admins/pending", response_model=list[DistrictAdminOut], tags=["DistrictAdmin"])
async def list_pending_admins():
    admins = await get_pending_admins()
    return admins

# Approve or reject pending admin
@app.patch("/district-admin/{admin_id}/status", tags=["DistrictAdmin"])
async def patch_status(
    admin_id: str = Path(..., description="District admin ID"),
    status_update: StatusUpdateRequest = None,
):
    try:
        updated_admin = await update_admin_status(admin_id, status_update.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid admin ID format")

    if not updated_admin:
        raise HTTPException(status_code=404, detail="District admin not found or not pending")

    return updated_admin

# Admin login
@app.get("/district-admin/login", tags=["DistrictAdmin"])
async def admin_login(email: str = Query(...), password: str = Query(...)):
    admin, error = await login_admin(email, password)
    if error:
        raise HTTPException(status_code=400, detail=error)

    token = create_access_token({"sub": str(admin["_id"]), "email": email})
    return {"access_token": token, "token_type": "bearer"}

# Root
@app.get("/", tags=["Root"])
def read_root():
    return {"Hello": "World"}

# Favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("path/to/favicon.ico")
