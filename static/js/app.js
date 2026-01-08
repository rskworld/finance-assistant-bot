/*
Finance Assistant Bot - JavaScript Application
==============================================
Project: Finance Assistant Bot
Category: Custom Chatbots
Description: Financial chatbot for account inquiries, transaction history, and financial advice.

Developer Information:
----------------------
Founder: Molla Samser
Email: help@rskworld.in
Phone: +91 93305 39277
Address: Nutanhat, Mongolkote, Purba Burdwan, West Bengal, India, 713147
Website: https://rskworld.in
Year: 2026
*/

// Check if user is logged in on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    // Load dashboard data when logged in
    setTimeout(() => {
        if (document.getElementById('chatContainer').style.display !== 'none') {
            loadDashboardData();
        }
    }, 1000);
});

// Show login modal
function showLogin() {
    document.getElementById('loginModal').style.display = 'block';
}

// Show register modal
function showRegister() {
    document.getElementById('registerModal').style.display = 'block';
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modals when clicking outside
window.onclick = function(event) {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    
    if (event.target == loginModal) {
        loginModal.style.display = 'none';
    }
    if (event.target == registerModal) {
        registerModal.style.display = 'none';
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            closeModal('loginModal');
            showChat();
            updateUserInfo(data.user);
            addBotMessage('Welcome back, ' + (data.user.full_name || data.user.username) + '! How can I assist you today?');
        } else {
            alert(data.message || 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred during login. Please try again.');
    }
}

// Handle register form submission
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const fullName = document.getElementById('regFullName').value;
    const phone = document.getElementById('regPhone').value;
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password, full_name: fullName, phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Registration successful! Please login.');
            closeModal('registerModal');
            showLogin();
        } else {
            alert(data.message || 'Registration failed. Please try again.');
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('An error occurred during registration. Please try again.');
    }
}

// Handle logout
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showWelcome();
            addBotMessage('You have been logged out. Thank you for using Finance Assistant Bot!');
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Check authentication status
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/account');
        
        if (response.ok) {
            const data = await response.json();
            showChat();
            updateUserInfo(data.user);
            addBotMessage('Welcome back, ' + (data.user.full_name || data.user.username) + '! How can I assist you today?');
        } else {
            showWelcome();
        }
    } catch (error) {
        showWelcome();
    }
}

// Update user info display
function updateUserInfo(user) {
    document.getElementById('userName').textContent = user.full_name || user.username;
    document.getElementById('userInfo').style.display = 'flex';
    document.getElementById('authButtons').style.display = 'none';
}

// Show chat interface
function showChat() {
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('chatContainer').style.display = 'flex';
    // Load dashboard data
    loadDashboardData();
    // Check for alerts
    setTimeout(() => checkAlerts(), 1500);
}

// Show welcome screen
function showWelcome() {
    document.getElementById('welcomeScreen').style.display = 'block';
    document.getElementById('chatContainer').style.display = 'none';
    document.getElementById('userInfo').style.display = 'none';
    document.getElementById('authButtons').style.display = 'flex';
    document.getElementById('chatMessages').innerHTML = `
        <div class="message bot-message">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>Hello! I'm your Finance Assistant. How can I help you today?</p>
                <span class="message-time">${getCurrentTime()}</span>
            </div>
        </div>
    `;
}

// Send message
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addUserMessage(message);
    input.value = '';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });
        
        if (response.ok) {
            const data = await response.json();
            setTimeout(() => {
                addBotMessage(data.response);
            }, 500);
        } else if (response.status === 401) {
            addBotMessage('Please login to use the chat feature.');
            showWelcome();
        } else {
            addBotMessage('Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        console.error('Chat error:', error);
        addBotMessage('Sorry, I encountered an error. Please try again.');
    }
}

// Send quick message
function sendQuickMessage(message) {
    document.getElementById('chatInput').value = message;
    sendMessage();
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Add user message to chat
function addUserMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-user"></i>
        </div>
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
            <span class="message-time">${getCurrentTime()}</span>
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <p>${escapeHtml(message).replace(/\n/g, '<br>')}</p>
            <span class="message-time">${getCurrentTime()}</span>
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    // Auto-detect and create action buttons for certain responses
    if (message.includes('accounts') || message.includes('balance')) {
        addActionButtons(['View All Accounts', 'Financial Report']);
    }
    if (message.includes('budget') || message.includes('Budget')) {
        addActionButtons(['View Budgets', 'Spending Analysis']);
    }
    if (message.includes('goal') || message.includes('Goal')) {
        addActionButtons(['View Goals', 'Financial Report']);
    }
    if (message.includes('investment') || message.includes('Investment')) {
        addActionButtons(['View Portfolio', 'Financial Report']);
    }
}

// Add action buttons to chat
function addActionButtons(buttons) {
    const messagesContainer = document.getElementById('chatMessages');
    const lastMessage = messagesContainer.lastElementChild;
    if (lastMessage && lastMessage.classList.contains('bot-message')) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'action-buttons';
        buttonContainer.style.marginTop = '10px';
        buttonContainer.style.display = 'flex';
        buttonContainer.style.gap = '10px';
        buttonContainer.style.flexWrap = 'wrap';
        
        buttons.forEach(buttonText => {
            const button = document.createElement('button');
            button.className = 'quick-btn';
            button.textContent = buttonText;
            button.onclick = () => {
                const command = getCommandFromButton(buttonText);
                if (command) {
                    document.getElementById('chatInput').value = command;
                    sendMessage();
                }
            };
            buttonContainer.appendChild(button);
        });
        
        lastMessage.querySelector('.message-content').appendChild(buttonContainer);
    }
}

// Get chat command from button text
function getCommandFromButton(buttonText) {
    const commands = {
        'View All Accounts': 'Show all accounts',
        'Financial Report': 'Financial report',
        'View Budgets': 'Budget status',
        'Spending Analysis': 'Spending analysis',
        'View Goals': 'My goals',
        'View Portfolio': 'My investments',
        'Account Statement': 'Account statement',
        'Expense Trends': 'Expense trends',
        'Loan Calculator': 'Loan calculator',
        'Financial Calendar': 'Financial calendar',
        'Transaction History': 'Transaction history',
        'Show Bills': 'Show my bills'
    };
    return commands[buttonText] || '';
}

// Load financial dashboard data
async function loadDashboardData() {
    try {
        const [accountsRes, budgetsRes, goalsRes, investmentsRes, analysisRes] = await Promise.all([
            fetch('/api/accounts'),
            fetch('/api/budgets'),
            fetch('/api/goals'),
            fetch('/api/investments'),
            fetch('/api/spending-analysis?days=30')
        ]);
        
        if (accountsRes.ok) {
            const data = await accountsRes.json();
            updateAccountsDisplay(data.accounts);
        }
        
        if (budgetsRes.ok) {
            const data = await budgetsRes.json();
            updateBudgetsDisplay(data.budgets);
        }
        
        if (goalsRes.ok) {
            const data = await goalsRes.json();
            updateGoalsDisplay(data.goals);
        }
        
        if (investmentsRes.ok) {
            const data = await investmentsRes.json();
            updateInvestmentsDisplay(data.investments);
        }
        
        if (analysisRes.ok) {
            const data = await analysisRes.json();
            updateSpendingChart(data);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Update accounts display (helper function for future dashboard)
function updateAccountsDisplay(accounts) {
    // This can be used to update a dashboard widget
    console.log('Accounts updated:', accounts);
}

// Update budgets display
function updateBudgetsDisplay(budgets) {
    console.log('Budgets updated:', budgets);
}

// Update goals display
function updateGoalsDisplay(goals) {
    console.log('Goals updated:', goals);
}

// Update investments display
function updateInvestmentsDisplay(investments) {
    console.log('Investments updated:', investments);
}

// Update spending chart
function updateSpendingChart(analysis) {
    console.log('Spending analysis:', analysis);
}

// Calculate loan payment
async function calculateLoan(principal, annualRate, termYears) {
    try {
        const response = await fetch('/api/loan-calculator', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({principal, annual_rate: annualRate, term_years: termYears})
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Loan calculator error:', error);
        return null;
    }
}

// Calculate compound interest
async function calculateInterest(principal, annualRate, years, compounding, monthlyContribution = 0) {
    try {
        const response = await fetch('/api/interest-calculator', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                principal,
                annual_rate: annualRate,
                years,
                compounding,
                monthly_contribution: monthlyContribution
            })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Interest calculator error:', error);
        return null;
    }
}

// Convert currency
async function convertCurrency(amount, fromCurrency, toCurrency) {
    try {
        const response = await fetch(`/api/currency-convert?amount=${amount}&from=${fromCurrency}&to=${toCurrency}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Currency conversion error:', error);
        return null;
    }
}

// Get expense trends
async function getExpenseTrends(months = 6) {
    try {
        const response = await fetch(`/api/expense-trends?months=${months}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Expense trends error:', error);
        return null;
    }
}

// Get alerts
async function getAlerts(unreadOnly = false) {
    try {
        const response = await fetch(`/api/alerts?unread_only=${unreadOnly}`);
        const data = await response.json();
        return data.alerts || [];
    } catch (error) {
        console.error('Get alerts error:', error);
        return [];
    }
}

// Search transactions
async function searchTransactions(query, limit = 50) {
    try {
        const response = await fetch(`/api/search-transactions?q=${encodeURIComponent(query)}&limit=${limit}`);
        const data = await response.json();
        return data.transactions || [];
    } catch (error) {
        console.error('Search transactions error:', error);
        return [];
    }
}

// Get account statement
async function getAccountStatement(accountNumber, startDate, endDate) {
    try {
        let url = '/api/account-statement?';
        if (accountNumber) url += `account=${accountNumber}&`;
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}`;
        
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Account statement error:', error);
        return null;
    }
}

// Calculate debt payoff
async function calculateDebtPayoff(debts, monthlyPayment, strategy = 'snowball') {
    try {
        const response = await fetch('/api/debt-payoff', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({debts, monthly_payment: monthlyPayment, strategy})
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Debt payoff calculator error:', error);
        return null;
    }
}

// Get financial calendar
async function getFinancialCalendar(month) {
    try {
        const response = await fetch(`/api/financial-calendar?month=${month}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Financial calendar error:', error);
        return null;
    }
}

// Get recurring transactions
async function getRecurringTransactions() {
    try {
        const response = await fetch('/api/recurring-transactions');
        const data = await response.json();
        return data.recurring_transactions || [];
    } catch (error) {
        console.error('Get recurring transactions error:', error);
        return [];
    }
}

// Check for alerts on login
async function checkAlerts() {
    const alerts = await getAlerts(true);
    if (alerts.length > 0) {
        const unreadCount = alerts.filter(a => !a.is_read).length;
        if (unreadCount > 0) {
            addBotMessage(`You have ${unreadCount} new alert(s). Type "Show alerts" to view them.`);
        }
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Get current time
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
