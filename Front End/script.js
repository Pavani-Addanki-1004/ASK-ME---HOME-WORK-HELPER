async function askQuestion() {
    const question = document.getElementById("questionInput").value.trim();
    const responseDiv = document.getElementById("response");

    if (!question) {
        alert("Please enter a question.");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:5000/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await res.json();
        responseDiv.innerText = "Answer: " + data.answer;
        animateResponse();
    } catch (err) {
        responseDiv.innerText = "Error connecting to the server.";
        animateResponse();
    }
}

async function uploadImage() {
    const fileInput = document.getElementById("imageInput");
    const responseDiv = document.getElementById("response");

    if (fileInput.files.length === 0) {
        alert("Please select an image.");
        return;
    }

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);

    try {
        const res = await fetch("http://127.0.0.1:5000/ask", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        responseDiv.innerText = "Answer: " + data.answer;
        animateResponse();
    } catch (err) {
        responseDiv.innerText = "Image upload failed.";
        animateResponse();
    }
}

function animateResponse() {
    const response = document.getElementById("response");
    response.classList.remove("show");
    setTimeout(() => response.classList.add("show"), 10);
}

function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("questionInput").value = transcript;
        askQuestion();  // Automatically ask after speech
    };

    recognition.onerror = (event) => {
        alert("Speech recognition error: " + event.error);
    };

    recognition.start();
}