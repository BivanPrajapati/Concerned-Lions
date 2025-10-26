// --- Autocomplete Code (with fixes) ---
let searchWords = ['AA', 'AR', 'AM', 'CS', 'DS', 'WR'];

const resultsBox = document.querySelector(".result-box");
const inputsBox = document.getElementById("input-box");

inputsBox.onkeyup = function () {
    let results = []; // <-- FIX: This was 'result' but should be 'results'
    let input = inputsBox.value;
    if (input.length) {
        // Correctly assign to the 'results' array
        results = searchWords.filter((keyword) => {
            return keyword.toLowerCase().includes(input.toLowerCase());
        });
    }
    display(results); // <-- FIX: Pass the 'results' array
}

function display(results) { // <-- FIX: Receive 'results'
    // FIX: Added closing </li> tag
    const content = results.map((list) => {
        return "<li>" + list + "</li>";
    });

    // FIX: Join the array and hide box if empty
    if (content.length) {
        resultsBox.innerHTML = "<ul>" + content.join('') + "</ul>";
    } else {
        resultsBox.innerHTML = "";
    }
}

// --- These functions are not being used ---
// let searchInput = document.getElementById('input-box');
// function Search(){
//     setInterval(drop_bar(), 1500)
// }
// function drop_bar(){
//    searchpop.style.display="block";
// }


// --- Backend Connection Code (Corrected) ---

const URL = 'http://localhost:8000';

function URLfy(path) {
    return URL + path;
}

async function Searchbar() {
    // Get the value from the search input
    const courseInput = document.getElementById('input-box').value.trim();
    const popup = document.querySelector('.search-popup');

    // Check if input is empty
    if (!courseInput) {
        alert('Please enter a course name');
        return;
    }

    // Show a loading message
    popup.innerHTML = `<h3>Generating tree for ${courseInput}...</h3>`;
    popup.style.display = 'block';

    try {
        // Make POST request to the backend
        const response = await fetch(URLfy('/course-tree'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                course_name: courseInput
            })
        });

        // Check if the response is ok
        if (!response.ok) {
            // Try to get JSON error details from the server
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Server error: ${response.statusText}`);
        }

        // --- ✅ THIS IS THE MAIN FIX ---

        // 1. Get the image data as a 'blob' (raw data)
        const imageBlob = await response.blob();

        // 2. Create a temporary local URL for the image
        const imageObjectURL = URL.createObjectURL(imageBlob);

        // 3. Display the image in your popup
        popup.innerHTML = `
            <h3>Prerequisite Tree for ${courseInput}</h3>
            <img src="${imageObjectURL}" alt="Prerequisite tree for ${courseInput}" style="width: 100%; height: auto;">
        `;
        popup.style.display = 'block';

    } catch (error) {
        console.error('Error:', error);
        popup.innerHTML = `<h3 style="color: red;">Error:</h3><p>${error.message}</p>`;
        popup.style.display = 'block';
    }
    
    // We don't need this, it tries to open a local file
    // OpenWindow(); 
}

// This function is not needed
// function OpenWindow(){
//     window.open('src/prereq_tree.png', '_blank');
// }