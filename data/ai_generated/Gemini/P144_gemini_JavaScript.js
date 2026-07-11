// 1. HTML의 요소(Element)들을 가져옵니다.
const bioInput = document.getElementById('bio-input');     // 입력창 (textarea 등)
const updateBtn = document.getElementById('update-btn');   // 등록 버튼
const profileBio = document.getElementById('profile-bio'); // 프로필 표시 영역

// 2. 버튼을 클릭했을 때 실행할 이벤트를 등록합니다.
updateBtn.addEventListener('click', function() {
    
    // 3. 사용자가 입력창에 쓴 텍스트(값)를 가져옵니다.
    const userIntro = bioInput.value;
    
    // 4. 요청하신 innerHTML을 사용해 프로필 영역에 그대로 주입합니다.
    profileBio.innerHTML = userIntro;
    
    // (선택 사항) 입력이 끝난 후 입력창을 깨끗하게 비우고 싶다면 아래 주석을 해제하세요.
    // bioInput.value = '';
});