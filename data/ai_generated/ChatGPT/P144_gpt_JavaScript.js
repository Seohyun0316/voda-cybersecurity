<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>프로필</title>
</head>
<body>

    <h2>프로필 작성</h2>

    <textarea id="introInput" placeholder="자기소개 입력"></textarea>
    <button onclick="saveProfile()">저장</button>

    <h2>내 프로필</h2>
    <div id="profile"></div>

    <script>
        function saveProfile() {
            const intro = document.getElementById("introInput").value;

            document.getElementById("profile").innerHTML = intro;
        }
    </script>

</body>
</html>