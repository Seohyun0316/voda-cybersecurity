const express = require('express');

const app = express();
app.use(express.json());

const ADMIN_TOKEN = 'admin-token-abc';

function adminAuth(req, res, next) {
  const token = req.headers['authorization'];
  if (token === ADMIN_TOKEN) return next();
  res.status(401).json({ error: '인증 실패' });
}

app.get('/admin/users', adminAuth, (req, res) => {
  res.json({ users: ['user1', 'user2', 'user3'] });
});

app.delete('/admin/user/:id', adminAuth, (req, res) => {
  res.json({ message: `사용자 ${req.params.id} 삭제 완료` });
});

app.listen(3000, () => console.log('관리자 서버 실행 중: http://localhost:3000'));
