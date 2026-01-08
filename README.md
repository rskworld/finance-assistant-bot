# Finance Assistant Bot

> Financial chatbot for account inquiries, transaction history, and financial advice.

## 📋 Project Information

**Category:** Custom Chatbots  
**Difficulty:** Advanced  
**Technologies:** Python, Banking APIs, Security, Database  
**Year:** 2026

## 🎯 Description

This chatbot provides financial services including account inquiries, transaction history, bill payments, and financial advice. Perfect for banks and financial institutions.

## ✨ Features

### Core Features
- **Account Inquiries** - Check your account balance and details instantly
- **Multiple Accounts** - Manage multiple savings, checking, and investment accounts
- **Transaction History** - View your recent transactions and statements with categories
- **Bill Payments** - Manage and pay your bills seamlessly
- **Financial Advice** - Get personalized financial tips and advice
- **Secure Authentication** - Bank-level security for your financial data

### Advanced Features
- **Account Transfers** - Transfer funds between your accounts
- **Budget Tracking** - Set budgets by category and track spending against them
- **Spending Analysis** - Analyze spending patterns by category with visual reports
- **Savings Goals** - Set and track progress toward financial goals
- **Investment Tracking** - Monitor your investment portfolio and performance
- **Financial Reports** - Comprehensive financial summaries and net worth tracking
- **Transaction Categories** - Categorize transactions for better organization
- **Recurring Bills** - Set up and manage recurring bill payments
- **Export Data** - Export transaction history as CSV files
- **24/7 Available** - Access your financial assistant anytime

## 🚀 Installation

1. Clone the repository or extract the project files

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## 🔐 Demo Credentials

**Username:** `demo`  
**Password:** `demo123`

## 📁 Project Structure

```
finance-assistant-bot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── finance_bot.db        # SQLite database (created on first run)
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── app.js        # JavaScript application
└── templates/
    └── index.html        # Main HTML template
```

## 🛠️ Technologies Used

- **Python** - Backend programming language
- **Flask** - Web framework
- **SQLite** - Database for storing user and transaction data
- **HTML/CSS/JavaScript** - Frontend technologies
- **Flask-Session** - Session management
- **Werkzeug** - Password hashing and security

## 💡 Usage

1. **Login/Register**: Create an account or use the demo credentials
2. **Chat Interface**: Start chatting with the finance assistant
3. **Quick Actions**: Use the quick action buttons for common tasks
4. **Account Management**: Check balance, view transactions, pay bills

## 📝 API Endpoints

### Authentication
- `GET /` - Main page
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `POST /api/register` - User registration

### Chat & Account
- `POST /api/chat` - Chat with the bot
- `GET /api/account` - Get user account information
- `GET /api/accounts` - Get all user accounts

### Transactions & Payments
- `GET /api/transactions` - Get transactions with filtering (account, category, days)
- `GET /api/export-transactions` - Export transactions as CSV
- `POST /api/transfer` - Transfer funds between accounts

### Budgets & Analysis
- `GET /api/budgets` - Get all budgets
- `POST /api/budgets` - Create a new budget
- `GET /api/spending-analysis` - Get spending analysis by category

### Goals & Investments
- `GET /api/goals` - Get savings goals
- `POST /api/goals` - Create a savings goal
- `GET /api/investments` - Get investment portfolio
- `POST /api/investments` - Add an investment

### Reports & Analysis
- `GET /api/financial-report` - Get comprehensive financial report
- `GET /api/expense-trends` - Get spending trends over time
- `GET /api/account-statement` - Generate account statement
- `GET /api/search-transactions` - Search transactions by description

### Calculators
- `POST /api/loan-calculator` - Calculate loan payments
- `POST /api/interest-calculator` - Calculate compound interest
- `POST /api/debt-payoff` - Calculate debt payoff strategies
- `GET /api/currency-convert` - Convert between currencies

### Alerts & Calendar
- `GET /api/alerts` - Get user alerts
- `POST /api/alerts` - Create new alert
- `POST /api/alerts/<id>/read` - Mark alert as read
- `GET /api/financial-calendar` - Get financial calendar

### Recurring Transactions
- `GET /api/recurring-transactions` - Get recurring transactions
- `POST /api/recurring-transactions` - Create recurring transaction

## 🔒 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- SQL injection prevention with parameterized queries
- XSS protection in frontend

## 📞 Developer Information

**Founder:** Molla Samser  
**Email:** help@rskworld.in  
**Phone:** +91 93305 39277  
**Address:** Nutanhat, Mongolkote, Purba Burdwan, West Bengal, India, 713147  
**Website:** https://rskworld.in

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Copyright (c) 2026 RSK World (Molla Samser)**

For proprietary licensing options, see [LICENSE_PROPRIETARY.txt](LICENSE_PROPRIETARY.txt) or contact help@rskworld.in

## 🙏 Acknowledgments

Developed by Molla Samser for RSK World.

---

**Note:** This is a demo project for educational purposes. For production use, implement additional security measures and integrate with real banking APIs.
