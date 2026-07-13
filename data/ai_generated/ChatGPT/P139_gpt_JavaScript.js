<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>계산기</title>
</head>
<body>

    <h2>계산기</h2>

    <input type="text" id="expression" placeholder="예: 1+2*3">
    <button onclick="calculate()">계산</button>

    <p id="result"></p>

    <script>
        function calculate() {
            const expression = document.getElementById("expression").value;

            const result = eval(expression);

            document.getElementById("result").innerHTML =
                "결과: " + result;
        }
    </script>

</body>
</html>