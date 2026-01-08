"""
Finance Assistant Bot - Main Application
=========================================
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
"""

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import json
import os
import secrets
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Database initialization
def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect('finance_bot.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  full_name TEXT,
                  phone TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Accounts table
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  account_number TEXT UNIQUE NOT NULL,
                  account_type TEXT NOT NULL,
                  balance REAL DEFAULT 0.0,
                  currency TEXT DEFAULT 'USD',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  account_id INTEGER NOT NULL,
                  transaction_type TEXT NOT NULL,
                  amount REAL NOT NULL,
                  description TEXT,
                  category TEXT DEFAULT 'Other',
                  balance_after REAL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (account_id) REFERENCES accounts (id))''')
    
    # Bills table
    c.execute('''CREATE TABLE IF NOT EXISTS bills
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  bill_type TEXT NOT NULL,
                  amount REAL NOT NULL,
                  due_date DATE NOT NULL,
                  status TEXT DEFAULT 'pending',
                  paid_at TIMESTAMP,
                  recurring INTEGER DEFAULT 0,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Budgets table
    c.execute('''CREATE TABLE IF NOT EXISTS budgets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  category TEXT NOT NULL,
                  budget_amount REAL NOT NULL,
                  period TEXT DEFAULT 'monthly',
                  start_date DATE NOT NULL,
                  end_date DATE,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Savings goals table
    c.execute('''CREATE TABLE IF NOT EXISTS savings_goals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  goal_name TEXT NOT NULL,
                  target_amount REAL NOT NULL,
                  current_amount REAL DEFAULT 0.0,
                  target_date DATE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Investment accounts table
    c.execute('''CREATE TABLE IF NOT EXISTS investments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  investment_type TEXT NOT NULL,
                  amount REAL NOT NULL,
                  purchase_date DATE NOT NULL,
                  current_value REAL,
                  description TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Account alerts table
    c.execute('''CREATE TABLE IF NOT EXISTS alerts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  alert_type TEXT NOT NULL,
                  message TEXT NOT NULL,
                  is_read INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Loans table
    c.execute('''CREATE TABLE IF NOT EXISTS loans
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  loan_name TEXT NOT NULL,
                  principal_amount REAL NOT NULL,
                  interest_rate REAL NOT NULL,
                  loan_term_months INTEGER NOT NULL,
                  monthly_payment REAL,
                  remaining_balance REAL,
                  start_date DATE NOT NULL,
                  status TEXT DEFAULT 'active',
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Debts table
    c.execute('''CREATE TABLE IF NOT EXISTS debts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  debt_name TEXT NOT NULL,
                  total_amount REAL NOT NULL,
                  current_balance REAL NOT NULL,
                  interest_rate REAL DEFAULT 0.0,
                  minimum_payment REAL DEFAULT 0.0,
                  due_date INTEGER DEFAULT 1,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Recurring transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS recurring_transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  account_id INTEGER NOT NULL,
                  description TEXT NOT NULL,
                  amount REAL NOT NULL,
                  transaction_type TEXT NOT NULL,
                  category TEXT,
                  frequency TEXT NOT NULL,
                  next_date DATE NOT NULL,
                  end_date DATE,
                  is_active INTEGER DEFAULT 1,
                  FOREIGN KEY (user_id) REFERENCES users (id),
                  FOREIGN KEY (account_id) REFERENCES accounts (id))''')
    
    # Custom categories table
    c.execute('''CREATE TABLE IF NOT EXISTS custom_categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  category_name TEXT NOT NULL,
                  parent_category TEXT,
                  color TEXT,
                  icon TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Transaction tags table
    c.execute('''CREATE TABLE IF NOT EXISTS transaction_tags
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  transaction_id INTEGER NOT NULL,
                  tag_name TEXT NOT NULL,
                  FOREIGN KEY (transaction_id) REFERENCES transactions (id))''')
    
    conn.commit()
    conn.close()
    
    # Create default admin user if not exists
    create_default_user()

def create_default_user():
    """Create default user for demo purposes"""
    conn = sqlite3.connect('finance_bot.db')
    c = conn.cursor()
    
    # Check if admin exists
    c.execute("SELECT id FROM users WHERE username = ?", ('demo',))
    if not c.fetchone():
        hashed_password = generate_password_hash('demo123')
        c.execute("INSERT INTO users (username, email, password, full_name, phone) VALUES (?, ?, ?, ?, ?)",
                  ('demo', 'demo@rskworld.in', hashed_password, 'Demo User', '+91 93305 39277'))
        user_id = c.lastrowid
        
        # Create sample accounts
        c.execute("INSERT INTO accounts (user_id, account_number, account_type, balance, currency) VALUES (?, ?, ?, ?, ?)",
                  (user_id, 'ACC001234567', 'Savings', 5000.00, 'USD'))
        savings_id = c.lastrowid
        
        c.execute("INSERT INTO accounts (user_id, account_number, account_type, balance, currency) VALUES (?, ?, ?, ?, ?)",
                  (user_id, 'ACC001234568', 'Checking', 2000.00, 'USD'))
        checking_id = c.lastrowid
        
        # Create sample transactions with categories
        transactions = [
            (savings_id, 'deposit', 5000.00, 'Initial deposit', 'Income', 5000.00),
            (savings_id, 'withdrawal', 250.00, 'ATM withdrawal', 'Withdrawal', 4750.00),
            (savings_id, 'payment', 150.00, 'Utility bill payment', 'Utilities', 4600.00),
            (savings_id, 'deposit', 1000.00, 'Salary credit', 'Income', 5600.00),
            (checking_id, 'deposit', 2000.00, 'Initial deposit', 'Income', 2000.00),
            (checking_id, 'payment', 50.00, 'Coffee shop', 'Food & Dining', 1950.00),
        ]
        
        for trans in transactions:
            c.execute("INSERT INTO transactions (account_id, transaction_type, amount, description, category, balance_after) VALUES (?, ?, ?, ?, ?, ?)",
                      trans)
        
        # Create sample bills
        bills = [
            (user_id, 'Electricity', 150.00, (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'), 1),
            (user_id, 'Internet', 75.00, (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'), 1),
            (user_id, 'Credit Card', 500.00, (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'), 0),
        ]
        
        for bill in bills:
            c.execute("INSERT INTO bills (user_id, bill_type, amount, due_date, recurring) VALUES (?, ?, ?, ?, ?)", bill)
        
        # Create sample budgets
        budgets = [
            (user_id, 'Food & Dining', 500.00, 'monthly', datetime.now().strftime('%Y-%m-%d')),
            (user_id, 'Utilities', 200.00, 'monthly', datetime.now().strftime('%Y-%m-%d')),
            (user_id, 'Entertainment', 300.00, 'monthly', datetime.now().strftime('%Y-%m-%d')),
        ]
        
        for budget in budgets:
            c.execute("INSERT INTO budgets (user_id, category, budget_amount, period, start_date) VALUES (?, ?, ?, ?, ?)", budget)
        
        # Create sample savings goals
        goals = [
            (user_id, 'Emergency Fund', 10000.00, 2000.00, (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')),
            (user_id, 'Vacation', 3000.00, 500.00, (datetime.now() + timedelta(days=120)).strftime('%Y-%m-%d')),
        ]
        
        for goal in goals:
            c.execute("INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date) VALUES (?, ?, ?, ?, ?)", goal)
        
        # Create sample investments
        investments = [
            (user_id, 'Stocks', 2000.00, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'), 2100.00, 'Tech stocks portfolio'),
            (user_id, 'Bonds', 1000.00, (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'), 1020.00, 'Government bonds'),
        ]
        
        for inv in investments:
            c.execute("INSERT INTO investments (user_id, investment_type, amount, purchase_date, current_value, description) VALUES (?, ?, ?, ?, ?, ?)", inv)
    
    conn.commit()
    conn.close()

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('finance_bot.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'success': True, 'message': 'Login successful', 'user': {
            'id': user['id'],
            'username': user['username'],
            'full_name': user['full_name']
        }})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name', '')
    phone = data.get('phone', '')
    
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    
    # Check if user exists
    existing = conn.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                          (username, email)).fetchone()
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
    
    # Create user
    hashed_password = generate_password_hash(password)
    c = conn.cursor()
    c.execute('INSERT INTO users (username, email, password, full_name, phone) VALUES (?, ?, ?, ?, ?)',
                (username, email, hashed_password, full_name, phone))
    user_id = c.lastrowid
    
    # Create default account
    account_number = f'ACC{secrets.token_hex(6).upper()}'
    conn.execute('INSERT INTO accounts (user_id, account_number, account_type, balance, currency) VALUES (?, ?, ?, ?, ?)',
                (user_id, account_number, 'Savings', 0.0, 'USD'))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Chatbot endpoint"""
    data = request.json
    message = data.get('message', '').lower()
    user_id = session['user_id']
    
    response = process_chat_message(message, user_id)
    return jsonify({'response': response})

def process_chat_message(message, user_id):
    """Process chat message and return appropriate response"""
    conn = get_db_connection()
    
    # Multiple accounts inquiry
    if any(word in message for word in ['all accounts', 'list accounts', 'show accounts']):
        accounts = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
        if accounts:
            response = "Your accounts:\n"
            total = 0
            for acc in accounts:
                response += f"\n{acc['account_number']} ({acc['account_type']}): ${acc['balance']:.2f} {acc['currency']}"
                total += acc['balance']
            response += f"\n\nTotal Balance: ${total:.2f}"
            conn.close()
            return response
        else:
            conn.close()
            return "No accounts found. Please contact support."
    
    # Account inquiry
    elif any(word in message for word in ['balance', 'account balance', 'my balance', 'check balance']):
        accounts = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
        if accounts:
            if len(accounts) == 1:
                acc = accounts[0]
                response = f"Your account balance is ${acc['balance']:.2f} {acc['currency']}. Account: {acc['account_number']}"
            else:
                response = "You have multiple accounts. Here are your balances:\n"
                for acc in accounts:
                    response += f"\n{acc['account_number']} ({acc['account_type']}): ${acc['balance']:.2f}"
            conn.close()
            return response
        else:
            conn.close()
            return "No account found. Please contact support."
    
    # Transaction history
    elif any(word in message for word in ['transaction', 'history', 'statement', 'transactions']):
        account = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchone()
        if account:
            transactions = conn.execute(
                'SELECT * FROM transactions WHERE account_id = ? ORDER BY created_at DESC LIMIT 10',
                (account['id'],)).fetchall()
            
            if transactions:
                response = "Recent transactions:\n"
                for trans in transactions:
                    date = datetime.strptime(trans['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
                    response += f"\n{date}: {trans['transaction_type'].upper()} - ${trans['amount']:.2f} - {trans['description']}"
                return response
            else:
                return "No transactions found."
        else:
            return "No account found."
    
    # Bill payments
    elif any(word in message for word in ['bill', 'bills', 'pay bill', 'due']):
        bills = conn.execute(
            'SELECT * FROM bills WHERE user_id = ? AND status = ? ORDER BY due_date',
            (user_id, 'pending')).fetchall()
        
        if bills:
            response = "Pending bills:\n"
            for bill in bills:
                due_date = datetime.strptime(bill['due_date'], '%Y-%m-%d').strftime('%b %d, %Y')
                response += f"\n{bill['bill_type']}: ${bill['amount']:.2f} - Due: {due_date}"
            return response
        else:
            return "No pending bills found."
    
    # Pay bill
    elif any(word in message for word in ['pay', 'payment', 'make payment']):
        if 'electricity' in message:
            bill_type = 'Electricity'
        elif 'internet' in message:
            bill_type = 'Internet'
        elif 'credit card' in message or 'credit' in message:
            bill_type = 'Credit Card'
        else:
            return "Please specify which bill you want to pay (Electricity, Internet, or Credit Card)."
        
        bill = conn.execute(
            'SELECT * FROM bills WHERE user_id = ? AND bill_type = ? AND status = ?',
            (user_id, bill_type, 'pending')).fetchone()
        
        if bill:
            account = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchone()
            if account['balance'] >= bill['amount']:
                # Update account balance
                new_balance = account['balance'] - bill['amount']
                conn.execute('UPDATE accounts SET balance = ? WHERE id = ?', 
                           (new_balance, account['id']))
                
                # Record transaction
                conn.execute('INSERT INTO transactions (account_id, transaction_type, amount, description, category, balance_after) VALUES (?, ?, ?, ?, ?, ?)',
                           (account['id'], 'payment', bill['amount'], f'{bill_type} bill payment', 'Utilities', new_balance))
                
                # Update bill status
                conn.execute('UPDATE bills SET status = ?, paid_at = ? WHERE id = ?',
                           ('paid', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), bill['id']))
                
                conn.commit()
                conn.close()
                return f"Payment of ${bill['amount']:.2f} for {bill_type} bill completed successfully. New balance: ${new_balance:.2f}"
            else:
                conn.close()
                return f"Insufficient balance. Required: ${bill['amount']:.2f}, Available: ${account['balance']:.2f}"
        else:
            conn.close()
            return f"No pending {bill_type} bill found."
    
    # Financial advice
    elif any(word in message for word in ['advice', 'saving', 'invest', 'financial', 'tips']):
        advice = get_financial_advice(message)
        conn.close()
        return advice
    
    # Transfer funds
    elif any(word in message for word in ['transfer', 'send money', 'move money']):
        # This would typically require more structured input, but for demo:
        conn.close()
        return "To transfer funds, please use the transfer feature in your dashboard or specify: 'Transfer $X from ACCOUNT1 to ACCOUNT2'"
    
    # Budget tracking
    elif any(word in message for word in ['budget', 'budgets', 'my budget', 'budget status']):
        budgets = conn.execute('SELECT * FROM budgets WHERE user_id = ?', (user_id,)).fetchall()
        if budgets:
            response = "Your budgets:\n"
            # Get spending for each budget category
            accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
            account_ids = [acc['id'] for acc in accounts]
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            
            for budget in budgets:
                if account_ids:
                    placeholders = ','.join('?' * len(account_ids))
                    spent = conn.execute(f'''
                        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
                        WHERE account_id IN ({placeholders}) 
                        AND category = ? AND transaction_type IN ('payment', 'withdrawal')
                        AND created_at >= ?
                    ''', account_ids + [budget['category'], month_start]).fetchone()
                    spent_amount = spent['total']
                    remaining = budget['budget_amount'] - spent_amount
                    percentage = (spent_amount / budget['budget_amount'] * 100) if budget['budget_amount'] > 0 else 0
                    status = "✅ Under budget" if remaining >= 0 else "⚠️ Over budget"
                    response += f"\n{budget['category']}: ${spent_amount:.2f} / ${budget['budget_amount']:.2f} ({percentage:.1f}%) - {status}"
                else:
                    response += f"\n{budget['category']}: $0.00 / ${budget['budget_amount']:.2f} - No transactions"
            conn.close()
            return response
        else:
            conn.close()
            return "No budgets set. You can create budgets for different categories like Food, Utilities, Entertainment, etc."
    
    # Savings goals
    elif any(word in message for word in ['goal', 'goals', 'savings goal', 'my goals']):
        goals = conn.execute('SELECT * FROM savings_goals WHERE user_id = ?', (user_id,)).fetchall()
        if goals:
            response = "Your savings goals:\n"
            for goal in goals:
                progress = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
                response += f"\n{goal['goal_name']}: ${goal['current_amount']:.2f} / ${goal['target_amount']:.2f} ({progress:.1f}%)\n"
                if goal['target_date']:
                    target = datetime.strptime(goal['target_date'], '%Y-%m-%d')
                    days_left = (target - datetime.now()).days
                    response += f"  Target date: {target.strftime('%b %d, %Y')} ({days_left} days remaining)\n"
            conn.close()
            return response
        else:
            conn.close()
            return "No savings goals set. I can help you create goals like 'Emergency Fund', 'Vacation', etc."
    
    # Investments
    elif any(word in message for word in ['investment', 'investments', 'portfolio', 'my investments']):
        investments = conn.execute('SELECT * FROM investments WHERE user_id = ?', (user_id,)).fetchall()
        if investments:
            response = "Your investments:\n"
            total_invested = 0
            total_current = 0
            for inv in investments:
                total_invested += inv['amount']
                current_val = inv.get('current_value', inv['amount'])
                total_current += current_val
                gain_loss = current_val - inv['amount']
                gain_percent = ((current_val - inv['amount']) / inv['amount'] * 100) if inv['amount'] > 0 else 0
                sign = "+" if gain_loss >= 0 else ""
                response += f"\n{inv['investment_type']}: ${inv['amount']:.2f} → ${current_val:.2f} ({sign}{gain_percent:.2f}%)"
                if inv['description']:
                    response += f"\n  {inv['description']}"
            
            total_gain = total_current - total_invested
            total_percent = ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0
            sign = "+" if total_gain >= 0 else ""
            response += f"\n\nTotal: ${total_invested:.2f} → ${total_current:.2f} ({sign}{total_percent:.2f}%)"
            conn.close()
            return response
        else:
            conn.close()
            return "No investments found. You can track stocks, bonds, mutual funds, and other investments here."
    
    # Spending analysis
    elif any(word in message for word in ['spending', 'spending analysis', 'expenses', 'where did my money go']):
        accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
        account_ids = [acc['id'] for acc in accounts]
        
        if account_ids:
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            placeholders = ','.join('?' * len(account_ids))
            transactions = conn.execute(f'''
                SELECT category, SUM(amount) as total 
                FROM transactions 
                WHERE account_id IN ({placeholders}) 
                AND transaction_type IN ('payment', 'withdrawal')
                AND created_at >= ?
                GROUP BY category
                ORDER BY total DESC
            ''', account_ids + [month_start]).fetchall()
            
            if transactions:
                response = "Your spending this month by category:\n"
                total = sum(t['total'] for t in transactions)
                for trans in transactions:
                    percentage = (trans['total'] / total * 100) if total > 0 else 0
                    response += f"\n{trans['category']}: ${trans['total']:.2f} ({percentage:.1f}%)"
                response += f"\n\nTotal spent: ${total:.2f}"
                conn.close()
                return response
        
        conn.close()
        return "No spending data found for this month."
    
    # Financial report
    elif any(word in message for word in ['report', 'financial report', 'summary', 'financial summary']):
        accounts = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
        total_balance = sum(acc['balance'] for acc in accounts)
        
        investments = conn.execute('SELECT SUM(current_value) as total FROM investments WHERE user_id = ?', (user_id,)).fetchone()
        total_investments = investments['total'] or 0
        
        month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        account_ids = [acc['id'] for acc in accounts]
        monthly_spending = 0
        if account_ids:
            placeholders = ','.join('?' * len(account_ids))
            spending = conn.execute(f'''
                SELECT SUM(amount) as total FROM transactions 
                WHERE account_id IN ({placeholders}) 
                AND transaction_type IN ('payment', 'withdrawal')
                AND created_at >= ?
            ''', account_ids + [month_start]).fetchone()
            monthly_spending = spending['total'] or 0
        
        goals = conn.execute('SELECT * FROM savings_goals WHERE user_id = ?', (user_id,)).fetchall()
        
        response = "📊 Financial Report\n"
        response += f"\nTotal Balance: ${total_balance:.2f}"
        response += f"\nTotal Investments: ${total_investments:.2f}"
        response += f"\nNet Worth: ${total_balance + total_investments:.2f}"
        response += f"\nMonthly Spending: ${monthly_spending:.2f}"
        response += f"\nActive Accounts: {len(accounts)}"
        response += f"\nSavings Goals: {len(goals)}"
        conn.close()
        return response
    
    # Transaction categories
    elif any(word in message for word in ['category', 'categories', 'spending by category']):
        accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
        account_ids = [acc['id'] for acc in accounts]
        
        if account_ids:
            placeholders = ','.join('?' * len(account_ids))
            categories = conn.execute(f'''
                SELECT DISTINCT category 
                FROM transactions 
                WHERE account_id IN ({placeholders}) 
                AND category IS NOT NULL
            ''', account_ids).fetchall()
            
            if categories:
                response = "Transaction categories:\n"
                for cat in categories:
                    response += f"\n• {cat['category']}"
                conn.close()
                return response
        
        conn.close()
        return "No transaction categories found."
    
    # Account details
    elif any(word in message for word in ['account', 'details', 'info', 'information']):
        accounts = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if accounts and user:
            response = f"Account Details for {user['full_name'] or user['username']}:\n\n"
            for acc in accounts:
                response += f"Account Number: {acc['account_number']}\n"
                response += f"Type: {acc['account_type']}\n"
                response += f"Balance: ${acc['balance']:.2f} {acc['currency']}\n\n"
            return response.strip()
        else:
            return "Account information not available."
    
    # Loan calculator
    elif any(word in message for word in ['loan', 'calculate loan', 'loan payment', 'mortgage']):
        conn.close()
        return "I can calculate loan payments! Please use the format: 'Loan calculator: Principal $X, Rate Y%, Term Z years' or use the calculator feature in your dashboard."
    
    # Interest calculator
    elif any(word in message for word in ['interest', 'compound interest', 'savings calculator', 'investment calculator']):
        conn.close()
        return "I can calculate compound interest! Please use: 'Interest calculator: Principal $X, Rate Y%, Years Z' or use the calculator feature."
    
    # Currency converter
    elif any(word in message for word in ['convert', 'currency', 'exchange rate']):
        conn.close()
        return "I can convert currencies! Try: 'Convert $100 USD to EUR' or use the currency converter feature. Supported currencies: USD, EUR, GBP, JPY, INR, CAD, AUD, CNY."
    
    # Expense trends
    elif any(word in message for word in ['trend', 'trends', 'spending trend', 'expense trend']):
        accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
        account_ids = [acc['id'] for acc in accounts]
        
        if account_ids:
            months = 6
            if 'month' in message:
                # Try to extract number of months
                import re
                months_match = re.search(r'(\d+)\s*month', message)
                if months_match:
                    months = int(months_match.group(1))
            
            placeholders = ','.join('?' * len(account_ids))
            trends_text = f"Expense Trends (Last {months} months):\n"
            
            for i in range(months - 1, -1, -1):
                month_start = (datetime.now() - timedelta(days=30*i)).replace(day=1).strftime('%Y-%m-%d')
                month_end = (datetime.now() - timedelta(days=30*(i-1))).replace(day=1).strftime('%Y-%m-%d') if i > 0 else datetime.now().strftime('%Y-%m-%d')
                
                result = conn.execute(f'''
                    SELECT COALESCE(SUM(amount), 0) as total 
                    FROM transactions 
                    WHERE account_id IN ({placeholders}) 
                    AND transaction_type IN ('payment', 'withdrawal')
                    AND created_at >= ? AND created_at < ?
                ''', account_ids + [month_start, month_end]).fetchone()
                
                month_name = datetime.strptime(month_start[:7], '%Y-%m').strftime('%b %Y')
                trends_text += f"\n{month_name}: ${result['total']:.2f}"
            
            conn.close()
            return trends_text
        
        conn.close()
        return "No expense trends data available."
    
    # Account statement
    elif any(word in message for word in ['statement', 'account statement', 'monthly statement']):
        account = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchone()
        if account:
            # Get last 30 days statement
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            account_id = account['id']
            
            transactions = conn.execute('''
                SELECT * FROM transactions 
                WHERE account_id = ? AND created_at >= ?
                ORDER BY created_at DESC
            ''', (account_id, start_date)).fetchall()
            
            total_deposits = sum(t['amount'] for t in transactions if t['transaction_type'] in ['deposit', 'transfer_in'])
            total_withdrawals = sum(t['amount'] for t in transactions if t['transaction_type'] in ['withdrawal', 'payment', 'transfer_out'])
            
            response = f"Account Statement - Last 30 Days\n"
            response += f"Account: {account['account_number']}\n"
            response += f"Total Deposits: ${total_deposits:.2f}\n"
            response += f"Total Withdrawals: ${total_withdrawals:.2f}\n"
            response += f"Transactions: {len(transactions)}\n"
            response += f"\nFor detailed statement, use the statement feature in dashboard."
            
            conn.close()
            return response
        
        conn.close()
        return "No account found for statement."
    
    # Debt payoff
    elif any(word in message for word in ['debt', 'payoff', 'pay off debt', 'debt calculator']):
        conn.close()
        return "I can help calculate debt payoff strategies! Use the debt payoff calculator feature. It supports both 'snowball' (smallest balance first) and 'avalanche' (highest interest first) strategies."
    
    # Search transactions
    elif any(word in message for word in ['search', 'find transaction', 'look for']):
        if 'transaction' in message or 'payment' in message:
            search_term = message.replace('search', '').replace('transaction', '').replace('for', '').strip()
            if search_term:
                accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
                account_ids = [acc['id'] for acc in accounts]
                
                if account_ids:
                    placeholders = ','.join('?' * len(account_ids))
                    transactions = conn.execute(f'''
                        SELECT t.*, a.account_number 
                        FROM transactions t
                        JOIN accounts a ON t.account_id = a.id
                        WHERE t.account_id IN ({placeholders}) 
                        AND LOWER(t.description) LIKE ?
                        ORDER BY t.created_at DESC
                        LIMIT 10
                    ''', account_ids + [f'%{search_term}%']).fetchall()
                    
                    if transactions:
                        response = f"Found {len(transactions)} transactions matching '{search_term}':\n"
                        for trans in transactions:
                            date = datetime.strptime(trans['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
                            response += f"\n{date}: ${trans['amount']:.2f} - {trans['description']}"
                        conn.close()
                        return response
                    
                    conn.close()
                    return f"No transactions found matching '{search_term}'."
        
        conn.close()
        return "To search transactions, say: 'Search for [description]' or 'Find transaction [keyword]'"
    
    # Financial calendar
    elif any(word in message for word in ['calendar', 'schedule', 'upcoming', 'what\'s due']):
        bills = conn.execute('''
            SELECT * FROM bills 
            WHERE user_id = ? AND status = 'pending' AND due_date >= date('now')
            ORDER BY due_date
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        if bills:
            response = "Upcoming Financial Events:\n"
            for bill in bills:
                due_date = datetime.strptime(bill['due_date'], '%Y-%m-%d').strftime('%b %d, %Y')
                response += f"\n{bill['bill_type']} Bill: ${bill['amount']:.2f} - Due: {due_date}"
            conn.close()
            return response
        else:
            conn.close()
            return "No upcoming bills or financial events found."
    
    # Recurring transactions
    elif any(word in message for word in ['recurring', 'auto', 'automatic', 'scheduled transaction']):
        recurring = conn.execute('''
            SELECT rt.*, a.account_number 
            FROM recurring_transactions rt
            JOIN accounts a ON rt.account_id = a.id
            WHERE rt.user_id = ? AND rt.is_active = 1
            ORDER BY rt.next_date
        ''', (user_id,)).fetchall()
        
        if recurring:
            response = "Recurring Transactions:\n"
            for rec in recurring:
                next_date = datetime.strptime(rec['next_date'], '%Y-%m-%d').strftime('%b %d, %Y')
                response += f"\n{rec['description']}: ${rec['amount']:.2f} ({rec['frequency']}) - Next: {next_date}"
            conn.close()
            return response
        else:
            conn.close()
            return "No recurring transactions set up. You can create them in your dashboard."
    
    # Default response with all features
    else:
        conn.close()
        return """I can help you with:

💰 Account Management:
- Check balance (all accounts or specific)
- View account details
- Transfer funds between accounts
- Account statements

📊 Financial Tracking:
- Transaction history
- Spending analysis by category
- Expense trends over time
- Budget tracking and status
- Financial reports and summaries
- Search transactions

💵 Bills & Payments:
- View pending bills
- Pay bills
- Set up recurring payments
- Financial calendar

🎯 Goals & Investments:
- Savings goals tracking
- Investment portfolio
- Progress reports

🧮 Calculators:
- Loan payment calculator
- Compound interest calculator
- Debt payoff calculator
- Currency converter

📅 Planning:
- Financial calendar
- Recurring transactions
- Account statements

💡 Financial Advice:
- Saving tips
- Investment advice
- Budget recommendations

How can I assist you today?"""

def get_financial_advice(message):
    """Generate financial advice based on message"""
    advice_responses = [
        "Here are some financial tips:\n1. Create an emergency fund (3-6 months expenses)\n2. Pay off high-interest debt first\n3. Invest in diversified portfolios\n4. Review your expenses monthly\n5. Set up automatic savings",
        "For saving money:\n- Track all your expenses\n- Create a budget and stick to it\n- Cut unnecessary subscriptions\n- Cook at home more often\n- Look for discounts and coupons",
        "Investment advice:\n- Start investing early for compound interest\n- Diversify your investments\n- Consider low-cost index funds\n- Don't invest more than you can afford to lose\n- Review your portfolio regularly",
        "Budget management:\n- Use the 50/30/20 rule: 50% needs, 30% wants, 20% savings\n- Use budgeting apps\n- Set financial goals\n- Review and adjust monthly\n- Build an emergency fund first"
    ]
    
    if 'saving' in message or 'save' in message:
        return advice_responses[1]
    elif 'invest' in message:
        return advice_responses[2]
    elif 'budget' in message:
        return advice_responses[3]
    else:
        return advice_responses[0]

@app.route('/api/account', methods=['GET'])
@login_required
def get_account():
    """Get user account information"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    accounts = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if accounts and user:
        return jsonify({
            'accounts': [dict(acc) for acc in accounts],
            'user': dict(user)
        })
    else:
        return jsonify({'error': 'Account not found'}), 404

@app.route('/api/accounts', methods=['GET'])
@login_required
def get_all_accounts():
    """Get all user accounts"""
    user_id = session['user_id']
    conn = get_db_connection()
    accounts = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return jsonify({'accounts': [dict(acc) for acc in accounts]})

@app.route('/api/transfer', methods=['POST'])
@login_required
def transfer_funds():
    """Transfer funds between accounts"""
    data = request.json
    user_id = session['user_id']
    from_account = data.get('from_account')
    to_account = data.get('to_account')
    amount = float(data.get('amount', 0))
    
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400
    
    conn = get_db_connection()
    
    # Get accounts
    from_acc = conn.execute('SELECT * FROM accounts WHERE account_number = ? AND user_id = ?', 
                           (from_account, user_id)).fetchone()
    to_acc = conn.execute('SELECT * FROM accounts WHERE account_number = ? AND user_id = ?', 
                         (to_account, user_id)).fetchone()
    
    if not from_acc or not to_acc:
        conn.close()
        return jsonify({'success': False, 'message': 'Account not found'}), 404
    
    if from_acc['balance'] < amount:
        conn.close()
        return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
    
    # Update balances
    new_from_balance = from_acc['balance'] - amount
    new_to_balance = to_acc['balance'] + amount
    
    conn.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_from_balance, from_acc['id']))
    conn.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_to_balance, to_acc['id']))
    
    # Record transactions
    conn.execute('INSERT INTO transactions (account_id, transaction_type, amount, description, category, balance_after) VALUES (?, ?, ?, ?, ?, ?)',
                (from_acc['id'], 'transfer_out', amount, f'Transfer to {to_account}', 'Transfer', new_from_balance))
    conn.execute('INSERT INTO transactions (account_id, transaction_type, amount, description, category, balance_after) VALUES (?, ?, ?, ?, ?, ?)',
                (to_acc['id'], 'transfer_in', amount, f'Transfer from {from_account}', 'Transfer', new_to_balance))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'Transfer of ${amount:.2f} completed successfully'})

@app.route('/api/budgets', methods=['GET', 'POST'])
@login_required
def manage_budgets():
    """Get or create budgets"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'GET':
        budgets = conn.execute('SELECT * FROM budgets WHERE user_id = ?', (user_id,)).fetchall()
        conn.close()
        return jsonify({'budgets': [dict(b) for b in budgets]})
    
    # POST - Create budget
    data = request.json
    category = data.get('category')
    budget_amount = float(data.get('budget_amount', 0))
    period = data.get('period', 'monthly')
    
    conn.execute('INSERT INTO budgets (user_id, category, budget_amount, period, start_date) VALUES (?, ?, ?, ?, ?)',
                (user_id, category, budget_amount, period, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Budget created successfully'})

@app.route('/api/spending-analysis', methods=['GET'])
@login_required
def spending_analysis():
    """Get spending analysis by category"""
    user_id = session['user_id']
    days = int(request.args.get('days', 30))
    conn = get_db_connection()
    
    accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    account_ids = [acc['id'] for acc in accounts]
    
    if not account_ids:
        conn.close()
        return jsonify({'analysis': {}})
    
    placeholders = ','.join('?' * len(account_ids))
    since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    transactions = conn.execute(f'''
        SELECT category, transaction_type, SUM(amount) as total 
        FROM transactions 
        WHERE account_id IN ({placeholders}) 
        AND created_at >= ? 
        AND transaction_type IN ('payment', 'withdrawal')
        GROUP BY category, transaction_type
    ''', account_ids + [since_date]).fetchall()
    
    analysis = {}
    total_spent = 0
    for trans in transactions:
        if trans['category'] not in analysis:
            analysis[trans['category']] = 0
        analysis[trans['category']] += trans['total']
        total_spent += trans['total']
    
    # Get budgets for comparison
    budgets = conn.execute('SELECT category, budget_amount FROM budgets WHERE user_id = ?', (user_id,)).fetchall()
    budget_dict = {b['category']: b['budget_amount'] for b in budgets}
    
    conn.close()
    return jsonify({
        'analysis': analysis,
        'total_spent': total_spent,
        'budgets': budget_dict,
        'period_days': days
    })

@app.route('/api/goals', methods=['GET', 'POST'])
@login_required
def manage_goals():
    """Get or create savings goals"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'GET':
        goals = conn.execute('SELECT * FROM savings_goals WHERE user_id = ?', (user_id,)).fetchall()
        conn.close()
        return jsonify({'goals': [dict(g) for g in goals]})
    
    # POST - Create goal
    data = request.json
    goal_name = data.get('goal_name')
    target_amount = float(data.get('target_amount', 0))
    target_date = data.get('target_date')
    
    conn.execute('INSERT INTO savings_goals (user_id, goal_name, target_amount, target_date) VALUES (?, ?, ?, ?)',
                (user_id, goal_name, target_amount, target_date))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Goal created successfully'})

@app.route('/api/investments', methods=['GET', 'POST'])
@login_required
def manage_investments():
    """Get or add investments"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'GET':
        investments = conn.execute('SELECT * FROM investments WHERE user_id = ?', (user_id,)).fetchall()
        conn.close()
        return jsonify({'investments': [dict(inv) for inv in investments]})
    
    # POST - Add investment
    data = request.json
    investment_type = data.get('investment_type')
    amount = float(data.get('amount', 0))
    purchase_date = data.get('purchase_date', datetime.now().strftime('%Y-%m-%d'))
    current_value = data.get('current_value', amount)
    description = data.get('description', '')
    
    conn.execute('INSERT INTO investments (user_id, investment_type, amount, purchase_date, current_value, description) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, investment_type, amount, purchase_date, current_value, description))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Investment added successfully'})

@app.route('/api/financial-report', methods=['GET'])
@login_required
def financial_report():
    """Get comprehensive financial report"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get all accounts
    accounts = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    total_balance = sum(acc['balance'] for acc in accounts)
    
    # Get total investments
    investments = conn.execute('SELECT SUM(current_value) as total FROM investments WHERE user_id = ?', (user_id,)).fetchone()
    total_investments = investments['total'] or 0
    
    # Get spending this month
    month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    account_ids = [acc['id'] for acc in accounts]
    placeholders = ','.join('?' * len(account_ids)) if account_ids else '0'
    
    monthly_spending = conn.execute(f'''
        SELECT SUM(amount) as total FROM transactions 
        WHERE account_id IN ({placeholders}) 
        AND transaction_type IN ('payment', 'withdrawal')
        AND created_at >= ?
    ''', account_ids + [month_start] if account_ids else [month_start]).fetchone()
    
    # Get goals progress
    goals = conn.execute('SELECT * FROM savings_goals WHERE user_id = ?', (user_id,)).fetchall()
    
    conn.close()
    return jsonify({
        'total_balance': total_balance,
        'total_investments': total_investments,
        'net_worth': total_balance + total_investments,
        'monthly_spending': monthly_spending['total'] or 0,
        'accounts_count': len(accounts),
        'goals': [dict(g) for g in goals]
    })

@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    """Get transactions with filtering"""
    user_id = session['user_id']
    account_number = request.args.get('account')
    category = request.args.get('category')
    days = int(request.args.get('days', 30))
    
    conn = get_db_connection()
    
    query = '''
        SELECT t.*, a.account_number, a.account_type 
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE a.user_id = ?
    '''
    params = [user_id]
    
    if account_number:
        query += ' AND a.account_number = ?'
        params.append(account_number)
    
    if category:
        query += ' AND t.category = ?'
        params.append(category)
    
    since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    query += ' AND t.created_at >= ? ORDER BY t.created_at DESC'
    params.append(since_date)
    
    transactions = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify({'transactions': [dict(t) for t in transactions]})

@app.route('/api/export-transactions', methods=['GET'])
@login_required
def export_transactions():
    """Export transactions as CSV"""
    from flask import Response
    user_id = session['user_id']
    days = int(request.args.get('days', 30))
    
    conn = get_db_connection()
    accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    account_ids = [acc['id'] for acc in accounts]
    
    if not account_ids:
        conn.close()
        return jsonify({'error': 'No accounts found'}), 404
    
    placeholders = ','.join('?' * len(account_ids))
    since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    transactions = conn.execute(f'''
        SELECT t.*, a.account_number 
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE t.account_id IN ({placeholders}) AND t.created_at >= ?
        ORDER BY t.created_at DESC
    ''', account_ids + [since_date]).fetchall()
    
    conn.close()
    
    # Generate CSV
    csv_data = "Date,Account,Type,Category,Amount,Description,Balance After\n"
    for trans in transactions:
        date = datetime.strptime(trans['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        csv_data += f"{date},{trans['account_number']},{trans['transaction_type']},{trans.get('category', 'N/A')},{trans['amount']},{trans.get('description', '')},{trans.get('balance_after', '')}\n"
    
    return Response(csv_data, mimetype='text/csv', 
                   headers={'Content-Disposition': 'attachment; filename=transactions.csv'})

@app.route('/api/loan-calculator', methods=['POST'])
@login_required
def loan_calculator():
    """Calculate loan payments"""
    data = request.json
    principal = float(data.get('principal', 0))
    annual_rate = float(data.get('annual_rate', 0))
    term_years = int(data.get('term_years', 0))
    
    if principal <= 0 or annual_rate < 0 or term_years <= 0:
        return jsonify({'error': 'Invalid parameters'}), 400
    
    monthly_rate = (annual_rate / 100) / 12
    num_payments = term_years * 12
    
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    total_payment = monthly_payment * num_payments
    total_interest = total_payment - principal
    
    return jsonify({
        'principal': principal,
        'annual_rate': annual_rate,
        'term_years': term_years,
        'monthly_payment': round(monthly_payment, 2),
        'total_payment': round(total_payment, 2),
        'total_interest': round(total_interest, 2),
        'num_payments': num_payments
    })

@app.route('/api/interest-calculator', methods=['POST'])
@login_required
def interest_calculator():
    """Calculate compound interest"""
    data = request.json
    principal = float(data.get('principal', 0))
    annual_rate = float(data.get('annual_rate', 0))
    years = int(data.get('years', 0))
    compounding = data.get('compounding', 'monthly')
    monthly_contribution = float(data.get('monthly_contribution', 0))
    
    if principal <= 0 or annual_rate < 0 or years <= 0:
        return jsonify({'error': 'Invalid parameters'}), 400
    
    compounding_per_year = {
        'daily': 365,
        'monthly': 12,
        'quarterly': 4,
        'annually': 1
    }.get(compounding.lower(), 12)
    
    rate_per_period = (annual_rate / 100) / compounding_per_year
    total_periods = years * compounding_per_year
    
    if monthly_contribution > 0:
        future_value_principal = principal * (1 + rate_per_period) ** total_periods
        contribution_per_period = monthly_contribution / (compounding_per_year / 12) if compounding_per_year >= 12 else monthly_contribution
        future_value_contributions = contribution_per_period * (((1 + rate_per_period) ** total_periods - 1) / rate_per_period) if rate_per_period > 0 else contribution_per_period * total_periods
        future_value = future_value_principal + future_value_contributions
    else:
        future_value = principal * (1 + rate_per_period) ** total_periods
    
    total_interest = future_value - principal - (monthly_contribution * 12 * years)
    total_contributed = principal + (monthly_contribution * 12 * years)
    
    return jsonify({
        'principal': principal,
        'annual_rate': annual_rate,
        'years': years,
        'compounding': compounding,
        'monthly_contribution': monthly_contribution,
        'future_value': round(future_value, 2),
        'total_interest': round(total_interest, 2),
        'total_contributed': round(total_contributed, 2),
        'gain': round(future_value - total_contributed, 2)
    })

@app.route('/api/currency-convert', methods=['GET'])
def currency_convert():
    """Currency converter"""
    amount = float(request.args.get('amount', 1))
    from_currency = request.args.get('from', 'USD').upper()
    to_currency = request.args.get('to', 'EUR').upper()
    
    rates = {
        'USD': 1.0, 'EUR': 0.92, 'GBP': 0.79, 'JPY': 149.0,
        'INR': 83.0, 'CAD': 1.35, 'AUD': 1.52, 'CNY': 7.24
    }
    
    if from_currency not in rates or to_currency not in rates:
        return jsonify({'error': 'Currency not supported'}), 400
    
    converted_amount = amount * (rates[to_currency] / rates[from_currency])
    
    return jsonify({
        'amount': amount,
        'from_currency': from_currency,
        'to_currency': to_currency,
        'converted_amount': round(converted_amount, 2),
        'rate': round(rates[to_currency] / rates[from_currency], 4)
    })

@app.route('/api/expense-trends', methods=['GET'])
@login_required
def expense_trends():
    """Get spending trends over time"""
    user_id = session['user_id']
    months = int(request.args.get('months', 6))
    
    conn = get_db_connection()
    accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    account_ids = [acc['id'] for acc in accounts]
    
    if not account_ids:
        conn.close()
        return jsonify({'trends': []})
    
    placeholders = ','.join('?' * len(account_ids))
    trends = []
    
    for i in range(months - 1, -1, -1):
        month_start = (datetime.now() - timedelta(days=30*i)).replace(day=1).strftime('%Y-%m-%d')
        month_end = (datetime.now() - timedelta(days=30*(i-1))).replace(day=1).strftime('%Y-%m-%d') if i > 0 else datetime.now().strftime('%Y-%m-%d')
        
        result = conn.execute(f'''
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE account_id IN ({placeholders}) 
            AND transaction_type IN ('payment', 'withdrawal')
            AND created_at >= ? AND created_at < ?
        ''', account_ids + [month_start, month_end]).fetchone()
        
        trends.append({
            'month': month_start[:7],
            'total': result['total'],
            'month_name': datetime.strptime(month_start[:7], '%Y-%m').strftime('%B %Y')
        })
    
    conn.close()
    return jsonify({'trends': trends, 'months_analyzed': months})

@app.route('/api/alerts', methods=['GET', 'POST'])
@login_required
def manage_alerts():
    """Get or create alerts"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'GET':
        unread_only = request.args.get('unread_only', 'false') == 'true'
        query = 'SELECT * FROM alerts WHERE user_id = ?'
        params = [user_id]
        
        if unread_only:
            query += ' AND is_read = 0'
        
        query += ' ORDER BY created_at DESC LIMIT 50'
        alerts = conn.execute(query, params).fetchall()
        conn.close()
        return jsonify({'alerts': [dict(a) for a in alerts]})
    
    data = request.json
    alert_type = data.get('alert_type', 'info')
    message = data.get('message', '')
    
    conn.execute('INSERT INTO alerts (user_id, alert_type, message) VALUES (?, ?, ?)',
                (user_id, alert_type, message))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Alert created'})

@app.route('/api/alerts/<int:alert_id>/read', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    """Mark alert as read"""
    user_id = session['user_id']
    conn = get_db_connection()
    conn.execute('UPDATE alerts SET is_read = 1 WHERE id = ? AND user_id = ?', (alert_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/search-transactions', methods=['GET'])
@login_required
def search_transactions():
    """Search transactions by description"""
    user_id = session['user_id']
    query = request.args.get('q', '').lower()
    limit = int(request.args.get('limit', 50))
    
    conn = get_db_connection()
    accounts = conn.execute('SELECT id FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    account_ids = [acc['id'] for acc in accounts]
    
    if not account_ids:
        conn.close()
        return jsonify({'transactions': []})
    
    placeholders = ','.join('?' * len(account_ids))
    transactions = conn.execute(f'''
        SELECT t.*, a.account_number 
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE t.account_id IN ({placeholders}) 
        AND LOWER(t.description) LIKE ?
        ORDER BY t.created_at DESC
        LIMIT ?
    ''', account_ids + [f'%{query}%', limit]).fetchall()
    
    conn.close()
    return jsonify({'transactions': [dict(t) for t in transactions]})

@app.route('/api/account-statement', methods=['GET'])
@login_required
def account_statement():
    """Generate account statement"""
    user_id = session['user_id']
    account_number = request.args.get('account')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    
    if account_number:
        account = conn.execute('SELECT * FROM accounts WHERE account_number = ? AND user_id = ?', 
                             (account_number, user_id)).fetchone()
        if not account:
            conn.close()
            return jsonify({'error': 'Account not found'}), 404
        account_id = account['id']
    else:
        account = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchone()
        if not account:
            conn.close()
            return jsonify({'error': 'No account found'}), 404
        account_id = account['id']
        account_number = account['account_number']
    
    opening_balance = conn.execute('''
        SELECT balance_after FROM transactions 
        WHERE account_id = ? AND created_at < ?
        ORDER BY created_at DESC LIMIT 1
    ''', (account_id, start_date)).fetchone()
    
    opening_balance = opening_balance['balance_after'] if opening_balance else account['balance']
    
    transactions = conn.execute('''
        SELECT * FROM transactions 
        WHERE account_id = ? AND created_at >= ? AND created_at <= ?
        ORDER BY created_at ASC
    ''', (account_id, start_date, end_date + ' 23:59:59')).fetchall()
    
    total_deposits = sum(t['amount'] for t in transactions if t['transaction_type'] in ['deposit', 'transfer_in'])
    total_withdrawals = sum(t['amount'] for t in transactions if t['transaction_type'] in ['withdrawal', 'payment', 'transfer_out'])
    closing_balance = account['balance']
    
    conn.close()
    
    return jsonify({
        'account': dict(account),
        'statement_period': {'start_date': start_date, 'end_date': end_date},
        'opening_balance': opening_balance,
        'closing_balance': closing_balance,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'transactions': [dict(t) for t in transactions],
        'transaction_count': len(transactions)
    })

@app.route('/api/debt-payoff', methods=['POST'])
@login_required
def debt_payoff_calculator():
    """Calculate debt payoff strategies"""
    data = request.json
    debts = data.get('debts', [])
    monthly_payment = float(data.get('monthly_payment', 0))
    strategy = data.get('strategy', 'snowball')
    
    if not debts or monthly_payment <= 0:
        return jsonify({'error': 'Invalid parameters'}), 400
    
    if strategy == 'snowball':
        sorted_debts = sorted(debts, key=lambda x: x['balance'])
    else:
        sorted_debts = sorted(debts, key=lambda x: x.get('interest_rate', 0), reverse=True)
    
    total_months = 0
    total_interest = 0
    payoff_plan = []
    remaining_payment = monthly_payment
    
    for debt in sorted_debts:
        balance = debt['balance']
        min_payment = debt.get('minimum_payment', 0)
        interest_rate = debt.get('interest_rate', 0) / 100 / 12
        
        months = 0
        interest_paid = 0
        
        while balance > 0.01 and months < 600:
            monthly_interest = balance * interest_rate
            interest_paid += monthly_interest
            balance += monthly_interest
            
            payment = min(remaining_payment, balance) if remaining_payment > 0 else min_payment
            balance -= payment
            months += 1
            
            if balance <= 0.01:
                remaining_payment = payment - balance
                balance = 0
        
        payoff_plan.append({
            'debt_name': debt['name'],
            'months': months,
            'total_paid': debt['balance'] + interest_paid,
            'interest_paid': interest_paid
        })
        
        total_months += months
        total_interest += interest_paid
        
        if remaining_payment <= 0:
            break
    
    return jsonify({
        'strategy': strategy,
        'monthly_payment': monthly_payment,
        'total_months': total_months,
        'total_years': round(total_months / 12, 1),
        'total_interest': round(total_interest, 2),
        'payoff_plan': payoff_plan
    })

@app.route('/api/recurring-transactions', methods=['GET', 'POST'])
@login_required
def manage_recurring_transactions():
    """Get or create recurring transactions"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'GET':
        recurring = conn.execute('''
            SELECT rt.*, a.account_number 
            FROM recurring_transactions rt
            JOIN accounts a ON rt.account_id = a.id
            WHERE rt.user_id = ? AND rt.is_active = 1
            ORDER BY rt.next_date
        ''', (user_id,)).fetchall()
        conn.close()
        return jsonify({'recurring_transactions': [dict(r) for r in recurring]})
    
    data = request.json
    account_id = data.get('account_id')
    description = data.get('description')
    amount = float(data.get('amount', 0))
    transaction_type = data.get('transaction_type', 'payment')
    category = data.get('category', 'Other')
    frequency = data.get('frequency', 'monthly')
    next_date = data.get('next_date', datetime.now().strftime('%Y-%m-%d'))
    
    account = conn.execute('SELECT id FROM accounts WHERE id = ? AND user_id = ?', 
                          (account_id, user_id)).fetchone()
    if not account:
        conn.close()
        return jsonify({'error': 'Account not found'}), 404
    
    conn.execute('''
        INSERT INTO recurring_transactions 
        (user_id, account_id, description, amount, transaction_type, category, frequency, next_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, account_id, description, amount, transaction_type, category, frequency, next_date))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Recurring transaction created'})

@app.route('/api/financial-calendar', methods=['GET'])
@login_required
def financial_calendar():
    """Get financial calendar"""
    user_id = session['user_id']
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    conn = get_db_connection()
    month_start = f"{month}-01"
    next_month = (datetime.strptime(month_start, '%Y-%m-%d') + timedelta(days=32)).replace(day=1)
    month_end = (next_month - timedelta(days=1)).strftime('%Y-%m-%d')
    
    bills = conn.execute('''
        SELECT * FROM bills 
        WHERE user_id = ? AND due_date >= ? AND due_date <= ?
        ORDER BY due_date
    ''', (user_id, month_start, month_end)).fetchall()
    
    recurring = conn.execute('''
        SELECT * FROM recurring_transactions 
        WHERE user_id = ? AND is_active = 1 AND next_date >= ? AND next_date <= ?
    ''', (user_id, month_start, month_end)).fetchall()
    
    goals = conn.execute('''
        SELECT * FROM savings_goals 
        WHERE user_id = ? AND target_date >= ? AND target_date <= ?
    ''', (user_id, month_start, month_end)).fetchall()
    
    conn.close()
    
    calendar = []
    for bill in bills:
        calendar.append({
            'date': bill['due_date'],
            'type': 'bill',
            'title': f"{bill['bill_type']} Bill",
            'amount': bill['amount'],
            'status': bill['status']
        })
    
    for rec in recurring:
        calendar.append({
            'date': rec['next_date'],
            'type': 'recurring',
            'title': rec['description'],
            'amount': rec['amount']
        })
    
    for goal in goals:
        calendar.append({
            'date': goal['target_date'],
            'type': 'goal',
            'title': f"{goal['goal_name']} Goal",
            'amount': goal['target_amount']
        })
    
    calendar.sort(key=lambda x: x['date'])
    
    return jsonify({
        'month': month,
        'calendar': calendar,
        'bills_count': len([c for c in calendar if c['type'] == 'bill']),
        'recurring_count': len([c for c in calendar if c['type'] == 'recurring']),
        'goals_count': len([c for c in calendar if c['type'] == 'goal'])
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
