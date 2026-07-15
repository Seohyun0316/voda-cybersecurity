const express = require('express');
const sqlite3 = require('sqlite3').verbose();

const app = express();
app.use(express.json());

const DB_PASS = 'dbpass123';
const db = new sqlite3.Database('users.db');

db.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)');

app.post('/register', (req, res) => {
  const { username, password, email } = req.body;
  db.run('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', [username, password, email], (err) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: '회원가입 완료' });
  });
});

app.listen(3000, () => console.log('서버 실행 중: http://localhost:3000'));
