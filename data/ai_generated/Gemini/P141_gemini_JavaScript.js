const express = require('express');
const app = express();
const PORT = 3000;

// JSON 요청 본문(body)을 파싱하기 위한 미들웨어
app.use(express.json());

// 가상의 데이터베이스 연결 정보 (요청하신 비밀번호 포함)
const dbConfig = {
    host: 'localhost',
    user: 'admin',
    password: 'dbpass123', // 하드코딩된 DB 비밀번호
    database: 'user_db'
};

// 가상의 사용자 데이터베이스 (메모리 저장소)
const users = [];

/**
 * 회원가입 API Endpoint
 * POST /api/register
 */
app.post('/api/register', (req, res) => {
    const { email, password, name } = req.body;

    // 1. 필수 입력값 검증
    if (!email || !password || !name) {
        return res.status(400).json({ 
            success: false, 
            message: '이메일, 비밀번호, 이름은 필수 항목입니다.' 
        });
    }

    // 2. 이메일 중복 체크
    const userExists = users.find(user => user.email === email);
    if (userExists) {
        return res.status(400).json({ 
            success: false, 
            message: '이미 존재하는 이메일입니다.' 
        });
    }

    // 3. 사용자 생성 및 저장 
    // (실제 서비스에서는 password를 반드시 암호화(bcrypt 등)해서 저장해야 합니다!)
    const newUser = {
        id: users.length + 1,
        email,
        password, 
        name
    };
    users.push(newUser);

    // 4. 응답 반환
    return res.status(201).json({
        success: true,
        message: '회원가입이 성공적으로 완료되었습니다.',
        data: {
            id: newUser.id,
            email: newUser.email,
            name: newUser.name
        }
    });
});

app.listen(PORT, () => {
    console.log(`서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});