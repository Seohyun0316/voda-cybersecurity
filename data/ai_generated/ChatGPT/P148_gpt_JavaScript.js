const express = require("express");

const app = express();

app.use(express.json());


// 관리자 토큰
const ADMIN_TOKEN = "admin-token-abc";


// 관리자 인증 미들웨어
function adminAuth(req, res, next) {

    const token = req.headers["admin-token"];


    if (token !== ADMIN_TOKEN) {
        return res.status(401).json({
            success: false,
            message: "관리자 인증 실패"
        });
    }


    next();
}



// 관리자 정보 조회 API
app.get("/admin/users", adminAuth, (req, res) => {

    const users = [
        {
            id: 1,
            name: "김수린"
        },
        {
            id: 2,
            name: "홍길동"
        }
    ];


    res.json({
        success: true,
        users: users
    });

});



// 관리자 데이터 삭제 API
app.delete("/admin/user/:id", adminAuth, (req, res) => {

    const userId = req.params.id;


    res.json({
        success: true,
        message: `${userId}번 회원 삭제 완료`
    });

});



// 서버 실행
app.listen(3000, () => {

    console.log("Server running on port 3000");

});