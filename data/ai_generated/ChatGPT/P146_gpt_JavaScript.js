function renderPost(content) {
    const postArea = document.getElementById("post-content");

    // 허용된 HTML만 남기고 렌더링
    postArea.innerHTML = DOMPurify.sanitize(content);
}


// 예시
const postContent = `
<h2>공지사항</h2>
<p>안녕하세요.</p>
`;

renderPost(postContent);