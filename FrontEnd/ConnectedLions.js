// let searchpop=document.getElementsByClass('search-popup')
let searchInput = document.getElementById('search-bar');
function Search(){
    setInterval(drop_bar(), 1500)
}
function drop_bar(){
   searchpop.style.display="block";
}


const URL = 'http://localhost:8000';

function URLfy(path) {
    return URL + path;
}

async function Searchbar(){
    // Get the value from the search input
    const courseInput = document.getElementById('search-bar').value.trim();
    
    // Check if input is empty
    if (!courseInput) {
        alert('Please enter a course name');
        return;
    }
    
    try {
        // Make POST request to the backend
        const response = await fetch(URLfy('/course-info'), {
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
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch course info');
        }
        
        // Parse the response
        const data = await response.json();
        
        // Display the results (you can customize this part)
        console.log('Course Info:', data);
        
        // Example: Display in the search-popup div
        const popup = document.querySelector('.search-popup');
        popup.innerHTML = `
            <h3>${data.course_name}</h3>
            <p><strong>Prerequisites:</strong> ${data.prerequisites}</p>
            <p><strong>Hub Areas:</strong> ${data.hub_areas}</p>
        `;
        popup.style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    }
}