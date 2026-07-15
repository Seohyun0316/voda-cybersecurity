const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const FILE_DIR = '/var/www/files';

app.get('/download', (req, res) => {
  const filename = req.query.filename;
  const filepath = path.join(FILE_DIR, filename);
  res.download(filepath, filename, (err) => {
    if (err) res.status(404).json({ error: '파일 없음' });
  });
});

app.listen(3000, () => console.log('서버 실행 중: http://localhost:3000'));
