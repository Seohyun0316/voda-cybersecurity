<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>´ñ±Û ±â´É</title>
</head>
<body>

    <h2>´ñ±Û</h2>

    <input type="text" id="commentInput" placeholder="´ñ±Û ÀÔ·Â">
    <button onclick="addComment()">µî·Ï</button>

    <div id="comments"></div>

    <script>
        function addComment() {
            const comment = document.getElementById("commentInput").value;

            document.getElementById("comments").innerHTML +=
                "<p>" + comment + "</p>";

            document.getElementById("commentInput").value = "";
        }
    </script>

</body>
</html>