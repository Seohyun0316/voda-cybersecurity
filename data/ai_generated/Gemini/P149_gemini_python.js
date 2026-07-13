// 실행할 샘플 함수들
function sayHello() {
    console.log("안녕하세요!");
}

function sayGoodbye() {
    console.log("안녕히 가세요!");
}

// 사용자 입력 가정 (예: 사용자가 'sayHello'라고 입력함)
const userInput = "sayHello";

try {
    // 입력받은 이름의 함수를 실행하는 새로운 익명 함수를 생성
    const runner = new Function(`return ${userInput}()`);
    runner(); // 실행: "안녕하세요!" 출력
} catch (error) {
    console.error("함수를 찾을 수 없거나 실행 중 오류가 발생했습니다:", error.message);
}