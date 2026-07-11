/**
 * 문자열로 된 수식을 받아 eval()로 계산하는 함수
 * @param {string} expression - 계산할 수식 (예: '2 + 3 * 4')
 * @returns {number|string} - 계산 결과 또는 에러 메시지
 */
function calculateExpression(expression) {
    // 공백 제거
    const cleanExpression = expression.replace(/\s+/g, '');

    // 빈 입력값 처리
    if (!cleanExpression) {
        return 0;
    }

    try {
        // 보안 및 유효성 검사: 숫자, 사칙연산자(+, -, *, /), 마침표(.)만 허용
        // eval을 사용할 때는 최소한의 방어 코증를 넣는 것이 좋습니다.
        const isValid = /^[\d+\-*/.]*$/.test(cleanExpression);
        
        if (!isValid) {
            throw new Error("Invalid characters");
        }

        // eval을 통한 수식 계산
        const result = eval(cleanExpression);
        
        return result;
    } catch (error) {
        // 잘못된 수식(예: '5++2')이나 허용되지 않은 문자 입력 시 처리
        return 'Error';
    }
}

// --- 테스트 코드 ---
console.log(calculateExpression("2 + 3 * 4")); // 출력: 14
console.log(calculateExpression("10 / 2 - 1")); // 출력: 4
console.log(calculateExpression("5 ++ 2"));     // 출력: Error (잘못된 수식)
console.log(calculateExpression("alert('danger')")); // 출력: Error (허용되지 않은 문자)