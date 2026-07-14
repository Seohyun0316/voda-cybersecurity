const express = require("express");
const path = require("path");

const app = express();

const DOWNLOAD_DIR = path.join(__dirname, "files");

app.get("/download", (req, res) => {
    const filename = req.query.file;

    // 파일명만 사용하도록 제한
    if (!filename || filename.includes("/") || filename.includes("\\")) {
        return res.status(400).send("잘못된 파일명입니다.");
    }

    const filePath = path.join(DOWNLOAD_DIR, filename);

    res.download(filePath, (err) => {
        if (err) {
            console.error(err);
            res.status(404).send("파일을 찾을 수 없습니다.");
        }
    });
});

app.listen(3000, () => {
    console.log("Server running on port 3000");
});