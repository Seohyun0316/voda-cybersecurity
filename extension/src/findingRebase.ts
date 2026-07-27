import { Finding } from './analyzer';

/** VS Code의 TextDocumentContentChangeEvent에서 위치 보정에 필요한 필드. */
export interface OffsetTextChange {
  rangeOffset: number;
  rangeLength: number;
  text: string;
}

/**
 * 문서 편집 뒤 기존 탐지 결과를 새 문서 위치로 옮긴다.
 *
 * - 편집 범위와 겹친 finding은 수정된 것으로 보고 제거한다.
 * - 편집 범위 뒤의 finding은 삽입·삭제 길이만큼 이동한다.
 * - 겹치지 않은 finding의 코드 자체는 바뀌지 않았으므로 다음 수정 제안에 계속 쓴다.
 */
export function rebaseFindings(
  findings: Finding[],
  originalText: string,
  currentText: string,
  changes: OffsetTextChange[],
): Finding[] {
  if (changes.length === 0) return findings;

  const originalLineStarts = lineStartOffsets(originalText);
  const currentLineStarts = lineStartOffsets(currentText);
  const orderedChanges = [...changes].sort((a, b) => a.rangeOffset - b.rangeOffset);
  const rebased: Finding[] = [];

  for (const finding of findings) {
    const originalStart = positionToOffset(
      originalText,
      originalLineStarts,
      finding.line,
      finding.startCol,
    );
    const originalEnd = positionToOffset(
      originalText,
      originalLineStarts,
      finding.line,
      finding.endCol,
    );
    let offsetDelta = 0;
    let overlapsEdit = false;

    for (const change of orderedChanges) {
      const changeStart = change.rangeOffset;
      const changeEnd = changeStart + change.rangeLength;
      const insertsInsideFinding =
        change.rangeLength === 0
        && changeStart >= originalStart
        && changeStart <= originalEnd;

      if (!insertsInsideFinding && changeEnd <= originalStart) {
        offsetDelta += change.text.length - change.rangeLength;
        continue;
      }
      if (!insertsInsideFinding && changeStart >= originalEnd) continue;

      overlapsEdit = true;
      break;
    }

    if (overlapsEdit) continue;

    const currentStart = offsetToPosition(
      currentText,
      currentLineStarts,
      originalStart + offsetDelta,
    );
    const currentEnd = offsetToPosition(
      currentText,
      currentLineStarts,
      originalEnd + offsetDelta,
    );
    if (currentStart.line !== currentEnd.line) continue;

    rebased.push({
      ...finding,
      line: currentStart.line,
      startCol: currentStart.character,
      endCol: currentEnd.character,
    });
  }

  return rebased;
}

function lineStartOffsets(text: string): number[] {
  const starts = [0];
  const newline = /\r\n|\r|\n/g;
  let match: RegExpExecArray | null;

  while ((match = newline.exec(text)) !== null) {
    starts.push(match.index + match[0].length);
  }
  return starts;
}

function positionToOffset(
  text: string,
  lineStarts: number[],
  line: number,
  character: number,
): number {
  const safeLine = Math.min(Math.max(line, 0), lineStarts.length - 1);
  const lineStart = lineStarts[safeLine];
  const nextLineStart = lineStarts[safeLine + 1] ?? text.length;
  const lineEnd = trimNewlineEnd(text, lineStart, nextLineStart);
  return Math.min(lineStart + Math.max(character, 0), lineEnd);
}

function offsetToPosition(
  text: string,
  lineStarts: number[],
  offset: number,
): { line: number; character: number } {
  const safeOffset = Math.min(Math.max(offset, 0), text.length);
  let low = 0;
  let high = lineStarts.length - 1;

  while (low <= high) {
    const middle = Math.floor((low + high) / 2);
    if (lineStarts[middle] <= safeOffset) {
      low = middle + 1;
    } else {
      high = middle - 1;
    }
  }

  const line = Math.max(high, 0);
  return { line, character: safeOffset - lineStarts[line] };
}

function trimNewlineEnd(text: string, lineStart: number, nextLineStart: number): number {
  let end = nextLineStart;
  if (end > lineStart && text[end - 1] === '\n') end -= 1;
  if (end > lineStart && text[end - 1] === '\r') end -= 1;
  return end;
}
