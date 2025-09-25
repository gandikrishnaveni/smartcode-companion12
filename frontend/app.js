// File: frontend/app.js

// --- FIX ---
// The backend routes are all under the "/api/v1/" prefix.
// We add that prefix to the base endpoint URL here.
const ENDPOINT = "http://127.0.0.1:8000/api/v1";
// ----------------------------------------------------

// --- Get Element References ---
const runBtn = document.getElementById("runBtn");
const debugBtn = document.getElementById("debugBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");

const codeInput = document.getElementById("codeInput");
const outputDiv = document.getElementById("output");
const statusDiv = document.getElementById("status");
const skillSelect = document.getElementById("skill");


// ---------------- Run Code ----------------
runBtn.addEventListener("click", async () => {
  const code = codeInput.value.trim();
  if (!code) {
    outputDiv.textContent = "⚠ Please enter some code first!";
    return;
  }

  outputDiv.textContent = "▶ Running code...";
  statusDiv.textContent = "Executing...";

  try {
    const res = await fetch(`${ENDPOINT}/run-code`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code,
        level: skillSelect.value || "beginner"  // include level if model requires it
      }),
    });

    const data = await res.json();
    if (data.error) {
      outputDiv.textContent = `❌ Error:\n${data.error}`;
      statusDiv.textContent = "Error";
    } else {
      outputDiv.textContent = data.output || "(no output)";
      statusDiv.textContent = "✅ Complete";
    }
  } catch (err) {
    statusDiv.textContent = "⚠ Connection Failed";
    outputDiv.textContent = `Failed to connect. Error: ${err}`;
  }
});

// ---------------- Debug ----------------
// ---------------- Debug ----------------
debugBtn.addEventListener("click", async () => {
  const code = codeInput.value.trim();
  if (!code) {
    outputDiv.textContent = "⚠ Please enter some code first!";
    return;
  }

  const level = skillSelect.value || "beginner";

  statusDiv.textContent = "🐞 Debugging...";
  outputDiv.textContent = "Sending code to the debugger...";

  try {
    const res = await fetch(`${ENDPOINT}/debug`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, level }),
    });

    const data = await res.json();

    if (res.ok) {
      statusDiv.textContent = "✅ Debug complete";

      if (data.error) {
        outputDiv.textContent = `🐞 Fixed Code:\n${data.fixed_code}\n\nError:\n${data.error}\n\nExplanation:\n${data.explanation}`;
      } else {
        outputDiv.textContent = `🐞 Fixed Code:\n${data.fixed_code}\n(No errors detected)`;
      }
    } else {
      statusDiv.textContent = "❌ Debug error";
      outputDiv.textContent = `Error from backend:\n${JSON.stringify(data, null, 2)}`;
    }
  } catch (err) {
    statusDiv.textContent = "⚠ Connection Failed";
    outputDiv.textContent = `Failed to connect to the backend. Error: ${err}`;
  }
});

// ---------------- Comment Code ----------------
// ---------------- Comment Code ----------------
const commentBtn = document.getElementById("commentBtn");

commentBtn.addEventListener("click", async () => {
  const code = codeInput.value.trim();
  if (!code) {
    outputDiv.textContent = "⚠ Please enter some code first!";
    return;
  }

  outputDiv.textContent = "💡 Generating comments...";
  statusDiv.textContent = "Commenting...";

  try {
    const res = await fetch(`${ENDPOINT}/comment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, level: skillSelect.value || "beginner" }),
    });

    const data = await res.json();

    if (res.ok) {
      // Replace code in editor with annotated version (code + inline comments)
      codeInput.value = data.comment; 
      outputDiv.textContent = "✅ Code explained in comments!";
      statusDiv.textContent = "Complete";
    } else {
      outputDiv.textContent = `❌ Error from backend:\n${JSON.stringify(data, null, 2)}`;
      statusDiv.textContent = "Error";
    }
  } catch (err) {
    outputDiv.textContent = `⚠ Failed to connect to backend. Error: ${err}`;
    statusDiv.textContent = "Connection Failed";
  }
});


// ---------------- Analyze / Comment ----------------
analyzeBtn.addEventListener("click", async () => {
  const code = codeInput.value;
  const level = skillSelect.value;
  outputDiv.textContent = "🧠 Analyzing...";
  statusDiv.textContent = "Analyzing...";

  try {
    // This will now correctly call http://127.0.0.1:8000/api/v1/comment
    const res = await fetch(`${ENDPOINT}/comment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, level }), // Matches the CodeRequest model
    });

    const data = await res.json();
    if (res.ok) {
      statusDiv.textContent = "✅ Analysis Complete";
      outputDiv.textContent = `💡 Comments:\n\n${data.comment}`;
    } else {
      statusDiv.textContent = "❌ Analysis Error";
      outputDiv.textContent = `Error from backend:\n${JSON.stringify(data, null, 2)}`;
    }
  } catch (err) {
    statusDiv.textContent = "⚠ Connection Failed";
    outputDiv.textContent = `Failed to connect to the backend. Is it running?\nError: ${err}`;
  }
});

// ---------------- Clear ----------------
clearBtn.addEventListener("click", () => {
  codeInput.value = "";
  outputDiv.textContent = "(no output)";
  statusDiv.textContent = "Idle";
});

// ---------------- Copy ----------------
copyBtn.addEventListener("click", () => {
  const output = outputDiv.textContent;
  navigator.clipboard.writeText(output).then(() => {
    // --- UX Improvement: No more alert() ---
    const originalText = copyBtn.textContent;
    copyBtn.textContent = "Copied!";
    setTimeout(() => {
      copyBtn.textContent = originalText;
    }, 1500); // Revert back after 1.5 seconds
  }).catch(err => {
    console.error('Failed to copy text: ', err);
  });
});
codeInput.addEventListener("keydown", async (e) => {
  if (e.key === "Enter") {
    const currentLine = getCurrentLineText(); // implement this
    const response = await fetch("/api/v1/comment-line", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: currentLine, level: userLevel }),
    });
    const data = await response.json();
    showCommentForLine(currentLineIndex, data.comment); // render inline
  }
});

// ---------------- Download ----------------
downloadBtn.addEventListener("click", () => {
  const output = outputDiv.textContent;
  const blob = new Blob([output], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "smart-code-output.txt";
  document.body.appendChild(a); // Required for Firefox
  a.click();
  document.body.removeChild(a);
});
// ---------------- Voice → Comments ----------------
// --- Frontend: Record & Send Audio for Watson STT ---
// ---------------- Voice → Comments ----------------
const voiceBtn = document.getElementById("voiceBtn");
// if needed for consistency
voiceBtn.addEventListener("click", () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("⚠ Your browser does not support speech recognition. Use Chrome or Edge.");
    return;
  }

  outputDiv.textContent = "🎤 Get ready, speaking starts in 2 seconds...";
  voiceBtn.textContent = "Preparing...";

  setTimeout(() => {
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    voiceBtn.textContent = "🎤 Recording...";
    outputDiv.textContent = "Listening now! Speak clearly.";

    recognition.start();

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.trim();
      codeInput.value += `\n# Voice Instruction: ${transcript}`;
      outputDiv.textContent = "✅ Voice comment added!";
      voiceBtn.textContent = "Start Voice Comment";
    };

    recognition.onerror = (event) => {
      outputDiv.textContent = `⚠ Speech recognition failed: ${event.error}`;
      voiceBtn.textContent = "Start Voice Comment";
    };

    recognition.onend = () => {
      voiceBtn.textContent = "Start Voice Comment";
    };
  }, 2000); // 2-second countdown
});
