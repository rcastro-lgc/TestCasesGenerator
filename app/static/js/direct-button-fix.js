// Emergency fix to add Jira buttons - Direct version with inline onclick
window.addEventListener('load', function() {
    console.log("🚨 Emergency Jira button fix loading - DIRECT VERSION");
    
    // Function to add direct buttons to all tickets
    function addDirectButtons() {
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
                    console.log(`Adding direct Jira button for ticket ${ticketId}`);
                    
                    // Create standalone button for the test cases container
                    const directContainer = document.createElement('div');
                    directContainer.className = 'direct-jira-container';
                    directContainer.style.cssText = 'text-align: center; margin: 20px 0; padding: 10px; border-top: 1px dashed #ccc;';
                    
                    const directButton = document.createElement('button');
                    directButton.id = `direct-jira-btn-${ticketId}`;
                    directButton.className = 'direct-jira-button';
                    directButton.textContent = 'SEND TO JIRA (DIRECT)';
                    directButton.setAttribute('onclick', `sendToJira('${ticketId}'); return false;`);
                    directButton.style.cssText = 'background-color: #e74c3c; color: white; border: none; border-radius: 4px; padding: 12px 24px; margin: 0 10px; font-size: 16px; font-weight: 600; cursor: pointer !important; display: inline-block; position: relative; z-index: 1000;';
                    
                    directContainer.appendChild(directButton);
                    
                    // Add to the test cases container
                    if (!testCasesEl.querySelector('.direct-jira-container')) {
                        testCasesEl.appendChild(directContainer);
                    }
                    
                    // Also add direct button to the ticket actions
                    const actionsEl = ticket.querySelector('.ticket-actions');
                    if (actionsEl && actionsEl.querySelector('.test-cases-badge')) {
                        // Only add if we don't already have a direct button
                        if (!actionsEl.querySelector('.header-direct-button')) {
                            const headerButton = document.createElement('button');
                            headerButton.className = 'header-direct-button';
                            headerButton.textContent = 'SEND TO JIRA';
                            headerButton.setAttribute('onclick', `sendToJira('${ticketId}'); event.stopPropagation(); return false;`);
                            headerButton.style.cssText = 'background-color: #e74c3c; color: white; border: none; border-radius: 4px; padding: 6px 12px; margin: 0 10px; font-size: 14px; font-weight: 500; cursor: pointer !important; display: inline-block; position: relative; z-index: 1000;';
                            
                            // Add after the badge
                            const badge = actionsEl.querySelector('.test-cases-badge');
                            if (badge && badge.nextSibling) {
                                actionsEl.insertBefore(headerButton, badge.nextSibling);
                            } else {
                                actionsEl.appendChild(headerButton);
                            }
                        }
                    }
                }
            }
        });
    }
    
    // First attempt after a short delay
    setTimeout(addDirectButtons, 1000);
    
    // Then periodically check for new tickets or test cases
    setInterval(addDirectButtons, 3000);
});
