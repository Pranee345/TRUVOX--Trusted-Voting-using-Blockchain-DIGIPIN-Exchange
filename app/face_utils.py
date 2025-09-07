# app/face_utils.py
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from typing import List, Tuple
from config import FACE_THRESHOLD, LIVENESS_NOSE_MOVE_PX, EMBED_DIM

# Initialize InsightFace app once (auto-downloads models on first run)
# providers: choose ['CUDAExecutionProvider'] if GPU + onnxruntime-gpu is installed
face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(640, 640))


def read_imagefile_bytes(file_bytes: bytes) -> np.ndarray:
    """
    Converts uploaded image bytes to an OpenCV BGR image
    """
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


def get_face_embedding(img: np.ndarray) -> Tuple[np.ndarray, dict]:
    """
    Detects first face in image, returns embedding (numpy array) and metadata dict.
    If no face detected, returns (None, None).
    """
    faces = face_app.get(img)
    if not faces or len(faces) == 0:
        return None, None

    # Use the first detected face
    face = faces[0]
    emb = face.embedding  # numpy array shape (512,)
    # get a small metadata snapshot
    meta = {
        "det_score": float(face.det_score),
        # if face.landmark exists it may include keypoints (x,y)
        "kps": face.kps.tolist() if hasattr(face, "kps") else None
    }
    return emb, meta


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two 1-D numpy arrays.
    """
    if a is None or b is None:
        return -1.0
    a = a.astype(np.float32)
    b = b.astype(np.float32)
    num = np.dot(a, b)
    den = np.linalg.norm(a) * np.linalg.norm(b)
    if den == 0:
        return -1.0
    return float(num / den)


def is_face_live_from_frames(frames: List[np.ndarray]) -> bool:
    """
    Simple active-liveness based on nose X movement across frames.
    Strategy:
        - For each frame, detect face and extract nose x from face.kps (InsightFace gives 5 keypoints: left eye, right eye, nose, left mouth, right mouth)
        - Compute the range (max_x - min_x). If > threshold we assume the user moved head (active), hence live.
    Notes:
        - This is a pragmatic and simple approach; it's not a full anti-spoof but works for a basic active-liveness check.
        - For production use, consider hardware-based liveness or trained anti-spoof models.
    """
    nose_x_positions = []
    for frame in frames:
        faces = face_app.get(frame)
        if not faces:
            continue
        f = faces[0]
        # Access keypoints: InsightFace returns 'kps' with shape (5,2) typically
        if hasattr(f, "kps") and f.kps is not None:
            try:
                # nose is typically index 2 in 5 keypoints: [left_eye, right_eye, nose, left_mouth, right_mouth]
                nose = f.kps[2]  # [x, y]
                nose_x_positions.append(float(nose[0]))
            except Exception:
                continue

    if not nose_x_positions:
        return False

    # calculate movement range
    move_range = max(nose_x_positions) - min(nose_x_positions)
    # print("Liveness nose move range:", move_range)
    return move_range >= LIVENESS_NOSE_MOVE_PX


def verify_embeddings(emb_live: np.ndarray, emb_stored: np.ndarray, threshold: float = FACE_THRESHOLD) -> Tuple[bool, float]:
    """
    Compare embeddings using cosine similarity and threshold.
    Returns (is_match, score)
    """
    score = cosine_similarity(emb_live, emb_stored)
    is_match = score >= threshold
    return is_match, score
