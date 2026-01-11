from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
import logging
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Secure #1: Token Configuration
serializer = URLSafeTimedSerializer(app.secret_key)

# Secure #3: Logging Configuration
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Dummy user database
users = {
    'admin': 'password123',
    'user1': 'pass456'
}

# Dummy data
sensitive_data = [
    {'id': 1, 'title': 'Data Rahasia 1', 'content': 'Informasi penting tentang proyek A'},
    {'id': 2, 'title': 'Data Rahasia 2', 'content': 'Informasi penting tentang proyek B'},
    {'id': 3, 'title': 'Data Rahasia 3', 'content': 'Informasi penting tentang proyek C'}
]

# CCTV data untuk dashboard
cctv_locations = [
    {'id': 1, 'name': 'Bundaran Waru', 'status': 'Online', 'location': 'Jl. Raya Waru'},
    {'id': 2, 'name': 'Terminal Larangan', 'status': 'Online', 'location': 'Jl. Raya Larangan'},
    {'id': 3, 'name': 'Alun-alun Sidoarjo', 'status': 'Online', 'location': 'Jl. Gajah Mada'},
    {'id': 4, 'name': 'Pasar Porong', 'status': 'Offline', 'location': 'Jl. Raya Porong'},
    {'id': 5, 'name': 'Delta Plaza', 'status': 'Online', 'location': 'Jl. Raya Candi'},
    {'id': 6, 'name': 'Stadion Gelora Delta', 'status': 'Online', 'location': 'Jl. Pahlawan'}
]

# Secure #2: Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            app.logger.warning(f'Unauthorized access attempt to {request.path} - IP: {request.remote_addr}')
            flash('Anda harus login terlebih dahulu!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Required Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            app.logger.warning(f'Unauthorized access attempt to {request.path} - IP: {request.remote_addr}')
            flash('Anda harus login sebagai admin!', 'danger')
            return redirect(url_for('login'))
        if session['username'] != 'admin':
            app.logger.warning(f'Non-admin access attempt to {request.path} - User: {session["username"]}')
            flash('Akses ditolak! Hanya admin yang bisa mengakses halaman ini.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Secure #1: Generate safe token for URL
def generate_token(data):
    return serializer.dumps(data, salt='url-safe-token')

# Secure #1: Verify token from URL
def verify_token(token, max_age=3600):
    try:
        data = serializer.loads(token, salt='url-safe-token', max_age=max_age)
        return data
    except:
        return None

# Function to read log file
def read_log_file(lines=50):
    try:
        if os.path.exists('app.log'):
            with open('app.log', 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]  # Return last N lines
        return []
    except Exception as e:
        app.logger.error(f'Error reading log file: {str(e)}')
        return []

# Dashboard/Home Template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - CCTV Sidoarjo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar-brand {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
        }
        .navbar-brand span {
            color: #764ba2;
        }
        .navbar-menu {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .nav-link {
            padding: 8px 16px;
            text-decoration: none;
            color: #333;
            border-radius: 6px;
            transition: all 0.3s;
            font-weight: 500;
        }
        .nav-link:hover {
            background: #667eea;
            color: white;
        }
        .nav-link.active {
            background: #667eea;
            color: white;
        }
        .user-info-nav {
            padding: 8px 16px;
            background: #f0f0f0;
            border-radius: 6px;
            margin-left: 10px;
        }
        
        .main-container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .content-box {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .alert {
            padding: 12px 20px;
            margin: 15px 0;
            border-radius: 8px;
            font-weight: 500;
        }
        .alert-success { background: #d4edda; color: #155724; border-left: 4px solid #28a745; }
        .alert-danger { background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
        .alert-info { background: #d1ecf1; color: #0c5460; border-left: 4px solid #17a2b8; }
        
        .dashboard-header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }
        .dashboard-header h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .dashboard-header p {
            color: #666;
            font-size: 16px;
        }
        
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-card h3 {
            font-size: 36px;
            margin-bottom: 5px;
        }
        .stat-card p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .cctv-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .cctv-card {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            transition: all 0.3s;
        }
        .cctv-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .cctv-preview {
            width: 100%;
            height: 180px;
            background: linear-gradient(45deg, #2c3e50, #34495e);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 48px;
        }
        .cctv-info {
            padding: 15px;
        }
        .cctv-info h3 {
            color: #333;
            margin-bottom: 8px;
        }
        .cctv-info p {
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-top: 8px;
        }
        .status-online {
            background: #d4edda;
            color: #155724;
        }
        .status-offline {
            background: #f8d7da;
            color: #721c24;
        }
        
        .security-info {
            background: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin-top: 30px;
        }
        .security-info h3 {
            color: #856404;
            margin-bottom: 10px;
        }
        .security-info ul {
            margin-left: 20px;
        }
        .security-info li {
            margin: 5px 0;
            color: #856404;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="{{ url_for('index') }}" class="navbar-brand">
                🎥 CCTV<span>Sidoarjo</span>
            </a>
            <div class="navbar-menu">
                <a href="{{ url_for('index') }}" class="nav-link active">Dashboard</a>
                
                {% if session.get('username') == 'admin' %}
                    <a href="{{ url_for('view_data') }}" class="nav-link">Data Rahasia</a>
                    <a href="{{ url_for('view_logs') }}" class="nav-link">Log Data</a>
                {% endif %}
                
                {% if session.get('username') %}
                    <span class="user-info-nav">👤 {{ session['username'] }}</span>
                    <a href="{{ url_for('logout') }}" class="nav-link">Sign Out</a>
                {% else %}
                    <a href="{{ url_for('login') }}" class="nav-link">Sign In</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="main-container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="content-box">
            <div class="dashboard-header">
                <h1>🎥 Pantauan CCTV Wilayah Sidoarjo</h1>
                <p>Sistem Monitoring Keamanan Kota Sidoarjo</p>
            </div>

            <div class="stats-container">
                <div class="stat-card">
                    <h3>{{ total_cctv }}</h3>
                    <p>Total CCTV</p>
                </div>
                <div class="stat-card">
                    <h3>{{ online_cctv }}</h3>
                    <p>Online</p>
                </div>
                <div class="stat-card">
                    <h3>{{ offline_cctv }}</h3>
                    <p>Offline</p>
                </div>
            </div>

            <h2 style="margin-bottom: 15px;">📍 Lokasi CCTV</h2>

            <div class="cctv-grid">
                {% for cctv in cctv_list %}
                <div class="cctv-card">
                    <div class="cctv-preview">
                        {% if cctv.status == 'Online' %}
                            📹
                        {% else %}
                            ⚠️
                        {% endif %}
                    </div>
                    <div class="cctv-info">
                        <h3>{{ cctv.name }}</h3>
                        <p>📍 {{ cctv.location }}</p>
                        <span class="status-badge status-{{ cctv.status.lower() }}">
                            {{ cctv.status }}
                        </span>
                    </div>
                </div>
                {% endfor %}
            </div>

            <div class="security-info">
                <h3>🔒 Implementasi Keamanan Sistem</h3>
                <ul>
                    <li><strong>Secure #1:</strong> Token URL terenkripsi untuk akses data detail</li>
                    <li><strong>Secure #2:</strong> Session management - Login required untuk data sensitif</li>
                    <li><strong>Secure #3:</strong> Logging semua aktivitas sistem</li>
                </ul>
                {% if not session.get('username') %}
                <p style="margin-top: 15px; font-style: italic;">
                    💡 <strong>Catatan:</strong> Silakan login sebagai <strong>admin</strong> untuk mengakses data rahasia dan log sistem.
                </p>
                {% elif session.get('username') != 'admin' %}
                <p style="margin-top: 15px; font-style: italic;">
                    ⚠️ <strong>Info:</strong> Anda login sebagai <strong>{{ session['username'] }}</strong>. Hanya <strong>admin</strong> yang dapat mengakses data rahasia dan log sistem.
                </p>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
'''

# Login Template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sign In - CCTV Sidoarjo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar-brand {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
        }
        .navbar-brand span {
            color: #764ba2;
        }
        .navbar-menu {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .nav-link {
            padding: 8px 16px;
            text-decoration: none;
            color: #333;
            border-radius: 6px;
            transition: all 0.3s;
            font-weight: 500;
        }
        .nav-link:hover {
            background: #667eea;
            color: white;
        }
        .nav-link.active {
            background: #667eea;
            color: white;
        }
        
        .main-container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .alert {
            padding: 12px 20px;
            margin: 15px 0;
            border-radius: 8px;
            font-weight: 500;
        }
        .alert-danger { background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
        
        .login-box {
            max-width: 400px;
            margin: 50px auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h2 {
            color: #333;
            font-size: 28px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #333;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn-login {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        .test-accounts {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            font-size: 13px;
        }
        .test-accounts strong {
            display: block;
            margin-bottom: 8px;
            color: #333;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="{{ url_for('index') }}" class="navbar-brand">
                🎥 CCTV<span>Sidoarjo</span>
            </a>
            <div class="navbar-menu">
                <a href="{{ url_for('index') }}" class="nav-link">Dashboard</a>
                <a href="{{ url_for('login') }}" class="nav-link active">Sign In</a>
            </div>
        </div>
    </nav>
    
    <div class="main-container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="login-box">
            <div class="login-header">
                <h2>🔐 Sign In</h2>
                <p>Masuk ke Sistem CCTV Sidoarjo</p>
            </div>
            
            <form method="POST">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" name="username" required autofocus>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn-login">Sign In</button>
            </form>
            
            <div class="test-accounts">
                <strong>🧪 Test Accounts:</strong>
                Username: <code>admin</code> | Password: <code>password123</code><br>
                Username: <code>user1</code> | Password: <code>pass456</code>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Data Template
DATA_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Data Rahasia - CCTV Sidoarjo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar-brand {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
        }
        .navbar-brand span {
            color: #764ba2;
        }
        .navbar-menu {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .nav-link {
            padding: 8px 16px;
            text-decoration: none;
            color: #333;
            border-radius: 6px;
            transition: all 0.3s;
            font-weight: 500;
        }
        .nav-link:hover {
            background: #667eea;
            color: white;
        }
        .nav-link.active {
            background: #667eea;
            color: white;
        }
        .user-info-nav {
            padding: 8px 16px;
            background: #f0f0f0;
            border-radius: 6px;
            margin-left: 10px;
        }
        
        .main-container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .content-box {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .page-header {
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }
        .page-header h2 {
            color: #333;
            font-size: 28px;
        }
        .data-item {
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
        }
        .data-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .data-item h3 {
            margin: 0 0 10px 0;
            color: #667eea;
        }
        .data-item p {
            color: #666;
            margin-bottom: 15px;
        }
        .btn {
            padding: 10px 20px;
            margin: 5px;
            text-decoration: none;
            border-radius: 6px;
            display: inline-block;
            font-weight: 500;
            transition: all 0.3s;
        }
        .btn-success { 
            background: #28a745; 
            color: white; 
        }
        .btn-success:hover { 
            background: #218838; 
        }
        .info-box {
            background: #d1ecf1;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid #17a2b8;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="{{ url_for('index') }}" class="navbar-brand">
                🎥 CCTV<span>Sidoarjo</span>
            </a>
            <div class="navbar-menu">
                <a href="{{ url_for('index') }}" class="nav-link">Dashboard</a>
                
                {% if session.get('username') == 'admin' %}
                    <a href="{{ url_for('view_data') }}" class="nav-link active">Data Rahasia</a>
                    <a href="{{ url_for('view_logs') }}" class="nav-link">Log Data</a>
                {% endif %}
                
                {% if session.get('username') %}
                    <span class="user-info-nav">👤 {{ session['username'] }}</span>
                    <a href="{{ url_for('logout') }}" class="nav-link">Sign Out</a>
                {% else %}
                    <a href="{{ url_for('login') }}" class="nav-link">Sign In</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="main-container">
        <div class="content-box">
            <div class="page-header">
                <h2>📊 Data Rahasia</h2>
                <p>Halo, <strong>{{ session['username'] }}</strong>! Berikut adalah data rahasia sistem:</p>
            </div>

            <div class="info-box">
                💡 <strong>Secure #1 (Token URL):</strong> Klik "Lihat Detail" untuk melihat URL dengan token terenkripsi!
            </div>

            {% for data in data_list %}
            <div class="data-item">
                <h3>{{ data.title }}</h3>
                <p>{{ data.content }}</p>
                <a href="{{ url_for('view_detail', token=generate_token(data.id)) }}" class="btn btn-success">Lihat Detail</a>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

# Detail Template
DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Detail Data - CCTV Sidoarjo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar-brand {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
        }
        .navbar-brand span {
            color: #764ba2;
        }
        .navbar-menu {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .nav-link {
            padding: 8px 16px;
            text-decoration: none;
            color: #333;
            border-radius: 6px;
            transition: all 0.3s;
            font-weight: 500;
        }
        .nav-link:hover {
            background: #667eea;
            color: white;
        }
        .nav-link.active {
            background: #667eea;
            color: white;
        }
        .user-info-nav {
            padding: 8px 16px;
            background: #f0f0f0;
            border-radius: 6px;
            margin-left: 10px;
        }
        
        .main-container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .content-box {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .page-header {
            margin-bottom: 25px;
        }
        .success-box {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #28a745;
            margin-bottom: 20px;
        }
        .token-box {
            background: #fff3cd;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            word-break: break-all;
        }
        .data-detail {
            background: #e7f3ff;
            padding: 25px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .data-detail h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        .data-detail p {
            margin: 10px 0;
            color: #333;
        }
        .btn {
            padding: 10px 20px;
            margin: 5px;
            text-decoration: none;
            border-radius: 6px;
            display: inline-block;
            font-weight: 500;
            transition: all 0.3s;
        }
        .btn-primary { 
            background: #667eea; 
            color: white; 
        }
        .btn-primary:hover { 
            background: #5568d3; 
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="{{ url_for('index') }}" class="navbar-brand">
                🎥 CCTV<span>Sidoarjo</span>
            </a>
            <div class="navbar-menu">
                <a href="{{ url_for('index') }}" class="nav-link">Dashboard</a>
                
                {% if session.get('username') == 'admin' %}
                    <a href="{{ url_for('view_data') }}" class="nav-link active">Data Rahasia</a>
                    <a href="{{ url_for('view_logs') }}" class="nav-link">Log Data</a>
                {% endif %}
                
                {% if session.get('username') %}
                    <span class="user-info-nav">👤 {{ session['username'] }}</span>
                    <a href="{{ url_for('logout') }}" class="nav-link">Sign Out</a>
                {% else %}
                    <a href="{{ url_for('login') }}" class="nav-link">Sign In</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="main-container">
        <div class="content-box">
            <div class="page-header">
                <h2>🔍 Detail Data</h2>
            </div>

            <div class="success-box">
                ✅ <strong>Secure #1 berhasil!</strong> URL ini menggunakan token terenkripsi, bukan ID langsung.
            </div>

            <div class="token-box">
                <strong>Token di URL:</strong><br>
                <small style="color: #856404;">{{ token }}</small>
            </div>

            <div class="data-detail">
                <h3>{{ data.title }}</h3>
                <p><strong>ID:</strong> {{ data.id }}</p>
                <p><strong>Konten:</strong> {{ data.content }}</p>
            </div>

            <div style="margin-top: 20px;">
                <a href="{{ url_for('view_data') }}" class="btn btn-primary">← Kembali ke Daftar Data</a>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Log Viewer Template
LOG_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Log Data - CCTV Sidoarjo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar-brand {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
        }
        .navbar-brand span {
            color: #764ba2;
        }
        .navbar-menu {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .nav-link {
            padding: 8px 16px;
            text-decoration: none;
            color: #333;
            border-radius: 6px;
            transition: all 0.3s;
            font-weight: 500;
        }
        .nav-link:hover {
            background: #667eea;
            color: white;
        }
        .nav-link.active {
            background: #667eea;
            color: white;
        }
        .user-info-nav {
            padding: 8px 16px;
            background: #f0f0f0;
            border-radius: 6px;
            margin-left: 10px;
        }
        
        .main-container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .content-box {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .page-header {
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }
        .page-header h2 {
            color: #333;
            font-size: 28px;
        }
        .log-info {
            background: #d1ecf1;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid #17a2b8;
        }
        .log-container {
            background: #2c3e50;
            color: #00ff00;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            max-height: 600px;
            overflow-y: auto;
            line-height: 1.6;
        }
        .log-container::-webkit-scrollbar {
            width: 8px;
        }
        .log-container::-webkit-scrollbar-track {
            background: #34495e;
        }
        .log-container::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }
        .log-line {
            margin: 5px 0;
            padding: 5px;
            border-radius: 3px;
        }
        .log-line:hover {
            background: rgba(255,255,255,0.1);
        }
        .log-level-INFO { color: #00ff00; }
        .log-level-WARNING { color: #ffaa00; }
        .log-level-ERROR { color: #ff5555; }
        .empty-log {
            text-align: center;
            color: #888;
            padding: 40px;
        }
        .btn {
            padding: 10px 20px;
            margin: 5px;
            text-decoration: none;
            border-radius: 6px;
            display: inline-block;
            font-weight: 500;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        .btn-primary { 
            background: #667eea; 
            color: white; 
        }
        .btn-primary:hover { 
            background: #5568d3; 
        }
        .refresh-btn {
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="{{ url_for('index') }}" class="navbar-brand">
                🎥 CCTV<span>Sidoarjo</span>
            </a>
            <div class="navbar-menu">
                <a href="{{ url_for('index') }}" class="nav-link">Dashboard</a>
                
                {% if session.get('username') == 'admin' %}
                    <a href="{{ url_for('view_data') }}" class="nav-link">Data Rahasia</a>
                    <a href="{{ url_for('view_logs') }}" class="nav-link active">Log Data</a>
                {% endif %}
                
                {% if session.get('username') %}
                    <span class="user-info-nav">👤 {{ session['username'] }}</span>
                    <a href="{{ url_for('logout') }}" class="nav-link">Sign Out</a>
                {% else %}
                    <a href="{{ url_for('login') }}" class="nav-link">Sign In</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="main-container">
        <div class="content-box">
            <div class="page-header">
                <h2>📋 Log Data Sistem</h2>
                <p>Menampilkan 50 log aktivitas terakhir</p>
            </div>

            <div class="log-info">
                ℹ️ <strong>Secure #3 - Logging:</strong> Semua aktivitas sistem dicatat secara otomatis untuk keamanan dan audit.
            </div>

            <a href="{{ url_for('view_logs') }}" class="btn btn-primary refresh-btn">🔄 Refresh Log</a>

            <div class="log-container">
                {% if logs %}
                    {% for log in logs %}
                    <div class="log-line {% if 'WARNING' in log %}log-level-WARNING{% elif 'ERROR' in log %}log-level-ERROR{% else %}log-level-INFO{% endif %}">
                        {{ log|trim }}
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-log">
                        📄 Belum ada log aktivitas.<br>
                        Silakan melakukan beberapa aktivitas terlebih dahulu.
                    </div>
                {% endif %}
            </div>

            <div style="margin-top: 20px;">
                <p style="color: #666; font-size: 14px;">
                    💾 Log disimpan di file: <code>app.log</code>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    app.logger.info(f'Dashboard accessed - IP: {request.remote_addr}' + (f' - User: {session["username"]}' if 'username' in session else ' - Guest'))
    
    total_cctv = len(cctv_locations)
    online_cctv = len([c for c in cctv_locations if c['status'] == 'Online'])
    offline_cctv = total_cctv - online_cctv
    
    return render_template_string(
        DASHBOARD_TEMPLATE, 
        cctv_list=cctv_locations,
        total_cctv=total_cctv,
        online_cctv=online_cctv,
        offline_cctv=offline_cctv
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        app.logger.info(f'Login attempt - Username: {username} - IP: {request.remote_addr}')
        
        if username in users and users[username] == password:
            session['username'] = username
            app.logger.info(f'Login successful - Username: {username}')
            flash('Login berhasil! Selamat datang.', 'success')
            return redirect(url_for('index'))
        else:
            app.logger.warning(f'Login failed - Username: {username} - IP: {request.remote_addr}')
            flash('Username atau password salah!', 'danger')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    session.pop('username', None)
    app.logger.info(f'User logged out - Username: {username}')
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/data')
@login_required
def view_data():
    app.logger.info(f'Data page accessed - User: {session["username"]}')
    return render_template_string(DATA_TEMPLATE, data_list=sensitive_data, generate_token=generate_token)

@app.route('/data/detail/<token>')
@login_required
def view_detail(token):
    data_id = verify_token(token)
    
    if data_id is None:
        app.logger.warning(f'Invalid token access - User: {session["username"]} - Token: {token[:20]}...')
        flash('Token tidak valid atau sudah kadaluarsa!', 'danger')
        return redirect(url_for('view_data'))
    
    data = next((d for d in sensitive_data if d['id'] == data_id), None)
    
    if data is None:
        app.logger.warning(f'Data not found - ID: {data_id} - User: {session["username"]}')
        flash('Data tidak ditemukan!', 'danger')
        return redirect(url_for('view_data'))
    
    app.logger.info(f'Data detail accessed - ID: {data_id} - User: {session["username"]}')
    return render_template_string(DETAIL_TEMPLATE, data=data, token=token)

@app.route('/logs')
@login_required
def view_logs():
    app.logger.info(f'Log viewer accessed - User: {session["username"]}')
    logs = read_log_file(lines=50)
    return render_template_string(LOG_TEMPLATE, logs=logs)

if __name__ == '__main__':
    app.logger.info('='*60)
    app.logger.info('CCTV SIDOARJO - SECURE SYSTEM STARTED')
    app.logger.info('='*60)
    print('='*60)
    print('🎥 CCTV SIDOARJO - SECURE MONITORING SYSTEM')
    print('='*60)
    print('✅ Implementasi Keamanan:')
    print('  - Secure #1: Token URL terenkripsi')
    print('  - Secure #2: Session management (login required)')
    print('  - Secure #3: Logging semua aktivitas')
    print('='*60)
    print('🧪 Test Accounts:')
    print('  Username: admin | Password: password123')
    print('  Username: user1 | Password: pass456')
    print('='*60)
    print('📍 Akses aplikasi di: http://127.0.0.1:5000')
    print('='*60)
    app.run(debug=True)