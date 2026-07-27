/**
 * 로컬 규칙 기반 분석 엔진 (F2 담당).
 *
 * ML 백엔드가 연결되기 전까지 실제 탐지를 담당한다.
 * 규칙을 추가하려면 RULES 배열에 항목을 추가하면 된다.
 */
import {
  AnalysisResult,
  Analyzer,
  Category,
  Finding,
  FixSuggestion,
  LegalRisk,
  Severity,
  computeRiskScore,
} from './types';

interface Rule {
  id: string;
  cwe: string;
  /** 한 줄 단위로 검사할 정규식 (g 플래그 필수 — 한 줄에 여러 건 탐지) */
  pattern: RegExp;
  severity: Severity;
  category: Category;
  message: string;
  detail: string;
  legal?: LegalRisk;
  /** 매치 텍스트를 받아 교체 문자열을 만드는 함수 (없으면 quick fix 없음) */
  makeFix?: (match: string, languageId: string) => FixSuggestion | undefined;
}

const PIPA_29: LegalRisk = {
  law: '개인정보보호법',
  article: '§29',
  description: '하드코딩된 인증정보 또는 개인정보 노출',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌, 과징금·과태료',
};

const SQLI_LEGAL: LegalRisk = {
  law: '개인정보보호법, 정보통신망법, 형법',
  article: 'CWE-89',
  description: 'SQL Injection으로 개인정보 유출 가능',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌, 과징금·과태료',
};

const COMMAND_INJECTION_LEGAL: LegalRisk = {
  law: '정보통신망법',
  article: 'CWE-77,78',
  description: 'OS Command Injection',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌',
};

const FILE_UPLOAD_LEGAL: LegalRisk = {
  law: '정보통신망법',
  article: 'CWE-434',
  description: '위험한 파일 업로드',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌',
};

const DESERIALIZATION_LEGAL: LegalRisk = {
  law: '정보통신망법',
  article: 'CWE-502',
  description: '안전하지 않은 역직렬화',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌',
};

const SSRF_LEGAL: LegalRisk = {
  law: '개인정보보호법',
  article: '§29',
  description: 'Server Side Request Forgery',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌',
};

function environmentExpression(name: string, languageId: string): string | undefined {
  switch (languageId) {
    case 'python':
      return `os.environ["${name}"]`;
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      return `process.env.${name}`;
    case 'java':
      return `System.getenv("${name}")`;
    case 'go':
      return `os.Getenv("${name}")`;
    case 'php':
      return `getenv("${name}")`;
    case 'ruby':
      return `ENV.fetch("${name}")`;
    default:
      return undefined;
  }
}

function envVarFix(varName: string, languageId: string): FixSuggestion | undefined {
  const name = varName.toUpperCase();
  const expression = environmentExpression(name, languageId);
  if (!expression) return undefined;
  let replacement: string;
  switch (languageId) {
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      replacement = `const ${varName} = ${expression};`;
      break;
    case 'java':
      replacement = `String ${varName} = ${expression};`;
      break;
    case 'go':
      replacement = `${varName} := ${expression}`;
      break;
    case 'php':
      replacement = `$${varName} = ${expression};`;
      break;
    default:
      replacement = `${varName} = ${expression}`;
  }
  return {
    title: `환경변수 ${name}(으)로 교체`,
    replacement,
    replaceEntireLine: true,
  };
}

function apiKeyFix(languageId: string): FixSuggestion | undefined {
  const replacement = environmentExpression('OPENAI_API_KEY', languageId);
  if (!replacement) return undefined;
  return {
    title: 'API 키를 환경변수에서 로드',
    replacement,
    replaceEntireLine: false,
  };
}

function sqlBindingFix(languageId: string): FixSuggestion | undefined {
  switch (languageId) {
    case 'python':
      return {
        title: 'DB 드라이버 바인딩 파라미터 사용',
        replacement: 'cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))',
        replaceEntireLine: true,
      };
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      return {
        title: 'DB 드라이버 바인딩 파라미터 사용',
        replacement: 'await db.query("SELECT * FROM users WHERE id = ?", [userId]);',
        replaceEntireLine: true,
      };
    case 'java':
      return {
        title: 'PreparedStatement 사용',
        replacement: [
          'PreparedStatement stmt = connection.prepareStatement(',
          '    "SELECT * FROM users WHERE id = ?");',
          'stmt.setString(1, userId);',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'go':
      return {
        title: 'QueryRow 바인딩 인자 사용',
        replacement: 'row := db.QueryRow("SELECT * FROM users WHERE id = ?", userID)',
        replaceEntireLine: true,
      };
    case 'php':
      return {
        title: 'PDO prepared statement 사용',
        replacement: [
          '$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");',
          '$stmt->execute([$userId]);',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'ruby':
      return {
        title: 'ActiveRecord 조건 인자 사용',
        replacement: 'user = User.find_by(id: user_id)',
        replaceEntireLine: true,
      };
    default:
      return undefined;
  }
}

function safeEvalFix(languageId: string): FixSuggestion | undefined {
  switch (languageId) {
    case 'python':
      return {
        title: '리터럴 파서 사용',
        replacement: 'ast.literal_eval(',
        replaceEntireLine: false,
      };
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      return {
        title: 'JSON 파서 사용',
        replacement: 'JSON.parse(',
        replaceEntireLine: false,
      };
    case 'php':
      return {
        title: 'JSON 파서 사용',
        replacement: 'json_decode(',
        replaceEntireLine: false,
      };
    case 'ruby':
      return {
        title: 'JSON 파서 사용',
        replacement: 'JSON.parse(',
        replaceEntireLine: false,
      };
    default:
      return undefined;
  }
}

function passwordHashFix(languageId: string): FixSuggestion | undefined {
  switch (languageId) {
    case 'python':
      return {
        title: 'Argon2id 비밀번호 해시 사용',
        replacement: 'password_hash = PasswordHasher().hash(password)',
        replaceEntireLine: true,
      };
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      return {
        title: 'Argon2 비밀번호 해시 사용',
        replacement: 'const passwordHash = await argon2.hash(password);',
        replaceEntireLine: true,
      };
    case 'java':
      return {
        title: 'PasswordEncoder 사용',
        replacement: 'String passwordHash = passwordEncoder.encode(password);',
        replaceEntireLine: true,
      };
    case 'go':
      return {
        title: 'bcrypt 비밀번호 해시 사용',
        replacement: 'passwordHash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)',
        replaceEntireLine: true,
      };
    case 'php':
      return {
        title: 'Argon2id 비밀번호 해시 사용',
        replacement: '$passwordHash = password_hash($password, PASSWORD_ARGON2ID);',
        replaceEntireLine: true,
      };
    case 'ruby':
      return {
        title: 'bcrypt 비밀번호 해시 사용',
        replacement: 'password_hash = BCrypt::Password.create(password)',
        replaceEntireLine: true,
      };
    default:
      return undefined;
  }
}

function safeCommandFix(languageId: string): FixSuggestion | undefined {
  switch (languageId) {
    case 'python':
      return {
        title: '셸 없이 명령과 인자를 분리',
        replacement: 'subprocess.run(["command", str(argument)], shell=False, check=True)',
        replaceEntireLine: true,
      };
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      return {
        title: 'execFile로 명령과 인자를 분리',
        replacement: 'execFile("command", [String(argument)], callback);',
        replaceEntireLine: true,
      };
    case 'java':
      return {
        title: 'ProcessBuilder 인자 배열 사용',
        replacement: 'new ProcessBuilder("command", String.valueOf(argument)).start();',
        replaceEntireLine: true,
      };
    case 'go':
      return {
        title: 'exec.Command 인자 분리',
        replacement: 'cmd := exec.Command("command", fmt.Sprint(argument))',
        replaceEntireLine: true,
      };
    case 'php':
      return {
        title: '셸 없이 명령과 인자를 분리',
        replacement: '$process = proc_open(["command", (string) $argument], $descriptorSpec, $pipes);',
        replaceEntireLine: true,
      };
    case 'ruby':
      return {
        title: 'Open3 인자 분리',
        replacement: 'stdout, stderr, status = Open3.capture3("command", argument.to_s)',
        replaceEntireLine: true,
      };
    default:
      return undefined;
  }
}

function safeDeserializationFix(languageId: string): FixSuggestion | undefined {
  switch (languageId) {
    case 'python':
      return {
        title: 'JSON 역직렬화 사용',
        replacement: 'payload = json.loads(untrusted_data)',
        replaceEntireLine: true,
      };
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      return {
        title: 'JSON 역직렬화 사용',
        replacement: 'const payload = JSON.parse(untrustedData);',
        replaceEntireLine: true,
      };
    case 'java':
      return {
        title: '명시적 JSON 타입으로 역직렬화',
        replacement: 'Payload payload = objectMapper.readValue(untrustedData, Payload.class);',
        replaceEntireLine: true,
      };
    case 'go':
      return {
        title: 'JSON 역직렬화 사용',
        replacement: 'err := json.Unmarshal(untrustedData, &payload)',
        replaceEntireLine: true,
      };
    case 'php':
      return {
        title: 'JSON 역직렬화 사용',
        replacement: '$payload = json_decode($untrustedData, true, 512, JSON_THROW_ON_ERROR);',
        replaceEntireLine: true,
      };
    case 'ruby':
      return {
        title: 'JSON 역직렬화 사용',
        replacement: 'payload = JSON.parse(untrusted_data)',
        replaceEntireLine: true,
      };
    default:
      return undefined;
  }
}

function safeUploadFix(languageId: string): FixSuggestion | undefined {
  switch (languageId) {
    case 'python':
      return {
        title: '검증된 파일명으로 업로드 저장',
        replacement: [
          'safe_name = secure_filename(uploaded_file.filename)',
          'uploaded_file.save(Path(UPLOAD_DIR) / safe_name)',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      return {
        title: '기준 디렉터리에 안전한 파일명으로 저장',
        replacement: [
          'const safeName = path.basename(uploadedFile.originalname);',
          'await fs.promises.writeFile(path.join(uploadDir, safeName), uploadedFile.buffer);',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'java':
      return {
        title: '파일명에서 경로 요소를 제거해 저장',
        replacement: [
          'String safeName = Paths.get(file.getOriginalFilename()).getFileName().toString();',
          'file.transferTo(uploadDir.resolve(safeName));',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'go':
      return {
        title: '파일명에서 경로 요소를 제거해 저장',
        replacement: [
          'safeName := filepath.Base(fileHeader.Filename)',
          'destination := filepath.Join(uploadDir, safeName)',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'php':
      return {
        title: '파일명에서 경로 요소를 제거해 저장',
        replacement: [
          '$safeName = basename($_FILES["file"]["name"]);',
          'move_uploaded_file(',
          '    $_FILES["file"]["tmp_name"],',
          '    $uploadDir . DIRECTORY_SEPARATOR . $safeName',
          ');',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'ruby':
      return {
        title: '파일명에서 경로 요소를 제거해 저장',
        replacement: [
          'safe_name = File.basename(uploaded_file.original_filename)',
          'File.binwrite(File.join(upload_dir, safe_name), uploaded_file.read)',
        ].join('\n'),
        replaceEntireLine: true,
      };
    default:
      return undefined;
  }
}

function safePathFix(languageId: string): FixSuggestion | undefined {
  switch (languageId) {
    case 'python':
      return {
        title: '기준 디렉터리 내부 경로만 허용',
        replacement: [
          'base_dir = Path(DATA_DIR).resolve()',
          'safe_path = (base_dir / user_path).resolve()',
          'if base_dir not in safe_path.parents:',
          '    raise ValueError("invalid path")',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      return {
        title: '기준 디렉터리 내부 경로만 허용',
        replacement: [
          'const baseDir = path.resolve(DATA_DIR);',
          'const safePath = path.resolve(baseDir, userPath);',
          'if (!safePath.startsWith(`${baseDir}${path.sep}`)) throw new Error("invalid path");',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'java':
      return {
        title: '정규화 후 기준 디렉터리 내부인지 확인',
        replacement: [
          'Path baseDir = Paths.get(DATA_DIR).toAbsolutePath().normalize();',
          'Path safePath = baseDir.resolve(userPath).normalize();',
          'if (!safePath.startsWith(baseDir)) throw new SecurityException("invalid path");',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'go':
      return {
        title: '상대 경로가 기준 디렉터리를 벗어나지 않는지 확인',
        replacement: [
          'safePath := filepath.Join(dataDir, userPath)',
          'relative, err := filepath.Rel(dataDir, safePath)',
          'if err != nil || relative == ".." || strings.HasPrefix(relative, ".."+string(os.PathSeparator)) {',
          '    return errors.New("invalid path")',
          '}',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'php':
      return {
        title: '실제 경로가 기준 디렉터리 내부인지 확인',
        replacement: [
          '$baseDir = realpath($dataDir);',
          '$safePath = realpath($baseDir . DIRECTORY_SEPARATOR . $userPath);',
          'if ($safePath === false || !str_starts_with($safePath, $baseDir . DIRECTORY_SEPARATOR)) {',
          '    throw new RuntimeException("invalid path");',
          '}',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'ruby':
      return {
        title: '확장 경로가 기준 디렉터리 내부인지 확인',
        replacement: [
          'base_dir = File.expand_path(DATA_DIR)',
          'safe_path = File.expand_path(user_path, base_dir)',
          'raise "invalid path" unless safe_path.start_with?("#{base_dir}#{File::SEPARATOR}")',
        ].join('\n'),
        replaceEntireLine: true,
      };
    default:
      return undefined;
  }
}

function ssrfFix(languageId: string): FixSuggestion | undefined {
  switch (languageId) {
    case 'python':
      return {
        title: '허용된 HTTPS 호스트만 요청',
        replacement: [
          'target = urlparse(target_url)',
          'if target.scheme != "https" or target.hostname not in ALLOWED_HOSTS:',
          '    raise ValueError("untrusted URL")',
          'response = requests.get(target_url, timeout=10)',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'javascript':
    case 'typescript':
    case 'javascriptreact':
    case 'typescriptreact':
      return {
        title: '허용된 HTTPS 호스트만 요청',
        replacement: [
          'const target = new URL(targetUrl);',
          'if (target.protocol !== "https:" || !ALLOWED_HOSTS.has(target.hostname)) {',
          '  throw new Error("untrusted URL");',
          '}',
          'const response = await fetch(target, { signal: AbortSignal.timeout(10_000) });',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'java':
      return {
        title: '허용된 HTTPS 호스트만 요청',
        replacement: [
          'URI target = URI.create(targetUrl);',
          'if (!"https".equals(target.getScheme()) || !allowedHosts.contains(target.getHost())) {',
          '    throw new IllegalArgumentException("untrusted URL");',
          '}',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'go':
      return {
        title: '허용된 HTTPS 호스트만 요청',
        replacement: [
          'target, err := url.Parse(targetURL)',
          'if err != nil || target.Scheme != "https" || !allowedHosts[target.Hostname()] {',
          '    return errors.New("untrusted URL")',
          '}',
          'client := &http.Client{Timeout: 10 * time.Second}',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'php':
      return {
        title: '허용된 HTTPS 호스트만 요청',
        replacement: [
          '$target = parse_url($targetUrl);',
          'if (($target["scheme"] ?? "") !== "https" || !in_array($target["host"] ?? "", $allowedHosts, true)) {',
          '    throw new InvalidArgumentException("untrusted URL");',
          '}',
        ].join('\n'),
        replaceEntireLine: true,
      };
    case 'ruby':
      return {
        title: '허용된 HTTPS 호스트만 요청',
        replacement: [
          'target = URI.parse(target_url)',
          'raise "untrusted URL" unless target.scheme == "https" && ALLOWED_HOSTS.include?(target.host)',
          'response = Net::HTTP.get_response(target)',
        ].join('\n'),
        replaceEntireLine: true,
      };
    default:
      return undefined;
  }
}

function personalInfoFix(languageId: string): FixSuggestion | undefined {
  return envVarFix('email', languageId);
}

const RULES: Rule[] = [
  {
    id: 'hardcoded-password',
    cwe: 'CWE-798',
    pattern: /(password|passwd|pwd|secret|db_password)\s*=\s*["'][^"']{4,}["']/gi,
    severity: 'error',
    category: 'secret',
    message: '하드코딩 비밀번호 — 개인정보보호법 §29',
    detail: '환경변수(.env) 또는 Secrets Manager 사용 권장',
    legal: PIPA_29,
    makeFix: (match, lang) => {
      const varName = match.split('=')[0].trim();
      return envVarFix(varName, lang);
    },
  },
  {
    id: 'exposed-api-key',
    cwe: 'CWE-798',
    pattern: /(["']?)(sk-[a-zA-Z0-9_-]{8,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,})\1/g,
    severity: 'error',
    category: 'cost',
    message: 'API 키 노출 — 과금 위험',
    detail: 'Git 푸시 시 무단 과금 발생 가능. 즉시 키 재발급 필요',
    makeFix: (_match, lang) => apiKeyFix(lang),
  },
  {
    id: 'sql-injection',
    cwe: 'CWE-89',
    pattern: /["'].*?\b(SELECT|INSERT|UPDATE|DELETE)\b.*?["']\s*\+/gi,
    severity: 'warning',
    category: 'injection',
    message: 'SQL Injection 위험',
    detail: 'parameterized query 또는 ORM 사용 필요',
    makeFix: (_match, lang) => sqlBindingFix(lang),
  },
  {
    id: 'weak-hash',
    cwe: 'CWE-327',
    pattern: /\b(md5|sha1)\s*\(/gi,
    severity: 'warning',
    category: 'crypto',
    message: '취약한 해시 알고리즘 (비밀번호 해싱 부적합)',
    detail: 'bcrypt, scrypt, argon2 사용 권장',
    makeFix: (_match, lang) => passwordHashFix(lang),
  },
  {
    id: 'dangerous-eval',
    cwe: 'CWE-94',
    pattern: /\beval\s*\(/g,
    severity: 'warning',
    category: 'injection',
    message: 'eval() 사용 — 코드 주입 위험',
    detail: '사용자 입력이 eval에 전달되면 원격 코드 실행 가능',
    makeFix: (_match, lang) => safeEvalFix(lang),
  },
  {
    id: 'debug-mode',
    cwe: 'CWE-209',
    pattern: /\bdebug\s*=\s*True\b/g,
    severity: 'info',
    category: 'other',
    message: '디버그 모드 활성화',
    detail: '운영 배포 시 내부 정보 노출 위험',
    makeFix: () => ({
      title: '디버그 모드 비활성화 (False)',
      replacement: 'debug = False',
      replaceEntireLine: false,
    }),
  },
  {
  id: 'dangerous-file-upload',
  cwe: 'CWE-434',
  pattern: /\b(move_uploaded_file|MultipartFile|IFormFile|multer|upload)\b/g,
  severity: 'warning',
  category: 'other',
  message: '위험한 파일 업로드 가능성',
  detail: '확장자, MIME Type, 파일명을 검증하세요.',
  legal: FILE_UPLOAD_LEGAL,
  makeFix: (_match, lang) => safeUploadFix(lang),
  },
  {
  id: 'hardcoded-credential',
  cwe: 'CWE-798',
  pattern: /\b(api[_-]?key|token|access[_-]?key|secret[_-]?key)\s*=\s*["'][^"']+["']/gi,
  severity: 'error',
  category: 'secret',
  message: '하드코딩된 자격증명',
  detail: '환경변수 또는 Secret Manager 사용 권장',
  legal: PIPA_29,
  makeFix: (match, lang) => envVarFix(match.split('=')[0].trim(), lang),
  },
  {
  id: 'path-traversal',
  cwe: 'CWE-22',
  pattern: /\.\.\//g,
  severity: 'warning',
  category: 'injection',
  message: 'Path Traversal 가능성',
  detail: '사용자 입력으로 경로를 생성하지 마세요.',
  legal: {
    law: '정보통신망법',
    article: 'CWE-22',
    description: '경로 탐색',
    liability: 2,
    sanction: 2,
    sanctionType: '형사처벌',
  },
  makeFix: (_match, lang) => safePathFix(lang),
  },
  {
  id: 'os-command-injection',
  cwe: 'CWE-77, CWE-78',
  pattern: /\b(exec|system|Runtime\.getRuntime\(\)|subprocess\.Popen|os\.system)\b/g,
  severity: 'error',
  category: 'injection',
  message: 'OS Command Injection 위험',
  detail: '쉘 명령에 사용자 입력을 전달하지 마세요.',
  legal: COMMAND_INJECTION_LEGAL,
  makeFix: (_match, lang) => safeCommandFix(lang),
  },
  {
  id: 'unsafe-deserialization',
  cwe: 'CWE-502',
  pattern: /\b(pickle\.loads|ObjectInputStream|BinaryFormatter|deserialize)\b/g,
  severity: 'error',
  category: 'other',
  message: '안전하지 않은 역직렬화',
  detail: '신뢰할 수 없는 데이터를 역직렬화하지 마세요.',
  legal: DESERIALIZATION_LEGAL,
  makeFix: (_match, lang) => safeDeserializationFix(lang),
  },
  {
  id: 'ssrf',
  cwe: 'CWE-918',
  pattern: /\b(requests\.get|axios\.get|fetch|http\.get|urllib\.request)\b/g,
  severity: 'warning',
  category: 'injection',
  message: 'SSRF 가능성',
  detail: '사용자 입력 URL을 직접 요청하지 마세요.',
  legal: SSRF_LEGAL,
  makeFix: (_match, lang) => ssrfFix(lang),
  },
  {
  id: 'personal-info',
  cwe: 'CWE-200, CWE-359',
  pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
  severity: 'warning',
  category: 'secret',
  message: '개인정보(이메일) 노출',
  detail: '소스코드에 개인정보를 저장하지 마세요.',
  legal: PIPA_29,
  makeFix: (_match, lang) => personalInfoFix(lang),
  },
];

export class RuleEngineAnalyzer implements Analyzer {
  readonly kind = 'rules' as const;

  async analyze(text: string, fileName: string, languageId: string): Promise<AnalysisResult> {
    const findings: Finding[] = [];
    const lines = text.split(/\r?\n/);

    lines.forEach((lineText, lineIdx) => {
      for (const rule of RULES) {
        rule.pattern.lastIndex = 0; // g 플래그 정규식 상태 초기화
        let m: RegExpExecArray | null;
        while ((m = rule.pattern.exec(lineText)) !== null) {
          findings.push({
            ruleId: rule.id,
            cwe: rule.cwe,
            message: rule.message,
            detail: rule.detail,
            severity: rule.severity,
            category: rule.category,
            line: lineIdx,
            startCol: m.index,
            endCol: m.index + m[0].length,
            legal: rule.legal,
            fix: rule.makeFix?.(m[0], languageId),
          });
        }
      }
    });

    return {
      fileName,
      languageId,
      riskScore: computeRiskScore(findings),
      findings,
      engine: 'rules',
      analyzedAt: new Date().toISOString(),
    };
  }
}
