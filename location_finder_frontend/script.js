document.addEventListener('DOMContentLoaded', () => {
    // --- CONFIGURATION ---
    // PASTE YOUR GOOGLE CLOUD FUNCTION TRIGGER URL HERE
    const BACKEND_URL = 'PASTE_YOUR_URL_HERE'; 

    // --- ELEMENT REFERENCES ---
    const findBtn = document.getElementById('find-btn');
    const regionInput = document.getElementById('region');
    const locationTypesContainer = document.getElementById('location-types-container');
    const addTypeBtn = document.getElementById('add-type-btn');
    const resultsOutput = document.getElementById('results-output');
    const loadingSpinner = document.getElementById('loading-spinner');

    // --- EVENT LISTENERS ---
    addTypeBtn.addEventListener('click', () => {
        const newInput = document.createElement('input');
        newInput.type = 'text';
        newInput.className = 'location-type';
        newInput.placeholder = 'Another location type...';
        locationTypesContainer.appendChild(newInput);
    });

    findBtn.addEventListener('click', async () => {
        if (BACKEND_URL === 'PASTE_YOUR_URL_HERE') {
            alert('ERROR: Please update the BACKEND_URL in script.js with your Cloud Function URL.');
            return;
        }

        // 1. Get user input
        const region = regionInput.value.trim();
        const locationTypeInputs = document.querySelectorAll('.location-type');
        
        const locationTypes = Array.from(locationTypeInputs)
            .map(input => input.value.trim())
            .filter(type => type !== ''); // Filter out empty strings

        // 2. Validate input
        if (!region) {
            alert('Please enter a region.');
            return;
        }
        if (locationTypes.length < 2) {
            alert('Please enter at least two location types.');
            return;
        }

        // 3. Prepare for API call
        resultsOutput.innerHTML = '';
        loadingSpinner.classList.remove('hidden');
        findBtn.disabled = true;

        try {
            // 4. Send data to backend
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    region: region,
                    location_types: locationTypes
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                // Display error from backend if available
                throw new Error(data.error || 'An unknown error occurred.');
            }

            // 5. Display results
            displayResults(data);

        } catch (error) {
            resultsOutput.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        } finally {
            // 6. Clean up UI
            loadingSpinner.classList.add('hidden');
            findBtn.disabled = false;
        }
    });

    // --- HELPER FUNCTIONS ---
    function displayResults(pairs) {
        if (!pairs || pairs.length === 0) {
            resultsOutput.innerHTML = '<p>No matching pairs found. Try a different region or location types.</p>';
            return;
        }

        const html = pairs.map((pair, index) => `
            <div class="pair">
                <h3>Pair ${index + 1}</h3>
                <p>
                    <span class="location-name">${pair.location1.type}:</span> ${pair.location1.name}
                    <br>
                    <small>${pair.location1.address}</small>
                </p>
                <p>
                    <span class="location-name">${pair.location2.type}:</span> ${pair.location2.name}
                    <br>
                    <small>${pair.location2.address}</small>
                </p>
                <p><strong>Distance:</strong> ${pair.distance_text} (${pair.duration_text})</p>
            </div>
        `).join('');

        resultsOutput.innerHTML = html;
    }
});
