// Diagnostic Jira button solution with verbose logging
console.log("🔍 DIAGNOSTIC JIRA BUTTON SCRIPT LOADED");

window.addEventListener('load', function() {
    console.log("🔍 DIAGNOSTIC JIRA BUTTON LOAD EVENT TRIGGERED");
    
    // Define a single global click handler for all Jira buttons
    document.addEventListener('click', function(event) {
        console.log("🔍 DOCUMENT CLICK EVENT:", event.target);
        
        // Get the clicked element
        const target = event.target;
        
        // Check if it has the jira-button class or is a child of it
        const jiraButton = target.closest('.jira-button');
        
        if (jiraButton) {
            console.log("🔍 JIRA BUTTON CLICKED:", jiraButton);
            
            // Get ticket ID from data attribute
            const ticketId = jiraButton.getAttribute('data-ticket-id');
            console.log("🔍 TICKET ID:", ticketId);
            
            if (ticketId) {
                event.preventDefault();
                event.stopPropagation();
                console.log("🔍 CALLING SEND TO JIRA API FOR TICKET:", ticketId);
                
                // Directly call the API without relying on other functions
                console.log("🔍 Making direct API call to send_to_jira/" + ticketId);
                
                // Show loading state
                jiraButton.disabled = true;
                jiraButton.textContent = 'Sending...';
                jiraButton.style.backgroundColor = '#7f8c8d';
                
                // Add a timestamp to force a new request
                const requestPayload = { timestamp: new Date().toISOString() };
                
                // Make explicit fetch call with detailed logging
                fetch(`/send_to_jira/${ticketId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(requestPayload)
                })
                .then(response => {
                    console.log("🔍 JIRA API RESPONSE:", response);
                    console.log("🔍 JIRA API STATUS:", response.status);
                    console.log("🔍 JIRA API HEADERS:", [...response.headers.entries()]);
                    
                    // Check response status before attempting to parse JSON
                    if (!response.ok) {
                        console.error(`🔍 Server returned ${response.status}: ${response.statusText}`);
                        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                    }
                    
                    return response.json();
                })
            } else {
                console.error("🔍 NO TICKET ID FOUND ON BUTTON:", jiraButton);
            }
        }
    });
    
    // Function to add buttons to all tickets with test cases
    function addDiagnosticButtons() {
        console.log("🔍 ADDING DIAGNOSTIC JIRA BUTTONS");
        
        // Find all tickets with test cases (that have a "Test Cases Generated" badge)
        const ticketsWithTestCases = document.querySelectorAll('.ticket-item .test-cases-badge');
        console.log("🔍 FOUND TICKETS WITH TEST CASES:", ticketsWithTestCases.length);
        
        ticketsWithTestCases.forEach(function(badge) {
            const ticketHeader = badge.closest('.ticket-header');
            const ticketItem = badge.closest('.ticket-item');
            
            if (!ticketHeader || !ticketItem) {
                console.error("🔍 COULDN'T FIND TICKET HEADER OR ITEM FOR BADGE:", badge);
                return;
            }
            
            // Get ticket ID from the ticket item
            const ticketId = ticketItem.id.replace('ticket-', '');
            console.log("🔍 PROCESSING TICKET:", ticketId);
            
            const actionsContainer = ticketHeader.querySelector('.ticket-actions');
            
            if (!actionsContainer) {
                console.error("🔍 NO ACTIONS CONTAINER FOUND FOR TICKET:", ticketId);
                return;
            }
            
            // Check if button already exists
            if (actionsContainer.querySelector(`.diagnostic-jira-button[data-ticket-id="${ticketId}"]`)) {
                console.log("🔍 BUTTON ALREADY EXISTS FOR TICKET:", ticketId);
                return;
            }
            
            // First check if this ticket already has test cases sent to Jira
            fetch(`/ticket_jira_status/${ticketId}`)
                .then(response => response.json())
                .then(data => {
                    console.log(`🔍 JIRA STATUS FOR ${ticketId}:`, data);
                    
                    // Create a simple button with inline styling for reliability
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.className = 'jira-button diagnostic-jira-button';
                    button.setAttribute('data-ticket-id', ticketId);
                    
                    const alreadySent = data.success && data.data && data.data.posted_to_jira === true;
                    
                    if (alreadySent) {
                        // Test cases already sent to Jira, show as completed
                        button.innerHTML = 'Sent ✓';
                        button.disabled = true;
                        button.style.cssText = `
                            background-color: #2ecc71;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 6px 12px;
                            margin-left: 10px;
                            font-size: 14px;
                            font-weight: 500;
                            cursor: not-allowed !important;
                            position: relative;
                            z-index: 10000;
                            pointer-events: auto;
                        `;
                        console.log(`🔍 ADDED COMPLETED BUTTON FOR TICKET ${ticketId} (already sent to Jira)`);
                    } else {
                        // Test cases not yet sent to Jira, show normal button
                        button.innerHTML = 'Send to Jira';
                        button.style.cssText = `
                            background-color: #236c54;
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
                        
                        // Add explicit onclick attribute as a fallback
                        button.setAttribute('onclick', `
                            console.log('🔍 INLINE ONCLICK TRIGGERED FOR TICKET: ${ticketId}');
                            event.preventDefault();
                            event.stopPropagation();
                            if(window.sendToJiraAPI) {
                                window.sendToJiraAPI('${ticketId}', this);
                            } else {
                                console.error('sendToJiraAPI function not found');
                                console.error('Error: sendToJiraAPI function not found');
                            }
                            return false;
                        `);
                        console.log(`🔍 ADDED SEND BUTTON FOR TICKET ${ticketId}`);
                    }
                    
                    // Add button after the badge
                    actionsContainer.insertBefore(button, badge.nextSibling);
                })
                .catch(error => {
                    console.error(`🔍 ERROR CHECKING JIRA STATUS FOR ${ticketId}:`, error);
                    
                    // If there was an error, still add the button in its normal state
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.className = 'jira-button diagnostic-jira-button';
                    button.setAttribute('data-ticket-id', ticketId);
                    button.innerHTML = 'Send to Jira';
                    
                    button.style.cssText = `
                        background-color: #236c54;
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
                    
                    button.setAttribute('onclick', `
                        console.log('🔍 INLINE ONCLICK TRIGGERED FOR TICKET: ${ticketId}');
                        event.preventDefault();
                        event.stopPropagation();
                        if(window.sendToJiraAPI) {
                            window.sendToJiraAPI('${ticketId}', this);
                        } else {
                            console.error('sendToJiraAPI function not found');
                            console.error('Error: sendToJiraAPI function not found');
                        }
                        return false;
                    `);
                    
                    actionsContainer.insertBefore(button, badge.nextSibling);
                    console.log(`🔍 ADDED FALLBACK BUTTON FOR TICKET ${ticketId} (after error)`);
                });
        });
    }
    
    // No-op function - disabled
    function addDirectTestButtons() {
        console.log("🔍 DIRECT TEST BUTTONS DISABLED");
    }
    
    // Function to directly call the API
    function sendToJiraAPI(ticketId, buttonElement) {
        console.log("🔍 SEND TO JIRA API CALLED FOR TICKET:", ticketId);
        
        // Show loading state
        if (buttonElement) {
            buttonElement.disabled = true;
            buttonElement.textContent = 'Sending...';
            buttonElement.style.backgroundColor = '#7f8c8d';
            console.log("🔍 UPDATED BUTTON STATE TO LOADING");
        }
        
        console.log("🔍 MAKING FETCH REQUEST TO:", `/send_to_jira/${ticketId}`);
        
        // Make the API call
        fetch(`/send_to_jira/${ticketId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log("🔍 RECEIVED RESPONSE:", response);
            console.log("🔍 RESPONSE STATUS:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("🔍 PARSED RESPONSE DATA:", data);
            
            if (data.success) {
                console.log("🔍 API CALL SUCCESSFUL");
                
                // Update button states
                const allButtons = document.querySelectorAll(`.jira-button[data-ticket-id="${ticketId}"]`);
                console.log("🔍 FOUND BUTTONS TO UPDATE:", allButtons.length);
                
                allButtons.forEach(btn => {
                    btn.textContent = 'Sent ✓';
                    btn.style.backgroundColor = '#2ecc71';
                    btn.disabled = true;
                });
                
                // Log success without showing an alert
                console.log(`Successfully sent test cases to Jira for ticket ${ticketId}`);
            } else {
                console.error("🔍 API CALL FAILED:", data.message);
                
                // Log error without showing an alert
                console.error(`Error sending to Jira: ${data.message}`);
                
                if (buttonElement) {
                    buttonElement.textContent = 'Error';
                    buttonElement.style.backgroundColor = '#e74c3c';
                    buttonElement.disabled = false;
                }
            }
        })
        .catch(error => {
            console.error("🔍 FETCH ERROR:", error);
            console.error(`Error sending to Jira: ${error}`);
            
            if (buttonElement) {
                buttonElement.textContent = 'Error';
                buttonElement.style.backgroundColor = '#e74c3c';
                buttonElement.disabled = false;
            }
        });
    }
    
    // Make the API function globally available
    window.sendToJiraAPI = sendToJiraAPI;
    
    // Run initially with a delay to ensure DOM is loaded
    console.log("🔍 SCHEDULING INITIAL BUTTON ADDITION");
    setTimeout(function() {
        console.log("🔍 RUNNING INITIAL BUTTON ADDITION");
        addDiagnosticButtons();
        // Don't add direct test buttons anymore
    }, 1000);
    
    // Check periodically for new tickets or test cases
    console.log("🔍 SETTING UP INTERVAL FOR BUTTON CHECKS");
    setInterval(function() {
        console.log("🔍 RUNNING PERIODIC BUTTON CHECK");
        addDiagnosticButtons();
        // Don't add direct test buttons anymore
    }, 5000);
    
    console.log("🔍 DIAGNOSTIC SCRIPT SETUP COMPLETE");
});
