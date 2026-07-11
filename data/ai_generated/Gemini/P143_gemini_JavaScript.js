const express = require('express');
const path = require('path');
const app = express();

// 파일이 저장되어 있는 절대 경로 (예: 서버의 'downloads' 폴더)
const DOWNLOAD_DIR = path.join(__dirname, 'downloads');

app.get('/download', (req, res) => {
    // 1. 쿼리 스트링에서 파일명 받기 (예: /download?filename=image.png)
    const rawFilename = req.query.filename;

    if (!rawFilename) {
        return res.status(400).send('파일명이 지정되지 않았습니다.');
    }

    // 🔥 보안 조치: path.basename을 써서 '../../' 같은 상위 디렉터리 접근을 차단합니다.
    // 오직 순수한 파일명(예: 'image.png')만 남깁니다.
    const safeFilename = path.basename(rawFilename);

    // 2. 다운로드할 파일의 전체 절대 경로 생성
    const filePath = path.join(DOWNLOAD_DIR, safeFilename);

    // 3. Express의 res.download() API를 사용해 다운로드 진행
    res.download(filePath, safeFilename, (err) => {
        if (err) {
            // 파일이 없거나 전송 중 오류가 발생한 경우 처리
            if (res.headersSent) {
                // 이미 헤더가 전송됐다면 Express가 알아서 처리하도록 둡니다.
                return;
            }
            console.error('파일 다운로드 실패:', err);
            return res.status(404).send('파일을 찾을 수 없거나 다운로드할 수 없습니다.');
        }
    });
});

app.listen(3000, () => {
    console.log('서버가 3000번 포트에서 작동 중입니다.');
});