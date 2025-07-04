// Emergency fix to add Jira buttons - HTML form fallback
window.addEventListener('load', function() {
    console.log("🚨 Emergency Jira button HTML FORM fix loading");
    
    // Function to add HTML form buttons to all tickets
    function addFormButtons() {
        // Find all ticket containers
        const tickets = document.querySelectorAll('.ticket-item');
        console.log(`Found ${tickets.length} tickets to check for HTML form buttons`);
        
        tickets.forEach(function(ticket) {
            const ticketId = ticket.id.replace('ticket-', '');
            const testCasesEl = document.getElementById('test-cases-' + ticketId);
            
            if (testCasesEl) {
                // Check if there are any test cases (no "no-test-cases" elements)
                const noTestCases = testCasesEl.querySelector('.no-test-cases');
                if (!noTestCases) {
                    console.log(`Adding HTML form button for ticket ${ticketId}`);
                    
                    // Only add if we don't already have a form button
                    if (!testCasesEl.querySelector('.html-form-container')) {
                        // Create a standard HTML form that will work without JS
                        const formContainer = document.createElement('div');
                        formContainer.className = 'html-form-container';
                        formContainer.style.cssText = 'text-align: center; margin: 20px 0; padding: 10px; border-top: 2px solid #f1c40f; background-color: #fff9e6;';
                        
                        // Create the form HTML directly
                        formContainer.innerHTML = `
                            <p style="margin-bottom: 10px; font-weight: bold;">If the other buttons don't work, try this one:</p>
                            <form action="/jira_button/${ticketId}" method="get" style="margin: 0; padding: 0;">
                                <button type="submit" class="html-form-button" style="background-color: #f1c40f; color: #000; border: none; border-radius: 4px; padding: 12px 24px; font-size: 16px; font-weight: 600; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                    SEND TO JIRA (HTML FORM)
                                </button>
                            </form>
                        `;
                        
                        // Add to the test cases container
                        testCasesEl.appendChild(formContainer);
                    }
                }
            }
        });
    }
    
    // First attempt after a short delay
    setTimeout(addFormButtons, 2000);
    
    // Then periodically check for new tickets or test cases
    setInterval(addFormButtons, 5000);
});
