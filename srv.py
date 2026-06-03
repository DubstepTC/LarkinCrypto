from flask import Flask, request, render_template_string, jsonify
import cypher
import csv
import datetime
import os

app = Flask(__name__)
CSV_FILE = "messages.csv"

# Полностью русифицированный черно-зеленый HTML/CSS шаблон
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Терминал: Сервер Шифрования</title>
    <style>
        /* Настройки окружения в стиле темного терминала */
        body { 
            font-family: 'Consolas', 'Courier New', monospace; 
            background-color: #121212; 
            color: #e0e0e0; 
            margin: 0; 
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        /* Монолитный контейнер формы */
        .container { 
            width: 100%;
            max-width: 480px; 
            background: #1e1e1e; 
            padding: 30px; 
            border-radius: 4px; 
            box-shadow: 0 0 20px rgba(0, 255, 102, 0.05);
            border: 1px solid #2d2d2d;
            box-sizing: border-box;
        }

        /* Заголовок с неоновым акцентом */
        h2 { 
            color: #00ff66; 
            font-size: 1.3rem;
            margin-top: 0;
            margin-bottom: 25px;
            letter-spacing: 1px;
            text-transform: uppercase;
            border-bottom: 1px dashed #2d2d2d;
            padding-bottom: 10px;
        }

        label {
            color: #888888;
            font-size: 0.85rem;
            display: block;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        /* Кастомное поле ввода текста */
        textarea { 
            width: 100%; 
            height: 120px; 
            padding: 12px; 
            box-sizing: border-box; 
            background-color: #2d2d2d;
            color: #00ff66;
            border: 1px solid #3d3d3d; 
            border-radius: 2px;
            resize: none; 
            font-family: 'Consolas', monospace;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }

        /* Эффект свечения при фокусе на поле */
        textarea:focus {
            border-color: #00ff66;
            box-shadow: 0 0 10px rgba(0, 255, 102, 0.2);
        }

        /* Хакерская кнопка отправки с анимацией */
        input[type="submit"] { 
            background-color: #2d2d2d; 
            color: #00ff66; 
            width: 100%;
            padding: 14px; 
            margin-top: 15px;
            border: 1px solid #00ff66; 
            border-radius: 2px; 
            cursor: pointer; 
            font-family: 'Consolas', monospace;
            font-size: 0.95rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }

        /* Инверсия цветов при наведении мыши */
        input[type="submit"]:hover { 
            background-color: #00ff66; 
            color: #121212;
            box-shadow: 0 0 15px rgba(0, 255, 102, 0.4);
        }

        /* Блок успешного статуса выполнения */
        .success { 
            color: #00ff66; 
            background-color: rgba(0, 255, 102, 0.05);
            border-left: 3px solid #00ff66;
            padding: 10px;
            margin-top: 20px; 
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Система: Ядро шифрования</h2>
        <form method="POST">
            <label for="text">> root@поток_входных_данных:</label>
            <textarea name="text" id="text" placeholder="Введите текст для шифрования..." required></textarea>
            <input type="submit" value="[ Выполнить шифрование ]">
        </form>
        {% if message %}
            <div class="success">СТАТУС: {{ message }}</div>
        {% endif %}
    </div>
</body>
</html>
'''


@app.route('/70225220', methods=['GET', 'POST'])
def handle_message():
    message = None
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if text:
            encrypted_text = cypher.encrypt(text)
            ip_address = request.remote_addr
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Высчитываем следующий порядковый ID для базы данных
            next_id = 1
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, 'r', encoding='utf-8') as f:
                    reader = list(csv.reader(f))
                    if reader:
                        try:
                            next_id = int(reader[-1][0]) + 1
                        except (ValueError, IndexError):
                            next_id = len(reader) + 1

            # Записываем строку в CSV файл
            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([next_id, timestamp, ip_address, encrypted_text])

            message = "ДАННЫЕ УСПЕШНО ЗАШИФРОВАНЫ И ЗАПИСАНЫ В БАЗУ."

    return render_template_string(HTML_TEMPLATE, message=message)


@app.route('/reset', methods=['GET'])
def reset():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    return "<body style='background:#121212;color:#ff3333;font-family:monospace;padding:20px;'><p>> Файл базы данных messages.csv успешно уничтожен.</p></body>"


@app.route('/get_all.json', methods=['GET'])
def get_all():
    data = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 4:
                    data.append({
                        "id": row[0],
                        "time": row[1],
                        "ip": row[2],
                        "decrypted_text": cypher.decrypt(row[3])
                    })
    return jsonify(data)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
