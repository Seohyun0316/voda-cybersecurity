<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>방명록</title>
</head>
<body>

    <h2>방명록</h2>

    <input type="text" id="messageInput" placeholder="메시지 입력">
    <button onclick="addMessage()">등록</button>

    <ul id="guestbook"></ul>

    <script>
        function addMessage() {
            const message = document.getElementById("messageInput").value;

            document.getElementById("guestbook").innerHTML +=
                "<li>" + message + "</li>";

            document.getElementById("messageInput").value = "";
        }
    </script>

</body>
</html>