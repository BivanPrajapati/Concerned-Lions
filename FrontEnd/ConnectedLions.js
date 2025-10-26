// === course-tree.js ===

// List of course prefixes (kept for reference)
const searchWords = [
  'WR','CS','AH','LY','LC','LF','LG','LH','LI','LK','LN','LP','AA','LX','BI',
  'CH','PY','EE','BB','MS','MA','AN','SO','EC','PL','PS','IS','PH','RN','CL',
  'HU','MU','TH','CI','EI','ME','CC'
];

// DOM elements
const inputsBox = document.getElementById("input-box");
const searchButton = document.getElementById("search-button");
const resultsBox = document.querySelector(".result-box");

// --- Display autocomplete suggestions ---
function displaySuggestions(results) {
  const suggestionsHTML = results.map(item => `<li class="suggestion-item">${item}</li>`).join('');
  resultsBox.innerHTML = suggestionsHTML ? `<ul>${suggestionsHTML}</ul>` : '';

  document.querySelectorAll(".suggestion-item").forEach(item => {
    item.onclick = function () {
      inputsBox.value = this.textContent;
      resultsBox.innerHTML = '';
      generateTree();
    };
  });
}

// --- Handle typing for live suggestions ---
inputsBox.addEventListener("keyup", function(e) {
  const input = inputsBox.value.trim();
  if (input.length) {
    const results = searchWords.filter(keyword =>
      keyword.toLowerCase().includes(input.toLowerCase())
    );
    displaySuggestions(results);
  } else {
    resultsBox.innerHTML = '';
  }

  if (e.key === "Enter") generateTree();
});

// --- Generate tree and open in new window ---
async function generateTree() {
  const courseName = inputsBox.value.trim();
  if (!courseName) {
    alert("Please enter a course name");
    return;
  }

  resultsBox.innerHTML = `<p>Generating prerequisite tree for <b>${courseName}</b>... please wait.</p>`;

  const formData = new FormData();
  formData.append("course_name", courseName);

  try {
    const response = await fetch("http://127.0.0.1:8000/generate-tree", {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error("Backend responded with status " + response.status);

    const data = await response.json();

    if (!data.url) throw new Error("No URL returned from backend");

    const fullUrl = `http://127.0.0.1:8000${data.url}`;
    window.open(fullUrl, "_blank");

    resultsBox.innerHTML = "";

  } catch (err) {
    console.error("Request failed:", err);
    resultsBox.innerHTML = `<p style="color:red;">❌ Request failed. Make sure backend is running.</p>`;
  }
}

// --- Search button listener ---
searchButton.addEventListener("click", generateTree);
