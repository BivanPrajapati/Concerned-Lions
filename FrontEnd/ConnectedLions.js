const searchWords = ['WR','CS','AH','LY','LC','LF','LG','LH','LI','LK','LN','LP','AA','LX','BI','CH','PY','EE','BB','MS','MA','AN','SO','EC','PL','PS','IS','PH','RN','CL','HU','MU','TH','CI','EI','ME','CC'];

const resultsBox = document.querySelector(".result-box");
const inputsBox = document.getElementById("input-box");
const searchButton = document.getElementById("search-button");

// --- Live suggestions ---
inputsBox.onkeyup = function () {
    const input = inputsBox.value.trim();
    let results = [];
    if (input.length) {
        results = searchWords.filter(keyword =>
            keyword.toLowerCase().includes(input.toLowerCase())
        );
    }
    displaySuggestions(results);
}

function displaySuggestions(results) {
    const suggestionsHTML = results.map(item => `<li class="suggestion-item">${item}</li>`).join('');
    resultsBox.innerHTML = suggestionsHTML ? `<ul>${suggestionsHTML}</ul>` : '';
    document.querySelectorAll(".suggestion-item").forEach(item => {
        item.onclick = function () {
            inputsBox.value = this.textContent;
            resultsBox.innerHTML = '';
            generateTree();
        }
    });
}

// --- Search triggers ---
searchButton.onclick = generateTree;
inputsBox.addEventListener('keyup', function(event) {
    if (event.key === "Enter") generateTree();
});

// --- Generate tree ---
function generateTree() {
    const courseName = inputsBox.value.trim();
    if (!courseName) {
        alert('Please enter a course name');
        return;
    }

    resultsBox.innerHTML = `<p>Loading prerequisite tree for ${courseName}...</p>`;

    const formData = new FormData();
    formData.append('course_name', courseName);

    fetch('http://localhost:8000/generate-tree', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Open the PNG in a new tab
            const pngURL = `http://localhost:8000/static/prereq_tree.png?${new Date().getTime()}`;
            window.open(pngURL, '_blank');
            resultsBox.innerHTML = '';
        } else {
            alert("Error generating tree");
            resultsBox.innerHTML = '';
        }
    })
    .catch(err => {
        alert("Request failed: " + err);
        resultsBox.innerHTML = '';
    });
}
