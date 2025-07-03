document.addEventListener('DOMContentLoaded', function() {
    // Get all script elements
    const scripts = [
        {
            name: 'fetch_backlog',
            runButton: document.getElementById('run-fetch-backlog'),
            stopButton: document.getElementById('stop-fetch-backlog'),
            statusElement: document.getElementById('fetch-backlog-status'),
            outputElement: document.getElementById('fetch-backlog-output')
        },
        {
            name: 'generate_questions',
            runButton: document.getElementById('run-generate-questions'),
            stopButton: document.getElementById('stop-generate-questions'),
            statusElement: document.getElementById('generate-questions-status'),
            outputElement: document.getElementById('generate-questions-output')
        },
        {
            name: 'generate_test_cases',
            runButton: document.getElementById('run-generate-test-cases'),
            stopButton: document.getElementById('stop-generate-test-cases'),
            statusElement: document.getElementById('generate-test-cases-status'),
            outputElement: document.getElementById('generate-test-cases-output')
        }
    ];

    // Initialize status colors
    updateStatusColors();

    // Add event listeners to all run buttons
    scripts.forEach(script => {
        // Run button
        script.runButton.addEventListener('click', function() {
            runScript(script.name);
        });

        // Stop button
        script.stopButton.addEventListener('click', function() {
            stopScript(script.name);
        });
    });

    // Function to run a script
    function runScript(scriptName) {
        fetch(`/run/${scriptName}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
            } else {
                // Start polling for status
                startPolling(scriptName);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Function to stop a script
    function stopScript(scriptName) {
        fetch(`/stop/${scriptName}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
            } else {
                // Update UI
                updateScriptStatus(scriptName, data);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Function to start polling for status
    function startPolling(scriptName) {
        const intervalId = setInterval(() => {
            fetch(`/status/${scriptName}`)
                .then(response => response.json())
                .then(data => {
                    updateScriptStatus(scriptName, data);
                    
                    // If script is not running anymore, stop polling
                    if (data.status !== 'running') {
                        clearInterval(intervalId);
                        
                        // Refresh page to show view buttons if completed
                        if (data.status === 'completed') {
                            setTimeout(() => {
                                location.reload();
                            }, 1000);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    clearInterval(intervalId);
                });
        }, 1000);
    }

    // Function to update the UI for a script
    function updateScriptStatus(scriptName, data) {
        const script = scripts.find(s => s.name === scriptName);
        if (!script) return;

        // Update status
        script.statusElement.textContent = data.status;
        script.statusElement.setAttribute('data-status', data.status);
        
        // Update buttons
        if (data.status === 'running') {
            script.runButton.disabled = true;
            script.stopButton.disabled = false;
        } else {
            script.runButton.disabled = false;
            script.stopButton.disabled = true;
        }

        // Update output
        script.outputElement.innerHTML = '';
        if (data.output && data.output.length > 0) {
            data.output.forEach(line => {
                const div = document.createElement('div');
                div.textContent = line;
                script.outputElement.appendChild(div);
            });
            // Scroll to bottom
            script.outputElement.scrollTop = script.outputElement.scrollHeight;
        }

        // Update status colors
        updateStatusColors();
    }

    // Function to update status colors
    function updateStatusColors() {
        const statusElements = document.querySelectorAll('.status-value');
        statusElements.forEach(element => {
            const status = element.textContent.trim().toLowerCase();
            element.setAttribute('data-status', status);
        });
    }

    // Poll for all script statuses on page load
    scripts.forEach(script => {
        fetch(`/status/${script.name}`)
            .then(response => response.json())
            .then(data => {
                updateScriptStatus(script.name, data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});
