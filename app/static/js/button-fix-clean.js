// Clean solution for Jira buttons
window.addEventListener('load', function() {
    console.log("📋 Clean Jira button solution loading");
    
    // Define a single global click handler for all Jira buttons
    document.addEventListener('click', function(event) {
        // Get the clicked element
        const target = event.target;
        
        // Check if it has the jira-button class or is a child of it
        const jiraButton = target.closest('.jira-button');
        
        if (jiraButton) {
            // Get ticket ID from data attribute
            const ticketId = jiraButton.getAttribute('data-ticket-id');
            if (ticketId) {
                event.preventDefault();
                event.stopPropagation();
                console.log(`Jira button clicked for ticket ${ticketId}`);
                
                // Directly call the API without relying on other functions
                sendToJiraAPI(ticketId, jiraButton);
            }
        }
    });
    
    // Function to add buttons to all tickets with test cases
    function addButtonsToTickets() {
        console.log("Adding clean Jira buttons to tickets with test cases");
        
        // Find all tickets with test cases (that have a "Test Cases Generated" badge)
        const ticketsWithTestCases = document.querySelectorAll('.ticket-item .test-cases-badge');
        
        ticketsWithTestCases.forEach(function(badge) {
            const ticketHeader = badge.closest('.ticket-header');
            const ticketItem = badge.closest('.ticket-item');
            
            if (!ticketHeader || !ticketItem) return;
            
            // Get ticket ID from the ticket item
            const ticketId = ticketItem.id.replace('ticket-', '');
            const actionsContainer = ticketHeader.querySelector('.ticket-actions');
            
            if (!actionsContainer) return;
            
            // Check if button already exists
            if (actionsContainer.querySelector(`.jira-button[data-ticket-id="${ticketId}"]`)) {
                return;
            }
            
            // Create a simple button with inline styling for reliability
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'jira-button';
            button.setAttribute('data-ticket-id', ticketId);
            button.innerHTML = 'Send to Jira';
            
            // Use inline styles for maximum reliability
            button.style.cssText = `
                background-color: #0052cc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                margin-left: 10px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer !important;
                position: relative;
                z-index: 10000;
                pointer-events: auto;
            `;
            
            // Add button after the badge
            actionsContainer.insertBefore(button, badge.nextSibling);
            
            console.log(`Added clean button for ticket ${ticketId}`);
        });
        
        // Also add HTML form buttons as fallback for each test cases container
        const testCasesContainers = document.querySelectorAll('.ticket-test-cases');
        testCasesContainers.forEach(function(container) {
            // Get ticket ID from closest ticket item
            const ticketItem = container.closest('.ticket-item');
            if (!ticketItem) return;
            
            const ticketId = ticketItem.id.replace('ticket-', '');
            
            // Skip if there are no test cases or if there's already a form
            if (container.querySelector('.no-test-cases') || 
                container.querySelector('.jira-form-fallback')) {
                return;
            }
            
            // Create a form fallback container
            const formContainer = document.createElement('div');
            formContainer.className = 'jira-form-fallback';
            formContainer.style.cssText = 'margin: 20px 0; padding: 15px; text-align: center; border-top: 1px solid #ddd;';
            
            // Create the form
            formContainer.innerHTML = `
                <form action="/jira_button/${ticketId}" method="get" style="margin: 0;">
                    <button type="submit" style="
                        background-color: #0052cc;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 10px 20px;
                        font-size: 16px;
                        font-weight: 500;
                        cursor: pointer;
                        position: relative;
                        z-index: 10000;
                    ">
                        Send Test Cases to Jira
                    </button>
                </form>
            `;
            
            // Add to the container
            container.appendChild(formContainer);
            
            console.log(`Added form fallback for ticket ${ticketId}`);
        });
    }
    
    // Function to directly call the API
    function sendToJiraAPI(ticketId, buttonElement) {
        // Show loading state
        if (buttonElement) {
            buttonElement.disabled = true;
            buttonElement.textContent = 'Sending...';
            buttonElement.style.backgroundColor = '#7f8c8d';
        }
        
        console.log(`Sending API request to /send_to_jira/${ticketId}`);
        
        // Make the API call
        fetch(`/send_to_jira/${ticketId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log(`Received response:`, data);
            
            if (data.success) {
                // Success state
                console.log(`Successfully sent to Jira for ticket ${ticketId}`);
                
                // Update all buttons for this ticket
                const allButtons = document.querySelectorAll(`.jira-button[data-ticket-id="${ticketId}"]`);
                allButtons.forEach(btn => {
                    btn.textContent = 'Sent ✓';
                    btn.style.backgroundColor = '#2ecc71';
                    btn.disabled = true;
                });
                
                // Update form fallbacks too
                const forms = document.querySelectorAll(`.jira-form-fallback form[action="/jira_button/${ticketId}"]`);
                forms.forEach(form => {
                    const btn = form.querySelector('button');
                    if (btn) {
                        btn.textContent = 'Sent ✓';
                        btn.style.backgroundColor = '#2ecc71';
                        btn.disabled = true;
                    }
                });
                
                // Show success message in test cases container
                const testCasesContainer = document.getElementById(`test-cases-${ticketId}`);
                if (testCasesContainer) {
                    const successMsg = document.createElement('div');
                    successMsg.className = 'jira-success-message';
                    successMsg.textContent = '✅ Test cases successfully sent to Jira';
                    successMsg.style.cssText = 'color: #2ecc71; font-weight: bold; margin: 10px 0; padding: 10px; background-color: #e8f8f5; border-radius: 4px; text-align: center;';
                    testCasesContainer.appendChild(successMsg);
                }
            } else {
                // Error state
                console.error(`Error sending to Jira: ${data.message}`);
                
                // Show error and reset buttons
                alert(`Error sending to Jira: ${data.message}`);
                
                const allButtons = document.querySelectorAll(`.jira-button[data-ticket-id="${ticketId}"]`);
                allButtons.forEach(btn => {
                    btn.textContent = 'Send to Jira';
                    btn.style.backgroundColor = '#0052cc';
                    btn.disabled = false;
                });
            }
        })
        .catch(error => {
            console.error(`Error in API call: ${error}`);
            alert(`Error sending to Jira. Please try again.`);
            
            // Reset buttons
            const allButtons = document.querySelectorAll(`.jira-button[data-ticket-id="${ticketId}"]`);
            allButtons.forEach(btn => {
                btn.textContent = 'Send to Jira';
                btn.style.backgroundColor = '#0052cc';
                btn.disabled = false;
            });
        });
    }
    
    // Run initially with a delay to ensure DOM is loaded
    setTimeout(addButtonsToTickets, 1000);
    
    // Check periodically for new tickets or test cases
    setInterval(addButtonsToTickets, 3000);
    
    // Make the API function globally available
    window.sendToJiraAPI = sendToJiraAPI;
});
