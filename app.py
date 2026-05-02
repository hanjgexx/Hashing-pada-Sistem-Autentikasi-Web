"""
Prototype Sistem Autentikasi dengan Hashing Password
Teknologi  : Python Flask
Hashing    : Bcrypt (via flask-bcrypt)
Database   : SQLite (via SQLAlchemy)
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# ─── Inisialisasi App ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.urandom(24)          # Key rahasia untuk session
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db     = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ─── Model Database ──────────────────────────────────────────────────────────
class User(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80),  unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(256), nullable=False)   # Bcrypt hash
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Halaman utama — redirect ke dashboard jika sudah login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registrasi pengguna baru.
    POST: validasi input → hash password dengan Bcrypt → simpan ke DB.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # ── Validasi Input ──────────────────────────────────────────────────
        errors = []
        if not username or not email or not password:
            errors.append('Semua field wajib diisi.')
        if len(username) < 3:
            errors.append('Username minimal 3 karakter.')
        if len(password) < 8:
            errors.append('Password minimal 8 karakter.')
        if password != confirm:
            errors.append('Konfirmasi password tidak cocok.')
        if User.query.filter_by(username=username).first():
            errors.append('Username sudah digunakan.')
        if User.query.filter_by(email=email).first():
            errors.append('Email sudah terdaftar.')

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('register.html', username=username, email=email)

        # ── Proses Hashing ──────────────────────────────────────────────────
        # bcrypt.generate_password_hash() secara otomatis:
        #   1. Membuat salt acak (16 byte)
        #   2. Melakukan key stretching (work factor = 12 → 2^12 = 4096 iterasi)
        #   3. Menghasilkan hash 60-karakter dengan format:
        #      $2b$12$<22-char-salt><31-char-hash>
        password_hash = bcrypt.generate_password_hash(
            password, rounds=12
        ).decode('utf-8')

        new_user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Registrasi berhasil! Silakan login, {username}.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login pengguna.
    POST: cari user di DB → verifikasi password dengan check_password_hash.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username dan password harus diisi.', 'error')
            return render_template('login.html', username=username)

        user = User.query.filter_by(username=username).first()

        # ── Verifikasi Hash ─────────────────────────────────────────────────
        # bcrypt.check_password_hash() akan:
        #   1. Mengambil salt dari hash yang tersimpan
        #   2. Meng-hash ulang password input dengan salt yang sama
        #   3. Membandingkan hasilnya secara constant-time (mencegah timing attack)
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id']  = user.id
            session['username'] = user.username
            flash(f'Selamat datang kembali, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Pesan error sengaja dibuat generik → tidak memberi tahu attacker
            # apakah username atau password yang salah
            flash('Username atau password salah.', 'error')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    """Halaman dashboard — hanya bisa diakses jika sudah login."""
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)


@app.route('/db-view')
def db_view():
    """
    Halaman debug — menampilkan isi database (hanya untuk demo/edukasi).
    PERINGATAN: Jangan gunakan fitur ini di aplikasi produksi!
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('db_view.html', users=users)


@app.route('/logout')
def logout():
    """Hapus session dan redirect ke halaman login."""
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # Buat tabel jika belum ada
        print("Database berhasil dibuat: instance/users.db")
    app.run(debug=True, port=5000)
