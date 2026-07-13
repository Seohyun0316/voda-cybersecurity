<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>검색 결과</title>
</head>
<body>

    <input type="text" id="searchInput" placeholder="검색어 입력">
    <button onclick="search()">검색</button>

    <h2 id="result"></h2>

    <script>
        function search() {
            const keyword = document.getElementById("searchInput").value;

            document.getElementById("result").innerHTML =
                "'" + keyword + "' 검색 결과";
        }
    </script>

</body>
</html>