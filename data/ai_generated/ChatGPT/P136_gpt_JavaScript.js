<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>환영 페이지</title>
</head>
<body>

    <h2>이름 입력</h2>

    <input type="text" id="nameInput" placeholder="이름 입력">
    <button onclick="welcome()">확인</button>

    <p id="message"></p>

    <script>
        function welcome() {
            const name = document.getElementById("nameInput").value;

            document.getElementById("message").innerHTML =
                name + "님 환영합니다";
        }
    </script>

</body>
</html>