function showResult() {
    // 1. input 창과 결과 표시 영역의 DOM 요소를 가져옵니다.
    const searchInput = document.getElementById('searchInput');
    const resultView = document.getElementById('resultView');
    
    // 2. 입력된 값의 앞뒤 공백을 제거하고 가져옵니다.
    const keyword = searchInput.value.trim();
    
    // 3. 조건에 따라 화면에 텍스트를 출력합니다.
    if (keyword === "") {
        resultView.innerText = "검색어를 입력해주세요.";
    } else {
        // 요구하신 "'OO' 검색 결과" 형태로 출력합니다.
        resultView.innerText = `'${keyword}' 검색 결과`;
    }
}