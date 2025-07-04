// Emergency fix to add Jira buttons
window.addEventListener('load', function() {
    console.log("🚨 Emergency Jira button fix loading");
    
    // Give the page time to fully render
    setTimeout(function() {
        // Find all ticket containers
        const tickets = document.querySelectorAll('.ticket-item');
        console.log(`Found ${tickets.length} tickets to check for Jira buttons`);
        
        tickets.forEach(function(ticket) {
            const ticketId = ticket.id.replace('ticket-', '');
            const testCasesEl = document.getElementById('test-cases-' + ticketId);
            
            if (testCasesEl) {
                // Check if there are any test cases (no "no-test-cases" elements)
                const noTestCases = testCasesEl.querySelector('.no-test-cases');
                if (!noTestCases) {
                    console.log(`Adding Jira button for ticket ${ticketId}`);
                    
                    // Look for the ticket actions element with the "Test Cases Generated" badge
                    const actionsEl = ticket.querySelector('.ticket-actions');
                    
                    if (actionsEl && actionsEl.querySelector('.test-cases-badge')) {
                        // Check if we already added the button
                        if (actionsEl.querySelector('.emergency-jira-button')) {
                            return;
                        }
                        
                        // Create button for the header
                        const jiraButton = document.createElement('button');
                        jiraButton.className = 'emergency-jira-button';
                        jiraButton.textContent = 'Send to Jira';
                        jiraButton.style.cssText = 'background-color: #0052cc; color: white; border: none; border-radius: 4px; padding: 6px 12px; margin: 0 10px; font-size: 14px; font-weight: 500; cursor: pointer; display: inline-block;';
                        
                        // Add click handler using addEventListener for better event handling
                        jiraButton.addEventListener('click', function(event) {
                            // Prevent ticket from expanding/collapsing
                            event.stopPropagation();
                            console.log(`Emergency Jira button clicked for ticket ${ticketId}`);
                            
                            // Call the main sendToJira function
                            if (typeof sendToJira === 'function') {
                                sendToJira(ticketId);
                            } else {
                                console.error('sendToJira function not found, using fallback');
                                
                                // Show loading state (fallback implementation)
                                jiraButton.disabled = true;
                                jiraButton.textContent = 'Sending...';
                                
                                // Make API request
                                fetch('/send_to_jira/' + ticketId, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    }
                                })
                                .then(response => response.json())
                                .then(data => {
                                    if (data.success) {
                                        jiraButton.textContent = 'Sent ✓';
                                        jiraButton.style.backgroundColor = '#2ecc71';
                                    } else {
                                        jiraButton.textContent = 'Error';
                                        jiraButton.style.backgroundColor = '#e74c3c';
                                        jiraButton.disabled = false;
                                    }
                                })
                                .catch(error => {
                                    console.error('Error sending to Jira:', error);
                                    jiraButton.textContent = 'Error';
                                    jiraButton.style.backgroundColor = '#e74c3c';
                                    jiraButton.disabled = false;
                                });
                            }
                        });
                        
                        // First, remove any existing content to replace it with new content that includes our button
                        const badgeText = actionsEl.querySelector('.test-cases-badge').innerHTML;
                        const expandButton = actionsEl.querySelector('.expand-button');
                        const expandButtonHTML = expandButton ? expandButton.outerHTML : '';
                        
                        // Clear the actions element
                        actionsEl.innerHTML = '';
                        
                        // Rebuild the actions element with our button in between
                        const badge = document.createElement('span');
                        badge.className = 'test-cases-badge';
                        badge.innerHTML = badgeText;
                        actionsEl.appendChild(badge);
                        
                        // Add our button in the middle
                        actionsEl.appendChild(jiraButton);
                        
                        // Add the expand button back if it existed
                        if (expandButtonHTML) {
                            actionsEl.innerHTML += expandButtonHTML;
                        }
                    }
                }
            }
        });
    }, 2000); // 2-second delay to ensure DOM is loaded
    
    // Also add a function to check periodically for new test cases badges
    setInterval(function() {
        // Check all tickets with test cases badges
        const badgeContainers = document.querySelectorAll('.ticket-actions');
        
        badgeContainers.forEach(function(container) {
            // Only add button if there's a badge and no button yet
            if (container.querySelector('.test-cases-badge') && !container.querySelector('.emergency-jira-button')) {
                const ticketItem = container.closest('.ticket-item');
                if (!ticketItem) return;
                
                const ticketId = ticketItem.id.replace('ticket-', '');
                console.log(`Adding missing Jira button for ticket ${ticketId} with test cases badge`);
                
                // Create button for the header
                const jiraButton = document.createElement('button');
                jiraButton.className = 'emergency-jira-button';
                jiraButton.textContent = 'Send to Jira';
                jiraButton.style.cssText = 'background-color: #0052cc; color: white; border: none; border-radius: 4px; padding: 6px 12px; margin: 0 10px; font-size: 14px; font-weight: 500; cursor: pointer; display: inline-block;';
                
                // Add click handler using addEventListener
                jiraButton.addEventListener('click', function(event) {
                    // Prevent ticket from expanding/collapsing
                    event.stopPropagation();
                    console.log(`Emergency Jira button clicked for ticket ${ticketId}`);
                    
                    // Call the main sendToJira function
                    if (typeof sendToJira === 'function') {
                        sendToJira(ticketId);
                    } else {
                        console.error('sendToJira function not found, using fallback');
                        
                        // Show loading state (fallback implementation)
                        jiraButton.disabled = true;
                        jiraButton.textContent = 'Sending...';
                        
                        // Make API request
                        fetch('/send_to_jira/' + ticketId, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                jiraButton.textContent = 'Sent ✓';
                                jiraButton.style.backgroundColor = '#2ecc71';
                            } else {
                                jiraButton.textContent = 'Error';
                                jiraButton.style.backgroundColor = '#e74c3c';
                                jiraButton.disabled = false;
                            }
                        })
                        .catch(error => {
                            console.error('Error sending to Jira:', error);
                            jiraButton.textContent = 'Error';
                            jiraButton.style.backgroundColor = '#e74c3c';
                            jiraButton.disabled = false;
                        });
                    }
                });
                
                // First, remove any existing content to replace it with new content that includes our button
                const badgeText = container.querySelector('.test-cases-badge').innerHTML;
                const expandButton = container.querySelector('.expand-button');
                const expandButtonHTML = expandButton ? expandButton.outerHTML : '';
                
                // Clear the actions element
                container.innerHTML = '';
                
                // Rebuild the actions element with our button in between
                const badge = document.createElement('span');
                badge.className = 'test-cases-badge';
                badge.innerHTML = badgeText;
                container.appendChild(badge);
                
                // Add our button in the middle
                container.appendChild(jiraButton);
                
                // Add the expand button back if it existed
                if (expandButtonHTML) {
                    container.innerHTML += expandButtonHTML;
                }
            }
        });
    }, 2000); // Check every 2 seconds
});
