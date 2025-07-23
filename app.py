from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        content = request.form['message']
        if 240 <= len(content) <= 360:
            # DB保存処理
            conn = sqlite3.connect('db/messages.db')
            c = conn.cursor()
            c.execute("INSERT INTO messages (content, replies, status) VALUES (?, 0, '漂流中')", (content,))
            conn.commit()
            conn.close()
            return redirect(url_for('send_complete'))
        else:
            error = "240〜360文字で入力してください"
            return render_template('send.html', error=error)
    return render_template('send.html')

@app.route('/send_complete')
def send_complete():
    return render_template('send_complete.html')  # 「漂流しました」画面
