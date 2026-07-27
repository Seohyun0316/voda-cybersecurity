/**
 * 탐지 범위에 replacement를 대입했을 때 사용자에게 보여줄 한 줄 미리보기.
 *
 * 백엔드가 줄 시작부터 탐지하면서 완성된 문장 전체를 replacement로 보내는
 * 경우에는 원문의 미탐지 suffix를 붙이지 않는다. 그 외에는 탐지 범위만
 * replacement로 바꿔 주변 문맥을 함께 보여준다.
 */
export function buildSuggestedCodePreview(
  line: string,
  startColumn: number,
  endColumn: number,
  replacement: string,
): string {
  const firstCodeColumn = line.length - line.trimStart().length;
  if (startColumn === firstCodeColumn && endColumn < line.length) {
    return line.slice(0, firstCodeColumn) + replacement;
  }
  return line.slice(0, startColumn)
    + replacement
    + line.slice(endColumn);
}
