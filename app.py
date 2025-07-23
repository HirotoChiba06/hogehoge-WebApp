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
    if request.method == 'POST':
        message_id = request.form['message_id']
        reply_content = request.form['reply']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect('db/messages.db', timeout=10) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO replies (message_id, content, timestamp) VALUES (?, ?, ?)",
                      (message_id, reply_content, timestamp))
            c.execute("UPDATE messages SET replies = replies + 1 WHERE id = ?", (message_id,))
            conn.commit()
        return redirect(url_for('receive_complete'))

    # GETメソッド時の表示
    with sqlite3.connect('db/messages.db') as conn:
        c = conn.cursor()
        c.execute("SELECT id, content FROM messages WHERE replies < 3 ORDER BY RANDOM() LIMIT 1")
        message = c.fetchone()

    if not message:
        return render_template('receive.html', error="今受信できるボトルはありません。")

    message_id, content = message
    return render_template('receive.html', message_id=message_id, content=content)


@app.route('/receive_complete')
def receive_complete():
    return render_template('receive_complete.html')

@app.route('/archive')
def archive():
    origin_key = request.args.get('key')  # 投稿者識別キー
    if not origin_key:
        return render_template('archive.html', error="キーが指定されていません。")

    conn = sqlite3.connect('db/messages.db')
    c = conn.cursor()

    # 投稿者のボトルを取得（3件以上返信されているもの）
    c.execute("SELECT id, content FROM messages WHERE origin_key = ? AND replies >= 3", (origin_key,))
    message = c.fetchone()

    if not message:
        conn.close()
        return render_template('archive.html', error="返信が集まったメッセージが見つかりません。")

    message_id, content = message

    # 返信一覧を取得
    c.execute("SELECT content, timestamp FROM replies WHERE message_id = ? ORDER BY id", (message_id,))
    replies = c.fetchall()

    conn.close()
    return render_template('archive.html', content=content, replies=replies)


# ✅ユーティリティ関数（投稿者識別キー生成）
def generate_key():
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    return "USER-" + now

if __name__ == '__main__':
    app.run(debug=True)
