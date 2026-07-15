const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

const JWT_SECRET = 'mysecret';
const users = { admin: 'password123', user: 'userpass' };

app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (users[username] && users[username] === password) {
    const token = jwt.sign({ username }, JWT_SECRET, { expiresIn: '24h' });
    return res.json({ token });
  }
  res.status(401).json({ message: '인증 실패' });
});

app.get('/protected', (req, res) => {
  const token = req.headers['authorization']?.split(' ')[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    res.json({ message: '인증 성공', user: decoded.username });
  } catch (e) {
    res.status(401).json({ message: '토큰 무효' });
  }
});

app.listen(3000, () => console.log('서버 실행 중: http://localhost:3000'));
