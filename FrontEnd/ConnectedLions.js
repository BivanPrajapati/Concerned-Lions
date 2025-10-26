// === course-tree.js ===

// List of course prefixes
const searchWords = [
  'WR','CS','AH','LY','LC','LF','LG','LH','LI','LK','LN','LP','AA','LX','BI',
  'CH','PY','EE','BB','MS','MA','AN','SO','EC','PL','PS','IS','PH','RN','CL',
  'HU','MU','TH','CI','EI','ME','CC'
];

// DOM elements
const resultsBox = document.querySelector(".result-box");
const inputsBox = document.getElementById("input-box");
const searchButton = document.getElementById("search-button");

// --- Live suggestions ---
inputsBox.addEventListener("keyup", function(event) {
  const input = inputsBox.value.trim();
  let results = [];
  if (input.length) {
    results = searchWords.filter(keyword =>
      keyword.toLowerCase().includes(input.toLowerCase())
    );
  }
  displaySuggestions(results);

  // Trigger search on Enter
  if (event.key === "Enter") generateTree();
});

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

// --- Search button ---
searchButton.addEventListener("click", generateTree);

// --- Generate tree using blob ---
async function generateTree() {
  const courseName = inputsBox.value.trim();
  if (!courseName) {
    alert('Please enter a course name');
    return;
  }

  resultsBox.innerHTML = `<p>Loading prerequisite tree for <b>${courseName}</b>... please wait (up to 1 minute).</p>`;

  const formData = new FormData();
  formData.append('course_name', courseName);

  try {
    // Fetch the PNG as blob (backend waits until fully ready)
    const response = await fetch('http://127.0.0.1:8000/generate-tree', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error("Backend responded with status " + response.status);

    const blob = await response.blob();

    // Create a temporary blob URL
    const imgURL = URL.createObjectURL(blob);

    // Open PNG in a new tab
    window.open(imgURL, '_blank');

    resultsBox.innerHTML = '';

  } catch (err) {
    console.error("Request failed:", err);
    resultsBox.innerHTML = `<p style="color:red;">Request failed. Make sure backend is running and frontend is served via HTTP.</p>`;
    alert("Request failed. Make sure the frontend is served via HTTP and backend is running.");
  }
}
