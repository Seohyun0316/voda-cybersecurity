const express = require("express");
const jwt = require("jsonwebtoken");

const app = express();

app.use(express.json());


// JWT Secret
const JWT_SECRET = "mysecret";


// 테스트 사용자
const users = [
    {
        id: "admin",
        password: "1234",
        name: "관리자"
    }
];


// 로그인 API
app.post("/login", (req, res) => {

    const { id, password } = req.body;


    // 사용자 조회
    const user = users.find(
        (u) => u.id === id && u.password === password
    );


    if (!user) {
        return res.status(401).json({
            success: false,
            message: "아이디 또는 비밀번호가 틀렸습니다."
        });
    }


    // JWT 생성
    const token = jwt.sign(
        {
            id: user.id,
            name: user.name
        },
        JWT_SECRET,
        {
            expiresIn: "1h"
        }
    );


    res.json({
        success: true,
        message: "로그인 성공",
        token: token
    });

});



// JWT 인증 미들웨어
function authMiddleware(req, res, next) {

    const authHeader = req.headers.authorization;


    if (!authHeader) {
        return res.status(401).json({
            message: "토큰이 없습니다."
        });
    }


    const token = authHeader.replace("Bearer ", "");


    try {

        const decoded = jwt.verify(
            token,
            JWT_SECRET
        );

        req.user = decoded;

        next();


    } catch (error) {

        return res.status(401).json({
            message: "유효하지 않은 토큰입니다."
        });

    }

}



// 로그인 사용자 정보 API
app.get("/profile", authMiddleware, (req, res) => {

    res.json({
        success: true,
        user: req.user
    });

});



app.listen(3000, () => {
    console.log("Server running on port 3000");
});