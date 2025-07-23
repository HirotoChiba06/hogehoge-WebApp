import sqlite3

conn = sqlite3.connect('db/messages.db')
c = conn.cursor()

# 手紙テーブル
c.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    replies INTEGER DEFAULT 0,
    status TEXT,
    origin_key TEXT
)
''')

# 返信テーブル
c.execute('''
CREATE TABLE IF NOT EXISTS replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT
)
''')

conn.commit()
conn.close()
print("✅ データベースとテーブルの初期化が完了しました")