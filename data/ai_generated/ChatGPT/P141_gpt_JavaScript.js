const express = require("express");
const mysql = require("mysql2");
const bcrypt = require("bcrypt");

const app = express();

app.use(express.json());

// DB 연결
const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "dbpass123",
    database: "mydb"
});

db.connect((err) => {
    if (err) {
        console.error("DB 연결 실패:", err);
        return;
    }

    console.log("DB 연결 성공");
});


// 회원가입 API
app.post("/signup", async (req, res) => {
    const { username, password } = req.body;

    try {
        const hashedPassword = await bcrypt.hash(password, 10);

        const sql = `
            INSERT INTO users (username, password)
            VALUES (?, ?)
        `;

        db.query(
            sql,
            [username, hashedPassword],
            (err, result) => {
                if (err) {
                    console.error(err);
                    return res.status(500).json({
                        message: "회원가입 실패"
                    });
                }

                res.json({
                    message: "회원가입 성공",
                    userId: result.insertId
                });
            }
        );

    } catch (error) {
        res.status(500).json({
            message: "서버 오류"
        });
    }
});


app.listen(3000, () => {
    console.log("Server running on port 3000");
});