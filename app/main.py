# app/main.py
import io
import base64
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from face_utils import read_imagefile_bytes, get_face_embedding, is_face_live_from_frames, verify_embeddings
from storage import save_voter, get_voter, list_voters
from config import FACE_THRESHOLD, EMBED_DIM
from cryptography.fernet import Fernet
import os
import json

# ---- Encryption key (for demo only) ----
# In production: use secure key management (Vault/KMS) and never hardcode keys.
KEY_FILE = "data/secret.key"
if not os.path.exists(KEY_FILE):
    # create and store key (demo)
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as kf:
        kf.write(key)
else:
    with open(KEY_FILE, "rb") as kf:
        key = kf.read()
fernet = Fernet(key)


app = FastAPI(title="TRUVOX - AI/ML Biometric Module (Dummy DB)")


class VoterIn(BaseModel):
    name: str
    father_name: Optional[str]
    dob: Optional[str]
    gender: Optional[str]
    address: Optional[str]
    epic: str  # EPIC number
    # photo is uploaded as file in endpoint


@app.post("/enroll")
async def enroll(
    name: str = Form(...),
    father_name: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    epic: str = Form(...),
    photo: UploadFile = File(...)
):
    """
    Enrollment endpoint.
    - Accepts voter details and photo.
    - Extracts embedding, encrypts and stores in dummy DB.
    - Prevents duplicate EPIC or duplicate face.
    """

    # 1. ---- Check if EPIC already exists ----
    existing_voter = get_voter(epic)
    if existing_voter is not None:
        return {"status": "error", "message": f"Voter with EPIC {epic} already exists."}

    # 2. ---- Process image ----
    b = await photo.read()
    img = read_imagefile_bytes(b)
    emb, meta = get_face_embedding(img)
    if emb is None:
        return {"status": "error", "message": "No face detected in enrollment photo."}

    # 3. ---- Check for duplicate face across ALL voters ----
    voters = list_voters()
    for vid, vdata in voters.items():
        emb_enc_b64 = vdata["biometrics"]["embedding_enc"]
        emb_enc = base64.b64decode(emb_enc_b64)
        emb_bytes = fernet.decrypt(emb_enc)
        emb_stored = np.frombuffer(emb_bytes, dtype=np.float32)

        match, score = verify_embeddings(emb, emb_stored, threshold=FACE_THRESHOLD)
        if match:
            return {
                "status": "error",
                "message": f"Face already exists in system (similar to EPIC {vid}). Duplicate enrollment blocked."
            }

    # 4. ---- Encrypt and save embedding ----
    emb_bytes = emb.tobytes()
    emb_enc = fernet.encrypt(emb_bytes)  # bytes

    voter_id = epic
    voter_record = {
        "name": name,
        "father_name": father_name,
        "dob": dob,
        "gender": gender,
        "address": address,
        "epic": epic,
        "biometrics": {
            "embedding_enc": base64.b64encode(emb_enc).decode("utf-8"),
            "model": "insightface_arcface_r50",
            "meta": meta
        }
    }

    save_voter(voter_id, voter_record)

    return {"status": "ok", "voter_id": voter_id, "message": "Enrolled successfully (dummy DB)."}


@app.post("/verify")
async def verify(
    epic: str = Form(...),
    # Provide a single image frame via 'photo' OR multiple frames via 'frame1','frame2',...
    photo: Optional[UploadFile] = File(None),
    frames: Optional[List[UploadFile]] = File(None)
):
    """
    Verification endpoint.
    Accepts EPIC (voter id) and either:
      - photo: one image (single frame) or
      - frames: list of image files (for active-liveness)
    Returns similarity score, liveness result and verified boolean.
    """
    voter = get_voter(epic)
    if voter is None:
        return {"status": "error", "message": "Voter not found."}

    # decrypt stored embedding
    emb_enc_b64 = voter["biometrics"]["embedding_enc"]
    emb_enc = base64.b64decode(emb_enc_b64)
    emb_bytes = fernet.decrypt(emb_enc)
    emb_stored = np.frombuffer(emb_bytes, dtype=np.float32)

    # prepare frames
    frame_imgs = []
    if frames:
        for f in frames:
            b = await f.read()
            frame_imgs.append(read_imagefile_bytes(b))
    elif photo:
        b = await photo.read()
        frame_imgs.append(read_imagefile_bytes(b))
    else:
        return {"status": "error", "message": "No image(s) provided."}

    # take first frame to compute embedding for quick compare
    emb_live, meta_live = get_face_embedding(frame_imgs[0])
    if emb_live is None:
        return {"status": "error", "message": "No face detected in provided image."}

    # compare embeddings
    match, score = verify_embeddings(emb_live, emb_stored, threshold=FACE_THRESHOLD)

    # liveness check (only meaningful if multiple frames provided)
    liveness_ok = False
    if len(frame_imgs) >= 2:
        liveness_ok = is_face_live_from_frames(frame_imgs)
    else:
        # fallback: if only one frame, we can still flag liveness as unknown / require manual
        liveness_ok = False

    # decision policy: require both match and liveness
    verified = match and liveness_ok

    # For demonstration, also support fallback: if match strong and liveness unknown, we may allow OTP fallback
    # You can replace this logic with any policy (admin override, OTP, fingerprint, etc).
    fallback_used = False
    if match and not liveness_ok:
        # Example fallback policy (NOT secure without OTP): here we just mark as pending for manual review
        # Replace with OTP flow if you'd like automatic fallback:
        verified = False
        fallback_used = True

    # Optional: update stored embedding if verification successful (to mitigate aging)
    # If you want to update stored embedding automatically, do it here (with consent/log).
    # Example (commented out):
    # if verified:
    #     # update embedding to latest embedding (re-enroll)
    #     new_emb_bytes = emb_live.tobytes()
    #     new_enc = fernet.encrypt(new_emb_bytes)
    #     voter["biometrics"]["embedding_enc"] = base64.b64encode(new_enc).decode("utf-8")
    #     save_voter(epic, voter)

    # Build response
    resp = {
        "status": "ok",
        "epic": epic,
        "match_score": score,
        "match": match,
        "liveness": liveness_ok,
        "verified": verified,
        "fallback_used_or_pending": fallback_used,
        "note": "liveness requires multiple frames; send multiple frames for robust check."
    }

    # Log verification attempt: in production write to audit logs + blockchain for non-repudiation
    return resp


@app.get("/voters")
async def get_all_voters():
    """
    Returns list of voter IDs and basic attributes - debug endpoint.
    Remove or secure this in production.
    """
    return list_voters()
