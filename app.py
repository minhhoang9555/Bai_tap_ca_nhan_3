from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Cấu hình ứng dụng Flask
app.config['SECRET_KEY'] = 'a_random_secret_key_here'  # Cần thay thế bằng secret key mạnh
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:Minh123456@localhost/music_library')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo SQLAlchemy và LoginManager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Cấu hình đường dẫn login
login_manager.login_view = "login"

# Định nghĩa model User cho việc đăng ký và đăng nhập
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Định nghĩa model Song cho việc quản lý bài hát
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)

# Tạo bảng khi lần đầu chạy ứng dụng
@app.before_first_request
def create_tables():
    db.create_all()

# Đăng nhập người dùng
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route trang chủ, yêu cầu người dùng phải đăng nhập
@app.route('/')
@login_required
def index():
    songs = Song.query.all()  # Lấy tất cả bài hát trong cơ sở dữ liệu
    return render_template('index.html', songs=songs)

# Route đăng ký người dùng mới
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')

    return render_template('login.html')

# Route đăng xuất
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route thêm bài hát mới
@app.route('/add_song', methods=['POST'])
@login_required
def add_song():
    # Lấy dữ liệu từ form
    title = request.form['title']
    artist = request.form['artist']
    file_path = request.form['file_path']

    # Tạo và thêm bài hát mới vào cơ sở dữ liệu
    new_song = Song(title=title, artist=artist, file_path=file_path)
    db.session.add(new_song)
    db.session.commit()

    # Hiển thị thông báo và quay lại trang chủ
    flash('Song added successfully!', 'success')
    return redirect(url_for('index'))


# Route phát nhạc (play song)
@app.route('/play/<int:song_id>')
@login_required
def play(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template('play_song.html', song=song)
# Route để chỉnh sửa bài hát
@app.route('/edit_song/<int:song_id>', methods=['GET', 'POST'])
@login_required
def edit_song(song_id):
    song = Song.query.get_or_404(song_id)
    if request.method == 'POST':
        song.title = request.form['title']
        song.artist = request.form['artist']
        song.file_path = request.form['file_path']
        
        db.session.commit()
        flash('Song updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_song.html', song=song)

# Route để xóa bài hát
@app.route('/delete_song/<int:song_id>', methods=['POST'])
@login_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    flash('Song deleted successfully!', 'success')
    return redirect(url_for('index'))

# Khởi chạy ứng dụng
if __name__ == "__main__":
    app.run(debug=True)
