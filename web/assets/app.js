const form = document.getElementById("ask-form");
const questionInput = document.getElementById("question");
const askBtn = document.getElementById("ask-btn");
const statusEl = document.getElementById("status");
const results = document.getElementById("results");
const errorBox = document.getElementById("error-box");
const summaryEl = document.getElementById("summary");
const sqlEl = document.getElementById("sql");
const rowsEl = document.getElementById("rows");

for (const chip of document.querySelectorAll(".chip")) {
  chip.addEventListener("click", () => {
    questionInput.value = chip.dataset.q || "";
    questionInput.focus();
  });
}

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

function setLoadingState(isLoading) {
  askBtn.disabled = isLoading;
  askBtn.textContent = isLoading ? "Running..." : "Ask Agent";
  statusEl.textContent = isLoading ? "Generating SQL and executing query..." : "";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = questionInput.value.trim();
  if (!question) {
    statusEl.textContent = "Please enter a question first.";
    questionInput.focus();
    return;
  }

  setLoadingState(true);
  errorBox.hidden = true;

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Request failed");
    }

    summaryEl.textContent = payload.summary;
    sqlEl.textContent = payload.sql;
    rowsEl.textContent = payload.rows;
    results.hidden = false;
    statusEl.textContent = "Done.";
  } catch (error) {
    errorBox.textContent = `Error: ${error.message}`;
    errorBox.hidden = false;
    statusEl.textContent = "";
  } finally {
    setLoadingState(false);
  }
});
