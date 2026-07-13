const express = require('express');
const app = express();
const PORT = 3000;

// JSON 요청 본문을 파싱하기 위한 미들웨어
app.use(express.json());

// 하드코딩된 관리자 토큰
const ADMIN_TOKEN = 'admin-token-abc';

/**
 * 관리자 인증 미들웨어
 * 요청 헤더의 Authorization 항목을 확인합니다.
 */
const authenticateAdmin = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    
    // 토큰 형식 체크 (Bearer admin-token-abc 또는 admin-token-abc)
    if (!authHeader) {
        return res.status(401).json({ message: '인증 토큰이 필요합니다.' });
    }

    // Bearer 패턴 대응 및 토큰 값 추출
    const token = authHeader.startsWith('Bearer ') ? authHeader.split(' ')[1] : authHeader;

    if (token !== ADMIN_TOKEN) {
        return res.status(403).json({ message: '권한이 없는 토큰입니다. 관리자만 접근 가능합니다.' });
    }

    // 인증 성공 시 다음 로직으로 진행
    next();
};

// 1. 관리자 전용 대시보드 데이터 조회 (GET)
app.get('/api/admin/dashboard', authenticateAdmin, (req, res) => {
    res.json({
        message: '관리자 대시보드 데이터 조회 성공',
        stats: {
            totalUsers: 1250,
            activeUsers: 420,
            dailyRevenue: 540000
        }
    });
});

// 2. 사용자 관리 - 사용자 차단 (POST)
app.post('/api/admin/users/:userId/block', authenticateAdmin, (req, res) => {
    const { userId } = req.params;
    const { reason } = req.body;

    // 실제 환경에서는 DB 로직이 들어갑니다.
    res.json({
        message: `사용자(ID: ${userId})가 성공적으로 차단되었습니다.`,
        reason: reason || '사유 미지정'
    });
});

// 서버 시작
app.listen(PORT, () => {
    console.log(`관리자 API 서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});