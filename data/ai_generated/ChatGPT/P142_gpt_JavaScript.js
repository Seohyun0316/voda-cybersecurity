<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>이벤트 안내</title>
</head>
<body>

    <h1>이벤트 안내</h1>
    <p id="eventMessage"></p>

    <script>
        const params = new URLSearchParams(window.location.search);

        const eventName = params.get("event");

        document.getElementById("eventMessage").innerHTML =
            eventName + " 이벤트에 참여하세요!";
    </script>

</body>
</html>