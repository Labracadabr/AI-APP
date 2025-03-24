const items = ["cube", "face", "car", "bicycle", "mountain", "dog", "house", "tree", "book", "apple", "cat"];
document.getElementById("draw-item").textContent = items[Math.floor(Math.random() * items.length)];

const canvas = document.getElementById("drawingCanvas");
const ctx = canvas.getContext("2d");
let drawing = false;
let brushSize = 5;
let paths = [];
let currentPath = [];

function setBrushSize(size) {
    brushSize = size;
}

function startDraw(event) {
    drawing = true;
    currentPath = [];
}

function draw(event) {
    if (!drawing) return;
    ctx.fillStyle = "black";
    ctx.beginPath();
    ctx.arc(event.offsetX, event.offsetY, brushSize / 2, 0, Math.PI * 2);
    ctx.fill();
    currentPath.push({ x: event.offsetX, y: event.offsetY, size: brushSize });
}

function stopDraw() {
    drawing = false;
    if (currentPath.length > 0) paths.push([...currentPath]);
}

function undo() {
    if (paths.length === 0) return;
    paths.pop();
    redraw();
}

function clearCanvas() {
    paths = [];
    redraw();
}

function redraw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    paths.forEach(path => {
        path.forEach(point => {
            ctx.fillStyle = "black";
            ctx.beginPath();
            ctx.arc(point.x, point.y, point.size / 2, 0, Math.PI * 2);
            ctx.fill();
        });
    });
}

async function submitDrawing() {
    document.getElementById("loading").classList.remove("hidden");

    // Convert canvas to Base64
    const dataUrl = canvas.toDataURL("image/png");
    const base64Image = dataUrl.split(",")[1];  // Remove "data:image/png;base64,"

    const itemName = document.getElementById("draw-item").textContent;  // Get the item to draw

    // Prepare the payload
    const payload = {
        image: base64Image,
        item_name: itemName
    };

    try {
        const response = await fetch("/api/submit-drawing", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        document.getElementById("loading").classList.add("hidden");

        if (result.choices) {
            alert(result.choices[0].message.content);
        } else {
            alert("No response from AI.");
        }
    } catch (error) {
        document.getElementById("loading").classList.add("hidden");
        alert("Error submitting drawing.");
    }
}

canvas.addEventListener("mousedown", startDraw);
canvas.addEventListener("mousemove", draw);
canvas.addEventListener("mouseup", stopDraw);
