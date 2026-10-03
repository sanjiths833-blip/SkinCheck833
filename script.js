/* ==================================================
   SKINSENSE AI
   FRONTEND JAVASCRIPT
================================================== */


/* ================= CONFIG ================= */

const API_URL = "http://127.0.0.1:5000/api";


/* ================= ELEMENTS ================= */

const imageInput =
    document.getElementById("imageInput");

const uploadArea =
    document.getElementById("uploadArea");

const previewContainer =
    document.getElementById("previewContainer");

const imagePreview =
    document.getElementById("imagePreview");

const removeBtn =
    document.getElementById("removeBtn");

const analyzeBtn =
    document.getElementById("analyzeBtn");

const loadingBox =
    document.getElementById("loadingBox");

const emptyResult =
    document.getElementById("emptyResult");

const resultContent =
    document.getElementById("resultContent");

const rejectedContent =
    document.getElementById("rejectedContent");


/* ================= OPEN FILE ================= */

uploadArea.addEventListener(
    "click",
    () => {

        imageInput.click();

    }
);


/* ================= FILE SELECT ================= */

imageInput.addEventListener(
    "change",
    () => {

        const file =
            imageInput.files[0];

        if (file) {

            handleFile(file);

        }

    }
);


/* ================= HANDLE FILE ================= */

function handleFile(file) {

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    if (!allowedTypes.includes(file.type)) {

        alert(
            "Please upload JPG, PNG or WEBP image."
        );

        return;
    }


    if (file.size > 8 * 1024 * 1024) {

        alert(
            "Maximum image size is 8 MB."
        );

        return;
    }


    const reader =
        new FileReader();


    reader.onload = function (event) {

        imagePreview.src =
            event.target.result;

        uploadArea.style.display =
            "none";

        previewContainer.classList.add(
            "active"
        );

        analyzeBtn.disabled =
            false;

    };


    reader.readAsDataURL(file);

}


/* ================= DRAG OVER ================= */

uploadArea.addEventListener(
    "dragover",
    (event) => {

        event.preventDefault();

        uploadArea.classList.add(
            "dragover"
        );

    }
);


/* ================= DRAG LEAVE ================= */

uploadArea.addEventListener(
    "dragleave",
    () => {

        uploadArea.classList.remove(
            "dragover"
        );

    }
);


/* ================= DROP ================= */

uploadArea.addEventListener(
    "drop",
    (event) => {

        event.preventDefault();

        uploadArea.classList.remove(
            "dragover"
        );

        const file =
            event.dataTransfer.files[0];

        if (file) {

            handleFile(file);

        }

    }
);


/* ================= REMOVE IMAGE ================= */

removeBtn.addEventListener(
    "click",
    resetUpload
);


function resetUpload() {

    imageInput.value = "";

    imagePreview.src = "";

    uploadArea.style.display =
        "flex";

    previewContainer.classList.remove(
        "active"
    );

    analyzeBtn.disabled =
        true;

}


/* ================= ANALYZE ================= */

analyzeBtn.addEventListener(
    "click",
    analyzeImage
);


async function analyzeImage() {

    const file =
        imageInput.files[0];


    if (!file) {

        alert(
            "Please select an image first."
        );

        return;
    }


    /* SHOW LOADING */

    loadingBox.classList.add(
        "active"
    );

    analyzeBtn.disabled =
        true;


    try {

        const formData =
            new FormData();

        formData.append(
            "image",
            file
        );


        /*
            Send image to Python Flask
            backend.
        */

        const response =
            await fetch(
                `${API_URL}/analyze`,
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Analysis failed."
            );

        }


        /* CHECK REJECTION */

        if (
            data.status ===
            "rejected"
        ) {

            showRejectedResult(data);

        }

        else {

            showResult(data);

            loadHistory();

        }

    }

    catch (error) {

        console.error(error);

        alert(
            "Backend connection failed.\n\n" +
            "Make sure your Python Flask server is running."
        );

    }

    finally {

        loadingBox.classList.remove(
            "active"
        );

        analyzeBtn.disabled =
            false;

    }

}


/* ================= SHOW RESULT ================= */

function showResult(data) {

    emptyResult.style.display =
        "none";

    rejectedContent.classList.remove(
        "active"
    );

    resultContent.classList.add(
        "active"
    );


    const riskElement =
        document.getElementById(
            "riskLevel"
        );


    riskElement.textContent =
        data.risk.toUpperCase();


    riskElement.className =
        "";


    riskElement.classList.add(
        data.risk
    );


    document.getElementById(
        "confidence"
    ).textContent =
        data.confidence;


    document.getElementById(
        "condition"
    ).textContent =
        data.condition;


    document.getElementById(
        "resultDisclaimer"
    ).textContent =
        data.disclaimer;


    document.getElementById(
        "imageQuality"
    ).textContent =
        data.quality;


    document.getElementById(
        "skinSignal"
    ).textContent =
        data.skin_score;


    document.getElementById(
        "nextStep"
    ).textContent =
        data.next_step;


    /* RISK BAR */

    const progress =
        document.getElementById(
            "riskProgress"
        );


    progress.style.width =
        data.confidence + "%";


    if (data.risk === "low") {

        progress.style.background =
            "#00e6a3";

    }

    else if (
        data.risk === "medium"
    ) {

        progress.style.background =
            "#ffc83d";

    }

    else {

        progress.style.background =
            "#ff5570";

    }

}


/* ================= REJECTED RESULT ================= */

function showRejectedResult(data) {

    emptyResult.style.display =
        "none";

    resultContent.classList.remove(
        "active"
    );

    rejectedContent.classList.add(
        "active"
    );


    document.getElementById(
        "rejectMessage"
    ).textContent =
        data.message;


    const reasons =
        document.getElementById(
            "rejectReasons"
        );


    reasons.innerHTML = "";


    if (data.reasons) {

        data.reasons.forEach(
            reason => {

                const li =
                    document.createElement(
                        "li"
                    );

                li.textContent =
                    reason;

                reasons.appendChild(
                    li
                );

            }
        );

    }

}


/* ================= RETRY ================= */

document
    .getElementById("retryBtn")
    .addEventListener(
        "click",
        () => {

            rejectedContent.classList.remove(
                "active"
            );

            emptyResult.style.display =
                "flex";

            resetUpload();

        }
    );


/* ================= HISTORY ================= */

async function loadHistory() {

    try {

        const response =
            await fetch(
                `${API_URL}/history`
            );


        const data =
            await response.json();


        const historyList =
            document.getElementById(
                "historyList"
            );


        if (
            !data ||
            data.length === 0
        ) {

            historyList.innerHTML =
                `<div class="no-history">
                    No previous scans available.
                </div>`;

            return;
        }


        historyList.innerHTML =
            data.map(
                scan => `

                <div class="history-row">

                    <div>
                        <strong>
                            ${scan.filename}
                        </strong>

                        <br>

                        ${scan.created_at}
                    </div>

                    <div>
                        ${scan.condition}
                    </div>

                    <div>
                        ${scan.confidence}%
                    </div>

                    <div
                        class="${scan.risk}"
                    >
                        ${scan.risk}
                    </div>

                </div>

                `
            ).join("");

    }

    catch (error) {

        console.log(
            "History unavailable."
        );

    }

}


/* ================= REFRESH ================= */

document
    .getElementById("refreshBtn")
    .addEventListener(
        "click",
        loadHistory
    );


/* ================= INITIAL ================= */

loadHistory();