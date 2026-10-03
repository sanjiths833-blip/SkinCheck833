import cv2


# =====================================================
# SKINSENSE AI PREDICTOR
# =====================================================

def predict_skin_condition(image_path):

    """
    DEMO AI PREDICTION

    Replace this function later with
    your trained machine learning model.

    This is NOT a medical diagnosis.
    """


    image = cv2.imread(
        str(image_path)
    )


    if image is None:

        raise ValueError(
            "Unable to read image."
        )


    # Resize

    image = cv2.resize(
        image,
        (224, 224)
    )


    # HSV

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )


    # Grayscale

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    # Saturation

    saturation = (

        hsv[:, :, 1].mean()

        /

        255

    )


    # Brightness

    brightness = (

        gray.mean()

        /

        255

    )


    # Texture

    texture = min(

        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
        /
        800,

        1

    )


    # Demo signal

    signal = (

        saturation * 0.45

        +

        texture * 0.35

        +

        (1 - brightness) * 0.20

    )


    # Confidence

    confidence = (

        58
        +
        signal * 25

    )


    confidence = round(

        min(
            confidence,
            95
        ),

        1

    )


    # Classification

    if signal < 0.38:

        risk = "low"

        condition = (
            "No strong visual risk signal"
        )


    elif signal < 0.62:

        risk = "medium"

        condition = (
            "Needs visual review"
        )


    else:

        risk = "high"

        condition = (
            "Higher visual risk signal"
        )


    return {

        "condition":
        condition,

        "confidence":
        confidence,

        "risk":
        risk

    }