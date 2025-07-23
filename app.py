from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ✅ルート: トップページ
@app.route('/')
def index():
    return render_template('index.html')

# ✅ルート: メッセージ送信
@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        content = request.form['message']
        if len(content) <= 360:
            conn = sqlite3.connect('db/messages.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO messages (content, replies, status, origin_key)
                VALUES (?, 0, ?, ?)
            ''', (content, '漂流中', generate_key()))
            conn.commit()
            conn.close()
            return redirect(url_for('send_complete'))
        else:
            error = "メッセージは360文字で入力してください。"
            return render_template('send.html', error=error)
    return render_template('send.html')

# ✅ルート: 完了メッセージ
@app.route('/send_complete')
def send_complete():
    return render_template('send_complete.html')

@app.route('/receive', methods=['GET', 'POST'])
def receive():
    conn = sqlite3.connect('db/messages.db')
    c = conn.cursor()

    # ✅返信数が3未満のボトルをランダムで1件抽出
    c.execute("SELECT id, content FROM messages WHERE replies < 3 ORDER BY RANDOM() LIMIT 1")
    message = c.fetchone()

    if not message:
        conn.close()
        return render_template('receive.html', error="今受信できるボトルはありません。")

    message_id, content = message

    if request.method == 'POST':
        reply_content = request.form['reply']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅replies テーブルに保存
        c.execute("INSERT INTO replies (message_id, content, timestamp) VALUES (?, ?, ?)",
                  (message_id, reply_content, timestamp))

        # ✅messages テーブルの返信数更新
        c.execute("UPDATE messages SET replies = replies + 1 WHERE id = ?", (message_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('receive_complete'))

    conn.close()
    return render_template('receive.html', message_id=message_id, content=content)

@app.route('/receive_complete')
def receive_complete():
    return render_template('receive_complete.html')

# ✅ユーティリティ関数（投稿者識別キー生成）
def generate_key():
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    return "USER-" + now

if __name__ == '__main__':
    app.run(debug=True)
