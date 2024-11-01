from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Инициализация базы данных и других расширений
app.config['12345678'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/avatars'  # Папка для загрузки аватаров

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

migrate = Migrate(app, db)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    avatar = db.Column(db.String(120), default='default_avatar.png')
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш аккаунт создан!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Вы вошли в систему!', 'success')
            return redirect(url_for('dashboard'))  # Перенаправление на главную страницу
        else:
            flash('Ошибка входа. Проверьте логин и пароль.', 'danger')
    return render_template('login.html')

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Обработка загрузки аватара
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.avatar = filename  # Обновление пути к аватару
                db.session.commit()
                flash('Аватар успешно изменен!', 'success')
    return render_template('profile.html')

def init_db():
    conn = sqlite3.connect('notifications.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Инициализация базы данных
init_db()



def inity_db():
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
inity_db()
    
def seed_services():
    services_data = [
        ('Городская поликлиника №1', 'Поликлиника', 'ул. Ленина, 1', '+7 (7152) 42-00-01', 54.867170, 69.187653),
        ('Городская поликлиника №2', 'Поликлиника', 'ул. Бухар Жырау, 3', '+7 (7152) 42-00-02', 54.867140, 69.188500),
        ('Спортивный комплекс «Олимп»', 'Спортивный центр', 'ул. Островского, 2', '+7 (7152) 42-22-25', 54.868210, 69.185710),
        ('Центр отдыха «Жас Ұлан»', 'Спортивный центр', 'ул. Вагжанова, 5', '+7 (7152) 42-33-55', 54.868500, 69.186500),
        ('Парковка у ТЦ «Керуен»', 'Парковка', 'пр. Кутузова, 12', '+7 (7152) 42-77-88', 54.870000, 69.184500),
        ('Точка сбора мусора (район ТЦ «Сити»)', 'Пункт сбора мусора', 'ул. Розыбакиева, 10', '+7 (7152) 42-88-99', 54.868700, 69.185000),
        ('Поликлиника для детей', 'Детская поликлиника', 'ул. Советская, 45', '+7 (7152) 42-11-21', 54.867500, 69.187000),
        ('Центр социальной помощи семье и детям', 'Социальная служба', 'ул. Шевченко, 30', '+7 (7152) 42-33-00', 54.868600, 69.188100),
    ]
    
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM services')
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.executemany('INSERT INTO services (name, type, address, phone, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)', services_data)
        conn.commit()
    
    conn.close()


reviews = []

events = []

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/notification', methods=['GET', 'POST'])
def notification():
    if request.method == 'POST':
        notification_type = request.form['type']
        message = request.form['message']
        conn = sqlite3.connect('notifications.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO notifications (type, message) VALUES (?, ?)', (notification_type, message))
        conn.commit()
        conn.close()
        return redirect(url_for('notification'))

    # Получение уведомлений из базы данных
    conn = sqlite3.connect('notifications.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notifications ORDER BY id DESC')
    notifications = cursor.fetchall()  # Список уведомлений
    conn.close()
    
    return render_template('notification.html', notifications=notifications)


@app.route('/events', methods=['GET', 'POST'])
def events_page():
    if request.method == 'POST':
        # Получаем данные из формы
        event_name = request.form.get('name')
        event_date = request.form.get('date')
        event_location = request.form.get('location')
        
        # Добавляем новое мероприятие в список
        if event_name and event_date and event_location:
            events.append({'name': event_name, 'date': event_date, 'location': event_location})
        
        # Перенаправляем пользователя на страницу мероприятий
        return redirect(url_for('events_page'))

    # Отображаем страницу мероприятий
    return render_template('events.html', events=events)


@app.route('/services', methods=['GET'])
def services():
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services')
    services = cursor.fetchall()  # Список служб
    conn.close()
    
    return render_template('services.html', services=services)



@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        review_text = request.form.get('review')
        
        # Добавляем новый отзыв в список
        if name and review_text:
            reviews.append({'name': name, 'review': review_text})
        
        # Перенаправляем пользователя на страницу отзывов
        return redirect(url_for('feedback'))

    # Отображаем страницу отзывов
    return render_template('feedback.html', reviews=reviews)

@app.route('/emergency')
def emergency():
    # Передаем каждую службу отдельно
    return render_template(
        'emergency.html',
        police_name="Полиция", police_phone="102",
        ambulance_name="Скорая помощь", ambulance_phone="103",
        fire_name="Пожарная служба", fire_phone="101",
        gas_name="Газовая служба", gas_phone="104"
    )
@app.route('/qrcode')
def qrcode():
    return render_template('qrcode.html')


if __name__ == "__main__":
    app.run(host = '0.0.0.0')