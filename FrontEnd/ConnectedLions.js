const searchWords = [
  'WR','CS','AH','LY','LC','LF','LG','LH','LI','LK','LN','LP','AA','LX','BI',
  'CH','PY','EE','BB','MS','MA','AN','SO','EC','PL','PS','IS','PH','RN','CL',
  'HU','MU','TH','CI','EI','ME','CC'
];

const inputsBox = document.getElementById("input-box");
const searchButton = document.getElementById("search-button");
const resultsBox = document.querySelector(".result-box");

// --- Live search suggestions ---
inputsBox.addEventListener("keyup", function(event) {
    const input = inputsBox.value.trim();
    let results = [];
    if (input.length) {
        results = searchWords.filter(keyword =>
            keyword.toLowerCase().includes(input.toLowerCase())
        );
    }
    displaySuggestions(results);

    if (event.key === "Enter") generateTree();
});

function displaySuggestions(results) {
    const suggestionsHTML = results.map(item => `<li class="suggestion-item">${item}</li>`).join('');
    resultsBox.innerHTML = suggestionsHTML ? `<ul>${suggestionsHTML}</ul>` : '';

    document.querySelectorAll(".suggestion-item").forEach(item => {
        item.onclick = function() {
            inputsBox.value = this.textContent;
            resultsBox.innerHTML = '';
            generateTree();
        };
    });
}

// --- Generate tree and open PNG in new window ---
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
        // Fetch the PNG directly
        const response = await fetch("http://127.0.0.1:8000/generate-tree", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }

        // Convert response to blob and open in new tab
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        window.open(blobUrl, "_blank");

        resultsBox.innerHTML = "";
    } catch (err) {
        console.error("Detailed fetch error:", err);
        resultsBox.innerHTML = `<p style="color:red;">
            ❌ Request failed: ${err.message}<br>
            Check if backend is running on <b>http://127.0.0.1:8000</b>
        </p>`;
    }
}

searchButton.addEventListener("click", generateTree);
