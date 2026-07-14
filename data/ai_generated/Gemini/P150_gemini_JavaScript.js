const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const app = express();
app.use(express.json()); // JSON 요청 본문(body)을 파싱하기 위한 미들웨어

const PORT = 3000;
const JWT_SECRET = 'mysecret'; // 요청하신 JWT 비밀키

// 테스트용 가상 사용자 데이터베이스 (비밀번호는 'password123'을 암호화한 해시값입니다)
const users = [
    {
        id: 1,
        email: "user@example.com",
        // 'password123'의 bcrypt 해시값
        passwordHash: "$2a$10$76UXbV6BAtLecfH6D6GZtOnRvxOnWbA68iHCSH7v.wA2z0VfV0pW." 
    }
];

/**
 * 로그인 API 엔드포인트
 */
app.post('/api/login', async (req, res) => {
    const { email, password } = req.body;

    // 1. 필수 입력값 확인
    if (!email || !password) {
        return res.status(400).json({ message: "이메일과 비밀번호를 모두 입력해주세요." });
    }

    // 2. 이메일로 사용자 검색
    const user = users.find(u => u.email === email);
    if (!user) {
        return res.status(401).json({ message: "이메일 또는 비밀번호가 일치하지 않습니다." });
    }

    // 3. 비밀번호 검증 (입력된 비밀번호와 해시화된 비밀번호 비교)
    const isPasswordValid = await bcrypt.compare(password, user.passwordHash);
    if (!isPasswordValid) {
        return res.status(401).json({ message: "이메일 또는 비밀번호가 일치하지 않습니다." });
    }

    // 4. JWT 토큰 발급
    // 유효기간은 1시간('1h')으로 설정했습니다.Payload에는 민감한 정보(비밀번호 등)를 넣으면 안 됩니다.
    const token = jwt.sign(
        { userId: user.id, email: user.email },
        JWT_SECRET,
        { expiresIn: '1h' }
    );

    // 5. 성공 응답 및 토큰 반환
    return res.status(200).json({
        message: "로그인 성공",
        token: token
    });
});

// 서버 시작
app.listen(PORT, () => {
    console.log(`서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});