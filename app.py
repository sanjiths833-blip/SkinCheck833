from flask import Flask, request, jsonify
from flask_cors import CORS

from datetime import datetime
from db import init_database, save_scan, get_history

from werkzeug.utils import secure_filename

from pathlib import Path
import uuid
import cv2
import numpy as np

from predictor import predict_skin_condition


# =====================================================
# FLASK APPLICATION
# =====================================================

app = Flask(__name__)

CORS(app)

init_database()


# =====================================================
# UPLOAD CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = str(
    UPLOAD_FOLDER
)

app.config["MAX_CONTENT_LENGTH"] = (
    8 * 1024 * 1024
)


ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


# =====================================================
# CHECK FILE
# =====================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =====================================================
# IMAGE QUALITY ANALYSIS
# =====================================================

def analyze_image_quality(image_path):

    image = cv2.imread(
        str(image_path)
    )

    if image is None:

        return {
            "quality": 0,
            "skin_score": 0,
            "reasons": [
                "Unable to read image."
            ]
        }


    height, width = image.shape[:2]


    # Image size

    if min(height, width) >= 500:

        size_score = 100

    elif min(height, width) >= 300:

        size_score = 80

    elif min(height, width) >= 150:

        size_score = 60

    else:

        size_score = 25


    # Blur detection

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blur_value = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    blur_score = min(
        100,
        blur_value / 6
    )


    # Brightness

    brightness = float(
        gray.mean()
    )

    lighting_score = max(
        0,
        100 - abs(
            brightness - 135
        ) * 0.75
    )


    # Skin-like pixel detection

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    lower_skin = np.array(
        [0, 20, 40]
    )

    upper_skin = np.array(
        [35, 255, 255]
    )

    skin_mask = cv2.inRange(
        hsv,
        lower_skin,
        upper_skin
    )

    skin_percentage = (
        np.count_nonzero(
            skin_mask
        )
        /
        skin_mask.size
    )

    skin_score = min(
        100,
        skin_percentage * 220
    )


    # Overall quality

    quality = (

        size_score * 0.30

        +

        blur_score * 0.30

        +

        lighting_score * 0.20

        +

        skin_score * 0.20

    )

    quality = round(
        quality,
        1
    )


    reasons = []


    if blur_value < 35:

        reasons.append(
            "The image appears blurry."
        )


    if brightness < 45:

        reasons.append(
            "The image is too dark."
        )


    if brightness > 225:

        reasons.append(
            "The image is overexposed."
        )


    if skin_percentage < 0.06:

        reasons.append(
            "The image does not contain enough skin-like information."
        )


    return {

        "quality": quality,

        "skin_score": round(
            skin_score,
            1
        ),

        "reasons": reasons

    }


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({

        "project":
        "SkinSense AI",

        "status":
        "Backend running",

        "message":
        "SkinSense AI API is working"

    })


# =====================================================
# HEALTH CHECK
# =====================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
        "healthy"

    })


# =====================================================
# ANALYZE IMAGE
# =====================================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze():

    # Check image

    if "image" not in request.files:

        return jsonify({

            "status":
            "error",

            "message":
            "No image uploaded."

        }), 400


    file = request.files["image"]


    # Check filename

    if file.filename == "":

        return jsonify({

            "status":
            "error",

            "message":
            "No image selected."

        }), 400


    # Check extension

    if not allowed_file(
        file.filename
    ):

        return jsonify({

            "status":
            "error",

            "message":
            "Only JPG, JPEG, PNG and WEBP images are allowed."

        }), 400


    # Create unique filename

    filename = secure_filename(
        file.filename
    )

    unique_filename = (
        uuid.uuid4().hex
        +
        "_"
        +
        filename
    )


    image_path = (
        UPLOAD_FOLDER
        /
        unique_filename
    )


    file.save(
        image_path
    )


    try:

        # -----------------------------------------
        # IMAGE QUALITY
        # -----------------------------------------

        quality_result = analyze_image_quality(
            image_path
        )


        quality = quality_result[
            "quality"
        ]

        skin_score = quality_result[
            "skin_score"
        ]

        reasons = quality_result[
            "reasons"
        ]


        # -----------------------------------------
        # REJECT UNSUITABLE IMAGE
        # -----------------------------------------

        if (
            quality < 38
            or
            skin_score < 5
        ):

            return jsonify({

                "status":
                "rejected",

                "message":
                "This image is not suitable for skin condition pre-screening.",

                "quality":
                quality,

                "skin_score":
                skin_score,

                "reasons":
                reasons

            })


        # -----------------------------------------
        # AI PREDICTION
        # -----------------------------------------

        prediction = predict_skin_condition(
            image_path
        )
        # -----------------------------------------
# SAVE SCAN TO DATABASE
# -----------------------------------------

save_scan(
    created_at=datetime.now().isoformat(timespec="seconds"),
    filename=filename,
    quality=quality,
    condition=prediction["condition"],
    confidence=prediction["confidence"],
    risk=prediction["risk"]
)
        


        # -----------------------------------------
        # RESPONSE
        # -----------------------------------------

        return jsonify({

            "status":
            "success",

            "condition":
            prediction["condition"],

            "confidence":
            prediction["confidence"],

            "risk":
            prediction["risk"],

            "quality":
            quality,

            "skin_score":
            skin_score,

            "disclaimer":
            "This is a preliminary AI screening result and is not a medical diagnosis.",

            "next_step":
            "Consult a qualified dermatologist for professional evaluation."

        })


    except Exception as error:

        print(
            "ERROR:",
            error
        )

        return jsonify({

            "status":
            "error",

            "message":
            "Unable to process the image."

        }), 500


    finally:

        # Delete temporary image

        try:

            image_path.unlink()

        except:

            pass

# =====================================================
# HISTORY
# =====================================================

@app.route(
    "/api/history",
    methods=["GET"]
)
def history():
    return jsonify(
        get_history()
    )

# =====================================================
# RUN SERVER
# =====================================================

@app.route("/api/history", methods=["GET"])
def history():
    return jsonify(get_history())
    
if __name__ == "__main__":

    print()
    print(
        "======================================"
    )
    print(
        "       SKINSENSE AI BACKEND"
    )
    print(
        "======================================"
    )
    print(
        "Server: http://127.0.0.1:5000"
    )
    print(
        "API: http://127.0.0.1:5000/api/analyze"
    )
    print(
        "======================================"
    )
    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )
