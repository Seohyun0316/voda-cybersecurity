import base64
import binascii
import codecs
import hashlib
import json
import math
import multiprocessing
import os
import re
import sys
import time
import traceback
import uuid
from collections import Counter, deque
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence
from urllib.parse import quote, urlparse

import requests
import tomllib  # Python 3.11+

GITHUB_API_BASE = "https://api.github.com"
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR
RULE_FILE = SCRIPT_DIR / "ruleset.toml"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_PREFIX = "repo_scan"

DEFAULT_REQUEST_DELAY_SECONDS = 0.1
DEFAULT_MAX_FILE_BYTES = 1_000_000
DEFAULT_GITHUB_MAX_RETRIES = 3
DEFAULT_GITHUB_RETRY_BACKOFF_SECONDS = 1.0
DEFAULT_GITHUB_MAX_RATE_LIMIT_WAIT_SECONDS = 60.0
DEFAULT_REGEX_SCAN_TIMEOUT_SECONDS = 15.0
MIN_REGEX_WORKER_STARTUP_TIMEOUT_SECONDS = 5.0

SCANNABLE_EXTENSIONS = {".js", ".py"}

# Names must begin with a letter or underscore so regex quantifiers such as
# {6,10} are not mistaken for keyword placeholders.
KEYWORD_PLACEHOLDER_PATTERN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

# A repeated ``newline + indentation`` alternative can backtrack by assigning
# the same spaces either to ``[ \t]+`` or to the next generic-character
# iteration. Making each unit atomic preserves the accepted text while
# preventing exponential repartitioning of indentation.
AMBIGUOUS_INDENTED_MULTILINE_FRAGMENT = r"(?:[^;\r\n]|\r?\n[ \t]+)"
ATOMIC_INDENTED_MULTILINE_FRAGMENT = r"(?>(?:[^;\r\n]|\r?\n[ \t]+))"

LIKELY_BINARY_EXTENSIONS = {
    ".7z",
    ".avif",
    ".bmp",
    ".bz2",
    ".class",
    ".dll",
    ".doc",
    ".docx",
    ".eot",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jar",
    ".jpeg",
    ".jpg",
    ".lockb",
    ".mp3",
    ".mp4",
    ".otf",
    ".pdf",
    ".png",
    ".pyc",
    ".rar",
    ".so",
    ".sqlite",
    ".ttf",
    ".wasm",
    ".webp",
    ".woff",
    ".woff2",
    ".zip",
}


class GitHubRequestError(RuntimeError):
    """A classified GitHub API failure safe to expose in scan metadata."""

    def __init__(
        self,
        message: str,
        *,
        category: str,
        url: str,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.url = url
        self.status_code = status_code


class GitHubAuthenticationError(GitHubRequestError):
    pass


class GitHubRateLimitError(GitHubRequestError):
    pass


class GitHubPermissionError(GitHubRequestError):
    pass


class RegexScanTimeoutError(RuntimeError):
    pass


class RegexScanWorkerError(RuntimeError):
    pass


def env_float(
    name: str,
    default: float,
    *,
    minimum: float = 0.0,
) -> float:
    value = os.getenv(name)
    if not value:
        return default

    try:
        parsed = float(value)
    except ValueError:
        print(f"[WARN] Invalid float for {name}={value!r}; using {default}")
        return default

    if not math.isfinite(parsed) or parsed < minimum:
        print(
            f"[WARN] {name} must be a finite number >= {minimum}; " f"using {default}"
        )
        return default

    return parsed


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default

    try:
        parsed = int(value)
    except ValueError:
        print(f"[WARN] Invalid integer for {name}={value!r}; using {default}")
        return default

    return max(parsed, 1)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_warning(warnings: List[str] | None, message: str) -> None:
    """Record and immediately surface a warning without duplicating it."""
    if warnings is not None and message not in warnings:
        warnings.append(message)
    print(f"[WARN] {message}")


def load_rule_set(rule_path: Path) -> Dict[str, Any]:
    with open(rule_path, "rb") as f:
        rule_set = tomllib.load(f)

    if not isinstance(rule_set, dict):
        raise ValueError("Rule file must contain a TOML table at its root.")
    return rule_set


def hash_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(64 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_nonempty_string_list(
    value: Any,
    field_name: str,
    *,
    allow_empty: bool = False,
) -> List[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    if not value and not allow_empty:
        raise ValueError(f"{field_name} must not be empty.")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{field_name} must contain only non-empty strings.")
    return value


def build_keyword_patterns(
    keyword_sets: Dict[str, List[str]],
) -> Dict[str, str]:
    """Convert each TOML keyword set into a reusable regex alternation."""
    if not isinstance(keyword_sets, dict):
        raise ValueError("keyword_sets must be a TOML table.")

    patterns = {}

    for name, keywords in keyword_sets.items():
        if not isinstance(name, str) or not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*", name
        ):
            raise ValueError(f"Invalid keyword set name: {name!r}.")

        validate_nonempty_string_list(keywords, f"Keyword set {name!r}")

        fragments = []
        for keyword in keywords:
            fragment = f"(?:{keyword})"
            try:
                re.compile(fragment)
            except re.error as exc:
                raise ValueError(
                    f"Keyword set {name!r} contains invalid regex {keyword!r}: {exc}"
                ) from exc
            fragments.append(fragment)
        if not fragments:
            raise ValueError(f"Keyword set {name!r} must not be empty.")

        patterns[name] = "|".join(fragments)

    return patterns


def expand_keyword_placeholders(
    raw_regex: str,
    keyword_patterns: Dict[str, str],
    rule_id: str,
) -> tuple[str, List[str]]:
    """Expand named keyword placeholders and report which sets a rule uses."""
    used_sets = []

    def replace(match: re.Match[str]) -> str:
        set_name = match.group(1)
        if set_name not in keyword_patterns:
            raise ValueError(f"Unknown keyword set {set_name!r} in rule {rule_id!r}.")

        if set_name not in used_sets:
            used_sets.append(set_name)

        return keyword_patterns[set_name]

    return KEYWORD_PLACEHOLDER_PATTERN.sub(replace, raw_regex), used_sets


def stabilize_regex(expanded_regex: str) -> str:
    """Replace known equivalent-but-pathological regex fragments."""
    return expanded_regex.replace(
        AMBIGUOUS_INDENTED_MULTILINE_FRAGMENT,
        ATOMIC_INDENTED_MULTILINE_FRAGMENT,
    )


def prepare_rules(rule_set: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate, expand, and compile every rule once before repository scanning."""
    title = rule_set.get("title")
    version = rule_set.get("version")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Rule set title must be a non-empty string.")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Rule set version must be a non-empty string.")

    raw_keyword_sets = rule_set.get("keyword_sets", {})
    keyword_patterns = build_keyword_patterns(raw_keyword_sets)
    raw_rules = rule_set.get("rules")
    if not isinstance(raw_rules, list) or not raw_rules:
        raise ValueError("Rule set must contain at least one [[rules]] entry.")

    prepared_rules = []
    seen_rule_ids = set()
    required_fields = {
        "id",
        "name",
        "desc",
        "owasp",
        "cwe",
        "severity",
        "allowlist",
        "regex",
    }

    for rule_index, raw_rule in enumerate(raw_rules, start=1):
        if not isinstance(raw_rule, dict):
            raise ValueError(f"Rule #{rule_index} must be a TOML table.")

        missing_fields = sorted(required_fields.difference(raw_rule))
        if missing_fields:
            raise ValueError(
                f"Rule #{rule_index} is missing required fields: "
                f"{', '.join(missing_fields)}"
            )

        rule = dict(raw_rule)
        rule_id = rule["id"]
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise ValueError(f"Rule #{rule_index} has an invalid id.")
        if rule_id in seen_rule_ids:
            raise ValueError(f"Duplicate rule id: {rule_id!r}.")
        seen_rule_ids.add(rule_id)

        for field_name in ("name", "desc", "severity"):
            value = rule[field_name]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Rule {rule_id!r} field {field_name!r} "
                    "must be a non-empty string."
                )

        validate_nonempty_string_list(rule["owasp"], f"Rule {rule_id!r} owasp")
        validate_nonempty_string_list(rule["cwe"], f"Rule {rule_id!r} cwe")
        allowlist = validate_nonempty_string_list(
            rule["allowlist"],
            f"Rule {rule_id!r} allowlist",
            allow_empty=True,
        )
        path_allowlist = validate_nonempty_string_list(
            rule.get("path_allowlist", []),
            f"Rule {rule_id!r} path_allowlist",
            allow_empty=True,
        )

        if rule["severity"] not in {"low", "medium", "high", "critical"}:
            raise ValueError(
                f"Rule {rule_id!r} has unsupported severity " f"{rule['severity']!r}."
            )

        raw_regex = rule["regex"]
        if not isinstance(raw_regex, str) or not raw_regex.strip():
            raise ValueError(f"Rule {rule_id!r} regex must be a non-empty string.")

        try:
            expanded_regex, used_sets = expand_keyword_placeholders(
                raw_regex,
                keyword_patterns,
                rule_id,
            )
            expanded_regex = stabilize_regex(expanded_regex)
            compiled_pattern = re.compile(expanded_regex, re.MULTILINE)
            compiled_allowlist = [
                re.compile(pattern, re.MULTILINE) for pattern in allowlist
            ]
            compiled_path_allowlist = [
                re.compile(pattern, re.MULTILINE) for pattern in path_allowlist
            ]
        except (ValueError, re.error) as exc:
            raise ValueError(f"Invalid rule {rule_id!r}: {exc}") from exc

        if compiled_pattern.search("") is not None:
            raise ValueError(f"Rule {rule_id!r} regex must not match empty text.")
        if any(pattern.search("") is not None for pattern in compiled_allowlist):
            raise ValueError(f"Rule {rule_id!r} allowlist must not match empty text.")
        if any(pattern.search("") is not None for pattern in compiled_path_allowlist):
            raise ValueError(
                f"Rule {rule_id!r} path_allowlist must not match empty text."
            )

        behavior_definition = {
            "rule": raw_rule,
            "expanded_regex": expanded_regex,
            "referenced_keyword_sets": {
                name: raw_keyword_sets[name] for name in used_sets
            },
        }
        definition_json = json.dumps(
            behavior_definition,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

        rule["_pattern"] = compiled_pattern
        rule["_allowlist_patterns"] = compiled_allowlist
        rule["_path_allowlist_patterns"] = compiled_path_allowlist
        rule["_expanded_regex"] = expanded_regex
        rule["_keyword_sets"] = used_sets
        rule["_definition_hash"] = hash_text(definition_json)
        prepared_rules.append(rule)

    return prepared_rules


def build_headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "VibeSafe-Research-Crawler",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def _response_message(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return (response.text or "").strip()[:300]

    if isinstance(payload, dict) and isinstance(payload.get("message"), str):
        return payload["message"][:300]
    return ""


def _retry_after_seconds(response: requests.Response) -> float | None:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(float(retry_after), 0.0)
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(retry_after)
                if retry_at.tzinfo is None:
                    retry_at = retry_at.replace(tzinfo=timezone.utc)
                return max((retry_at - datetime.now(timezone.utc)).total_seconds(), 0.0)
            except (TypeError, ValueError, OverflowError):
                pass

    reset_at = response.headers.get("X-RateLimit-Reset")
    if reset_at:
        try:
            return max(float(reset_at) - time.time(), 0.0)
        except ValueError:
            pass

    return None


def _is_rate_limited(response: requests.Response, message: str) -> bool:
    if response.status_code == 429:
        return True
    if response.status_code != 403:
        return False

    lowered_message = message.lower()
    return (
        response.headers.get("X-RateLimit-Remaining") == "0"
        or "rate limit" in lowered_message
        or "secondary rate" in lowered_message
        or "abuse detection" in lowered_message
        or "Retry-After" in response.headers
    )


def github_get(
    url: str,
    headers: Dict[str, str],
    params: Dict[str, Any] | None = None,
    *,
    session: requests.Session | None = None,
    warnings: List[str] | None = None,
    max_retries: int | None = None,
    retry_backoff_seconds: float | None = None,
    max_rate_limit_wait_seconds: float | None = None,
) -> Dict[str, Any]:
    """Fetch one JSON object with classified, bounded retry behavior."""
    if max_retries is None:
        max_retries = env_int("GITHUB_MAX_RETRIES", DEFAULT_GITHUB_MAX_RETRIES)
    if retry_backoff_seconds is None:
        retry_backoff_seconds = env_float(
            "GITHUB_RETRY_BACKOFF_SECONDS",
            DEFAULT_GITHUB_RETRY_BACKOFF_SECONDS,
        )
    if max_rate_limit_wait_seconds is None:
        max_rate_limit_wait_seconds = env_float(
            "GITHUB_MAX_RATE_LIMIT_WAIT_SECONDS",
            DEFAULT_GITHUB_MAX_RATE_LIMIT_WAIT_SECONDS,
        )

    requester = session.get if session is not None else requests.get
    total_attempts = max_retries + 1

    for attempt in range(1, total_attempts + 1):
        try:
            response = requester(
                url,
                headers=headers,
                params=params,
                timeout=(10, 30),
            )
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt < total_attempts:
                delay = retry_backoff_seconds * (2 ** (attempt - 1))
                append_warning(
                    warnings,
                    f"GitHub request failed temporarily; retrying in {delay:.1f}s "
                    f"(attempt {attempt}/{total_attempts}): {url}",
                )
                if delay:
                    time.sleep(delay)
                continue
            raise GitHubRequestError(
                f"GitHub network request failed after {total_attempts} attempts: "
                f"{type(exc).__name__}",
                category="network",
                url=url,
            ) from exc
        except requests.RequestException as exc:
            raise GitHubRequestError(
                f"GitHub request could not be sent: {type(exc).__name__}",
                category="network",
                url=url,
            ) from exc

        status_code = response.status_code
        message = _response_message(response)

        if status_code == 401:
            raise GitHubAuthenticationError(
                "GitHub token is missing, expired, or invalid.",
                category="authentication",
                url=url,
                status_code=status_code,
            )

        if _is_rate_limited(response, message):
            wait_seconds = _retry_after_seconds(response)
            if wait_seconds is None:
                wait_seconds = retry_backoff_seconds * (2 ** (attempt - 1))

            if attempt < total_attempts and wait_seconds <= max_rate_limit_wait_seconds:
                append_warning(
                    warnings,
                    f"GitHub rate limit reached; retrying in {wait_seconds:.1f}s "
                    f"(attempt {attempt}/{total_attempts}).",
                )
                if wait_seconds:
                    time.sleep(wait_seconds)
                continue

            reset_detail = (
                f" Required wait: {wait_seconds:.1f}s."
                if wait_seconds is not None
                else ""
            )
            raise GitHubRateLimitError(
                "GitHub API rate limit prevented the request." f"{reset_detail}",
                category="rate_limit",
                url=url,
                status_code=status_code,
            )

        if status_code == 403:
            raise GitHubPermissionError(
                f"GitHub denied access to the requested resource: "
                f"{message or 'permission denied'}",
                category="permission",
                url=url,
                status_code=status_code,
            )

        if status_code >= 500:
            if attempt < total_attempts:
                delay = retry_backoff_seconds * (2 ** (attempt - 1))
                append_warning(
                    warnings,
                    f"GitHub returned HTTP {status_code}; retrying in {delay:.1f}s "
                    f"(attempt {attempt}/{total_attempts}).",
                )
                if delay:
                    time.sleep(delay)
                continue
            raise GitHubRequestError(
                f"GitHub returned HTTP {status_code} after {total_attempts} attempts.",
                category="server",
                url=url,
                status_code=status_code,
            )

        if status_code >= 400:
            category = "not_found" if status_code == 404 else "http"
            raise GitHubRequestError(
                f"GitHub returned HTTP {status_code}: "
                f"{message or 'request failed'}",
                category=category,
                url=url,
                status_code=status_code,
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise GitHubRequestError(
                "GitHub returned a non-JSON response.",
                category="invalid_response",
                url=url,
                status_code=status_code,
            ) from exc

        if not isinstance(data, dict):
            raise GitHubRequestError(
                "GitHub returned JSON with an unexpected top-level type.",
                category="invalid_response",
                url=url,
                status_code=status_code,
            )
        return data

    raise AssertionError("unreachable")


def parse_github_repo(repo_input: str) -> Dict[str, str]:
    value = repo_input.strip()
    value = re.sub(r"\.git$", "", value)

    shorthand_match = re.fullmatch(r"([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", value)
    if shorthand_match:
        owner, repo = shorthand_match.groups()
        return {"owner": owner, "repo": repo, "input": repo_input}

    ssh_match = re.fullmatch(
        r"(?:git@|ssh://git@)github\.com[:/]([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
        value,
    )
    if ssh_match:
        owner, repo = ssh_match.groups()
        return {"owner": owner, "repo": repo, "input": repo_input}

    parsed = urlparse(value)
    host = parsed.netloc.lower()
    if host not in {"github.com", "www.github.com"}:
        raise ValueError("Only GitHub repository URLs are supported.")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("GitHub URL must include owner and repository name.")

    owner, repo = parts[0], re.sub(r"\.git$", "", parts[1])
    return {"owner": owner, "repo": repo, "input": repo_input}


def get_repository_metadata(
    owner: str,
    repo: str,
    headers: Dict[str, str],
    *,
    session: requests.Session | None = None,
    warnings: List[str] | None = None,
) -> Dict[str, Any]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    return github_get(url, headers=headers, session=session, warnings=warnings)


def get_repository_snapshot(
    owner: str,
    repo: str,
    branch: str,
    headers: Dict[str, str],
    *,
    session: requests.Session | None = None,
    warnings: List[str] | None = None,
) -> tuple[str, str]:
    """Resolve a mutable branch name to an immutable commit and root tree."""
    escaped_branch = quote(branch, safe="")
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits/{escaped_branch}"
    data = github_get(url, headers=headers, session=session, warnings=warnings)
    commit_sha = data.get("sha")
    commit_data = data.get("commit")
    tree_data = commit_data.get("tree") if isinstance(commit_data, dict) else None
    tree_sha = tree_data.get("sha") if isinstance(tree_data, dict) else None

    if not isinstance(commit_sha, str) or not commit_sha:
        raise GitHubRequestError(
            "GitHub commit response did not contain a commit SHA.",
            category="invalid_response",
            url=url,
        )
    if not isinstance(tree_sha, str) or not tree_sha:
        raise GitHubRequestError(
            "GitHub commit response did not contain a root tree SHA.",
            category="invalid_response",
            url=url,
        )

    return commit_sha, tree_sha


def get_repository_files(
    owner: str,
    repo: str,
    tree_sha: str,
    headers: Dict[str, str],
    *,
    session: requests.Session | None = None,
    warnings: List[str] | None = None,
) -> tuple[List[Dict[str, Any]], bool, bool]:
    """List blobs and recover a truncated recursive response tree-by-tree.

    Returns ``(files, tree_complete, recursive_tree_was_truncated)``.
    """
    root_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{tree_sha}"
    data = github_get(
        root_url,
        headers=headers,
        params={"recursive": "1"},
        session=session,
        warnings=warnings,
    )

    root_entries = data.get("tree")
    if not isinstance(root_entries, list):
        raise GitHubRequestError(
            "GitHub tree response did not contain a valid entry list.",
            category="invalid_response",
            url=root_url,
        )

    if not data.get("truncated"):
        files = []
        for item in root_entries:
            if not isinstance(item, dict):
                raise GitHubRequestError(
                    "GitHub tree response contained a non-object entry.",
                    category="invalid_response",
                    url=root_url,
                )
            if item.get("type") == "blob" and item.get("path"):
                files.append(item)
        return files, True, False

    append_warning(
        warnings,
        "GitHub truncated the recursive tree response; recovering files by "
        "walking each subtree.",
    )
    files: List[Dict[str, Any]] = []
    pending_trees = deque([(tree_sha, "")])
    tree_complete = True

    while pending_trees:
        current_sha, path_prefix = pending_trees.popleft()
        tree_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{current_sha}"
        try:
            tree_data = github_get(
                tree_url,
                headers=headers,
                session=session,
                warnings=warnings,
            )
        except (GitHubAuthenticationError, GitHubRateLimitError):
            raise
        except GitHubRequestError as exc:
            tree_complete = False
            append_warning(
                warnings,
                f"Could not recover subtree {current_sha} at "
                f"{path_prefix or '/'}: {exc}",
            )
            continue

        if tree_data.get("truncated"):
            tree_complete = False
            append_warning(
                warnings,
                f"GitHub also truncated non-recursive subtree {current_sha} at "
                f"{path_prefix or '/'}; that directory is incomplete.",
            )

        entries = tree_data.get("tree", [])
        if not isinstance(entries, list):
            tree_complete = False
            append_warning(
                warnings,
                f"GitHub returned an invalid entry list for subtree {current_sha}.",
            )
            continue

        for item in entries:
            if not isinstance(item, dict) or not item.get("path"):
                tree_complete = False
                continue

            relative_path = item["path"]
            full_path = (
                f"{path_prefix}/{relative_path}" if path_prefix else relative_path
            )
            item_type = item.get("type")

            if item_type == "blob":
                normalized_item = dict(item)
                normalized_item["path"] = full_path
                files.append(normalized_item)
            elif item_type == "tree" and isinstance(item.get("sha"), str):
                pending_trees.append((item["sha"], full_path))

    # A malformed tree can repeat an entry. Keep deterministic path/SHA pairs.
    unique_files = {}
    for item in files:
        unique_files[(item.get("path"), item.get("sha"))] = item
    return list(unique_files.values()), tree_complete, True


def is_probably_binary_path(path: str) -> bool:
    return Path(path.lower()).suffix in LIKELY_BINARY_EXTENSIONS


def is_scannable_path(path: str) -> bool:
    return Path(path.lower()).suffix in SCANNABLE_EXTENSIONS


def decode_blob_text(raw: bytes) -> tuple[str | None, str | None]:
    """Decode UTF text strictly, recognizing UTF-8/16/32 byte-order marks."""
    if raw.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
        encoding = "utf-32"
    elif raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        encoding = "utf-16"
    elif raw.startswith(codecs.BOM_UTF8):
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"

    try:
        text = raw.decode(encoding, errors="strict")
    except UnicodeDecodeError:
        return (
            None,
            "unsupported text encoding (expected UTF-8 or BOM-marked UTF-16/UTF-32)",
        )

    if "\x00" in text:
        return None, "binary content (NUL byte)"

    if text:
        control_count = sum(
            1
            for character in text
            if ord(character) < 32 and character not in "\n\r\t\f"
        )
        if control_count / len(text) > 0.05:
            return None, "binary content (control characters)"

    return text, None


def fetch_blob_content(
    blob_url: str,
    headers: Dict[str, str],
    max_file_bytes: int,
    *,
    expected_blob_sha: str | None = None,
    session: requests.Session | None = None,
    warnings: List[str] | None = None,
) -> tuple[str | None, str | None]:
    data = github_get(
        blob_url,
        headers=headers,
        session=session,
        warnings=warnings,
    )
    size = data.get("size")

    if isinstance(size, int) and size > max_file_bytes:
        return None, f"file too large ({size} bytes)"

    returned_sha = data.get("sha")
    if expected_blob_sha and returned_sha != expected_blob_sha:
        raise GitHubRequestError(
            "GitHub blob SHA did not match the repository tree.",
            category="invalid_response",
            url=blob_url,
        )

    if data.get("encoding") != "base64":
        raise GitHubRequestError(
            f"GitHub returned unsupported blob encoding: {data.get('encoding')!r}",
            category="invalid_response",
            url=blob_url,
        )

    encoded_content = data.get("content")
    if not isinstance(encoded_content, str):
        raise GitHubRequestError(
            "GitHub blob response did not contain base64 text.",
            category="invalid_response",
            url=blob_url,
        )

    try:
        compact_content = "".join(encoded_content.split()).encode("ascii")
        raw = base64.b64decode(compact_content, validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
        raise GitHubRequestError(
            "GitHub blob response contained invalid base64 data.",
            category="invalid_response",
            url=blob_url,
        ) from exc

    if len(raw) > max_file_bytes:
        return None, f"file too large after decoding ({len(raw)} bytes)"

    return decode_blob_text(raw)


def mask_match(text: str) -> str:
    if len(text) <= 4:
        return "*" * len(text)

    return text[:2] + "*" * (len(text) - 4) + text[-2:]


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def line_preview_for_match(
    content: str,
    start_index: int,
    end_index: int,
    max_chars: int = 200,
) -> str:
    """Return one line centered around the match, truncating distant context."""
    line_start = content.rfind("\n", 0, start_index) + 1
    line_end = content.find("\n", start_index)

    if line_end == -1:
        line_end = len(content)

    line = content[line_start:line_end]
    if len(line) <= max_chars:
        return line.strip()

    relative_start = start_index - line_start
    relative_end = min(end_index - line_start, len(line))
    match_length = max(relative_end - relative_start, 1)
    window_capacity = max(max_chars - 6, 1)

    if match_length >= window_capacity:
        window_start = relative_start
    else:
        context_before = (window_capacity - match_length) // 2
        window_start = max(relative_start - context_before, 0)

    window_end = min(window_start + window_capacity, len(line))
    if window_end - window_start < window_capacity:
        window_start = max(window_end - window_capacity, 0)

    prefix = "..." if window_start > 0 else ""
    suffix = "..." if window_end < len(line) else ""
    return f"{prefix}{line[window_start:window_end]}{suffix}"[:max_chars]


def is_rule_path_allowlisted(path: str, rule: Dict[str, Any]) -> bool:
    """Return whether a rule explicitly excludes this repository-relative path."""
    patterns = rule.get("_path_allowlist_patterns")
    if patterns is None:
        patterns = [
            re.compile(pattern, re.MULTILINE)
            for pattern in rule.get("path_allowlist", [])
        ]
    return any(pattern.search(path) for pattern in patterns)


def scan_content(
    content: str,
    rule: Dict[str, Any],
    file_path: str | None = None,
) -> List[Dict[str, Any]]:
    if file_path is not None and is_rule_path_allowlisted(file_path, rule):
        return []

    pattern = rule.get("_pattern")
    if pattern is None:
        pattern = re.compile(rule["regex"], re.MULTILINE)
    allowlist_patterns = rule.get("_allowlist_patterns", [])

    findings = []

    for match in pattern.finditer(content):
        if match.start() == match.end():
            continue

        matched_text = match.group(0)
        # Rule-local allowlists inspect only the exact match, never its path or line.
        if any(pattern.search(matched_text) for pattern in allowlist_patterns):
            continue

        start_offset = match.start()
        end_offset = match.end()
        line_no = content.count("\n", 0, start_offset) + 1
        line_start = content.rfind("\n", 0, start_offset) + 1
        column_no = start_offset - line_start + 1
        end_line_no = content.count("\n", 0, end_offset) + 1
        end_line_start = content.rfind("\n", 0, end_offset) + 1
        end_column_no = end_offset - end_line_start + 1

        findings.append(
            {
                "line": line_no,
                "column": column_no,
                "end_line": end_line_no,
                "end_column": end_column_no,
                "start_offset": start_offset,
                "end_offset": end_offset,
                "match_masked": mask_match(matched_text),
                "match_hash": hash_text(matched_text),
                "line_preview": line_preview_for_match(
                    content,
                    match.start(),
                    match.end(),
                ),
            }
        )

    return findings


def _scan_file_worker(
    content: str,
    file_path: str | None,
    rule_specs: Sequence[Dict[str, Any]],
    send_connection: Any,
) -> None:
    """Child-process entrypoint used to contain pathological regex behavior."""
    try:
        for spec in rule_specs:
            rule_id = spec["id"]
            send_connection.send(("rule_started", rule_id))
            try:
                worker_rule = {
                    "regex": spec["regex"],
                    "_pattern": re.compile(spec["regex"], re.MULTILINE),
                    "_allowlist_patterns": [
                        re.compile(pattern, re.MULTILINE)
                        for pattern in spec["allowlist"]
                    ],
                    "_path_allowlist_patterns": [
                        re.compile(pattern, re.MULTILINE)
                        for pattern in spec["path_allowlist"]
                    ],
                }
                rule_findings = scan_content(content, worker_rule, file_path=file_path)
            except BaseException:
                send_connection.send(
                    (
                        "rule_error",
                        rule_id,
                        traceback.format_exc(limit=20),
                    )
                )
                continue

            send_connection.send(("rule_ok", rule_id, rule_findings))

        send_connection.send(("complete",))
    except BaseException:
        send_connection.send(("worker_error", traceback.format_exc(limit=20)))
    finally:
        send_connection.close()


def scan_file_with_timeout(
    content: str,
    rules: Sequence[Dict[str, Any]],
    timeout_seconds: float,
    file_path: str | None = None,
) -> tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, str]]]:
    """Scan each rule with an independent timeout and retain partial results."""
    pending_rule_specs = [
        {
            "id": rule["id"],
            "regex": rule["_expanded_regex"],
            "allowlist": list(rule["allowlist"]),
            "path_allowlist": list(rule.get("path_allowlist", [])),
        }
        for rule in rules
    ]
    context = multiprocessing.get_context("spawn")
    findings_by_rule: Dict[str, List[Dict[str, Any]]] = {}
    rule_failures: List[Dict[str, str]] = []

    while pending_rule_specs:
        segment_specs = pending_rule_specs
        receive_connection, send_connection = context.Pipe(duplex=False)
        process = context.Process(
            target=_scan_file_worker,
            args=(content, file_path, segment_specs, send_connection),
            daemon=True,
        )
        current_rule_id: str | None = None

        try:
            process.start()
            send_connection.close()

            while True:
                poll_timeout = (
                    timeout_seconds
                    if current_rule_id is not None
                    else max(timeout_seconds, MIN_REGEX_WORKER_STARTUP_TIMEOUT_SECONDS)
                )
                if not receive_connection.poll(poll_timeout):
                    if current_rule_id is None:
                        raise RegexScanWorkerError(
                            "regex worker did not start a rule within "
                            f"{poll_timeout:.1f} seconds"
                        )

                    rule_failures.append(
                        {
                            "rule_id": current_rule_id,
                            "category": "regex_timeout",
                            "reason": (
                                f"regex scan exceeded {timeout_seconds:.1f} seconds"
                            ),
                        }
                    )
                    current_index = next(
                        index
                        for index, spec in enumerate(segment_specs)
                        if spec["id"] == current_rule_id
                    )
                    pending_rule_specs = segment_specs[current_index + 1 :]
                    break

                try:
                    message = receive_connection.recv()
                except EOFError as exc:
                    raise RegexScanWorkerError(
                        "regex worker exited without completing its protocol "
                        f"(exit code {process.exitcode})"
                    ) from exc

                if not isinstance(message, tuple) or not message:
                    raise RegexScanWorkerError(
                        "regex worker returned an invalid protocol message"
                    )

                status = message[0]
                if status == "rule_started" and len(message) == 2:
                    current_rule_id = message[1]
                elif status == "rule_ok" and len(message) == 3:
                    rule_id, payload = message[1], message[2]
                    if rule_id != current_rule_id or not isinstance(payload, list):
                        raise RegexScanWorkerError(
                            "regex worker returned invalid rule findings"
                        )
                    findings_by_rule[rule_id] = payload
                    current_rule_id = None
                elif status == "rule_error" and len(message) == 3:
                    rule_id, payload = message[1], message[2]
                    if rule_id != current_rule_id:
                        raise RegexScanWorkerError(
                            "regex worker returned an out-of-order rule error"
                        )
                    rule_failures.append(
                        {
                            "rule_id": rule_id,
                            "category": "regex_worker_error",
                            "reason": str(payload).strip(),
                        }
                    )
                    current_rule_id = None
                elif status == "complete" and len(message) == 1:
                    pending_rule_specs = []
                    break
                elif status == "worker_error" and len(message) == 2:
                    raise RegexScanWorkerError(
                        f"regex worker failed:\n{str(message[1]).strip()}"
                    )
                else:
                    raise RegexScanWorkerError(
                        f"regex worker returned unknown status {status!r}"
                    )
        finally:
            receive_connection.close()
            send_connection.close()
            if process.is_alive():
                process.terminate()
                process.join(timeout=2)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=2)
            else:
                process.join(timeout=2)

    return findings_by_rule, rule_failures


def make_github_file_url(
    repo_html_url: str,
    commit_sha: str,
    path: str,
    line: int | None = None,
) -> str:
    url = (
        f"{repo_html_url}/blob/{quote(commit_sha, safe='')}/" f"{quote(path, safe='/')}"
    )
    return f"{url}#L{line}" if line is not None else url


def next_output_file() -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    pattern = re.compile(rf"^{re.escape(OUTPUT_PREFIX)}_(\d+)\.json$")
    max_number = 0

    for path in OUTPUT_DIR.glob(f"{OUTPUT_PREFIX}_*.json"):
        match = pattern.match(path.name)
        if match:
            max_number = max(max_number, int(match.group(1)))

    return OUTPUT_DIR / f"{OUTPUT_PREFIX}_{max_number + 1:03d}.json"


def save_scan_result(result: Dict[str, Any], output_file: Path) -> None:
    """Publish a complete JSON file atomically without overwriting a peer."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = output_file.with_name(
        f".{output_file.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    )

    try:
        with open(temp_file, "x", encoding="utf-8", newline="\n") as file_handle:
            json.dump(result, file_handle, ensure_ascii=False, indent=2)
            file_handle.write("\n")
            file_handle.flush()
            os.fsync(file_handle.fileno())

        try:
            # A hard link publishes the fully-written inode and fails if another
            # crawler claimed the same numbered output first.
            os.link(temp_file, output_file)
        except FileExistsError:
            raise
        except OSError:
            # Some Windows filesystems do not permit hard links. Reserve the
            # destination exclusively, then atomically replace our reservation.
            reservation_fd = os.open(
                output_file,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
            os.close(reservation_fd)
            try:
                os.replace(temp_file, output_file)
            except BaseException:
                output_file.unlink(missing_ok=True)
                raise
    finally:
        temp_file.unlink(missing_ok=True)


def get_target_repo_input() -> str:
    if len(sys.argv) >= 2:
        return sys.argv[1]

    env_repo = os.getenv("GITHUB_REPO_URL") or os.getenv("TARGET_REPO_URL")
    if env_repo:
        return env_repo

    return input("GitHub repository URL or owner/repo: ").strip()


def build_summary(
    rules: List[Dict[str, Any]],
    findings: List[Dict[str, Any]],
    skipped_files: List[Dict[str, Any]],
    partially_scanned_files: List[Dict[str, Any]],
    failed_files: List[Dict[str, Any]],
) -> Dict[str, Any]:
    rule_counts = Counter(finding["rule_id"] for finding in findings)
    severity_counts = Counter(finding["severity"] for finding in findings)
    unique_locations = {
        (
            finding.get("commit_sha"),
            finding.get("file_path"),
            finding.get("start_offset"),
            finding.get("end_offset"),
            finding.get("match_hash"),
        )
        for finding in findings
    }

    return {
        "total_findings": len(findings),
        "total_unique_findings": len(unique_locations),
        "total_skipped_files": len(skipped_files),
        "total_partially_scanned_files": len(partially_scanned_files),
        "total_failed_files": len(failed_files),
        "by_rule": [
            {
                "rule_id": rule["id"],
                "rule_name": rule.get("name", ""),
                "severity": rule.get("severity", "unknown"),
                "rule_definition_hash": rule["_definition_hash"],
                "count": rule_counts.get(rule["id"], 0),
            }
            for rule in rules
        ],
        "by_severity": dict(sorted(severity_counts.items())),
    }


def scan_repository() -> Dict[str, Any]:
    started_at = utc_now_iso()
    repo_input = get_target_repo_input()
    parsed_repo = parse_github_repo(repo_input)
    headers = build_headers()
    warnings: List[str] = []
    request_delay_seconds = env_float(
        "GITHUB_REQUEST_DELAY_SECONDS", DEFAULT_REQUEST_DELAY_SECONDS
    )
    max_file_bytes = env_int("GITHUB_MAX_FILE_BYTES", DEFAULT_MAX_FILE_BYTES)
    regex_scan_timeout_seconds = env_float(
        "REGEX_SCAN_TIMEOUT_SECONDS",
        DEFAULT_REGEX_SCAN_TIMEOUT_SECONDS,
        minimum=0.001,
    )

    rule_set = load_rule_set(RULE_FILE)
    rules = prepare_rules(rule_set)
    rule_set_hash = hash_file(RULE_FILE)

    session = requests.Session()
    try:
        metadata = get_repository_metadata(
            parsed_repo["owner"],
            parsed_repo["repo"],
            headers,
            session=session,
            warnings=warnings,
        )
        default_branch = metadata.get("default_branch") or "main"
        commit_sha, tree_sha = get_repository_snapshot(
            parsed_repo["owner"],
            parsed_repo["repo"],
            default_branch,
            headers,
            session=session,
            warnings=warnings,
        )
        files, tree_complete, recursive_tree_truncated = get_repository_files(
            parsed_repo["owner"],
            parsed_repo["repo"],
            tree_sha,
            headers,
            session=session,
            warnings=warnings,
        )

        full_name = (
            metadata.get("full_name") or f"{parsed_repo['owner']}/{parsed_repo['repo']}"
        )
        repo_html_url = metadata.get("html_url") or f"https://github.com/{full_name}"
        findings = []
        scanned_files = []
        skipped_files = []
        partially_scanned_files = []
        failed_files = []
        seen_findings = set()
        scanned_file_count = 0
        partially_scanned_file_count = 0
        processed_file_count = 0
        scan_aborted_reason = None

        print(f"[INFO] Target repository: {full_name}")
        print(f"[INFO] Default branch: {default_branch}")
        print(f"[INFO] Commit SHA: {commit_sha}")
        print(f"[INFO] Loaded {len(rules)} rules from {RULE_FILE}")
        print(f"[INFO] Repository files discovered: {len(files)}")

        for index, file_item in enumerate(files, start=1):
            processed_file_count = index
            path = file_item["path"]
            blob_sha = file_item.get("sha")
            tree_size = file_item.get("size")

            if index == 1 or index % 25 == 0 or index == len(files):
                print(f"[INFO] Scanning files: {index}/{len(files)}")

            common_file_metadata = {
                "path": path,
                "blob_sha": blob_sha,
                "size": tree_size,
            }

            if not is_scannable_path(path):
                skipped_files.append(
                    {
                        **common_file_metadata,
                        "category": "unsupported_extension",
                        "reason": "outside scan scope (.py and .js files only)",
                    }
                )
                continue

            # Tree metadata lets us avoid downloading known oversized blobs.
            if isinstance(tree_size, int) and tree_size > max_file_bytes:
                skipped_files.append(
                    {
                        **common_file_metadata,
                        "category": "file_too_large",
                        "reason": f"file too large ({tree_size} bytes)",
                    }
                )
                continue

            if is_probably_binary_path(path):
                skipped_files.append(
                    {
                        **common_file_metadata,
                        "category": "binary_extension",
                        "reason": "binary file extension",
                    }
                )
                continue

            if not isinstance(blob_sha, str) or not blob_sha:
                failed_files.append(
                    {
                        **common_file_metadata,
                        "category": "invalid_tree_entry",
                        "reason": "repository tree entry did not contain a blob SHA",
                    }
                )
                continue

            blob_url = file_item.get("url")
            if not isinstance(blob_url, str) or not blob_url:
                blob_url = (
                    f"{GITHUB_API_BASE}/repos/{parsed_repo['owner']}/"
                    f"{parsed_repo['repo']}/git/blobs/{blob_sha}"
                )

            try:
                content, skip_reason = fetch_blob_content(
                    blob_url,
                    headers=headers,
                    max_file_bytes=max_file_bytes,
                    expected_blob_sha=blob_sha,
                    session=session,
                    warnings=warnings,
                )
            except GitHubAuthenticationError:
                raise
            except (GitHubRateLimitError, GitHubPermissionError) as exc:
                failed_files.append(
                    {
                        **common_file_metadata,
                        "category": exc.category,
                        "status_code": exc.status_code,
                        "reason": str(exc),
                    }
                )
                scan_aborted_reason = str(exc)
                append_warning(
                    warnings,
                    "Repository scan stopped before all files were attempted: "
                    f"{exc}",
                )
                break
            except GitHubRequestError as exc:
                failed_files.append(
                    {
                        **common_file_metadata,
                        "category": exc.category,
                        "status_code": exc.status_code,
                        "reason": str(exc),
                    }
                )
                continue
            except Exception as exc:
                failed_files.append(
                    {
                        **common_file_metadata,
                        "category": "unexpected_fetch_error",
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                )
                continue

            if skip_reason:
                if skip_reason.startswith("file too large"):
                    skip_category = "file_too_large"
                elif skip_reason.startswith("unsupported text encoding"):
                    skip_category = "unsupported_text_encoding"
                else:
                    skip_category = "binary_content"
                skipped_files.append(
                    {
                        **common_file_metadata,
                        "category": skip_category,
                        "reason": skip_reason,
                    }
                )
                continue

            if content is None:
                failed_files.append(
                    {
                        **common_file_metadata,
                        "category": "invalid_blob_content",
                        "reason": "blob decoder returned no content or skip reason",
                    }
                )
                continue

            try:
                findings_by_rule, rule_failures = scan_file_with_timeout(
                    content,
                    rules,
                    regex_scan_timeout_seconds,
                    file_path=path,
                )
            except RegexScanWorkerError as exc:
                failed_files.append(
                    {
                        **common_file_metadata,
                        "category": "regex_worker_error",
                        "reason": str(exc),
                    }
                )
                continue

            if rule_failures:
                partially_scanned_file_count += 1
                scanned_files.append(
                    {
                        **common_file_metadata,
                        "status": "partial",
                        "rules_scanned": len(findings_by_rule),
                        "rules_failed": len(rule_failures),
                    }
                )
                partially_scanned_files.append(
                    {
                        **common_file_metadata,
                        "category": "regex_rule_failures",
                        "reason": (
                            f"{len(rule_failures)} rule(s) could not scan this file"
                        ),
                        "failed_rules": rule_failures,
                    }
                )
            else:
                scanned_file_count += 1
                scanned_files.append(
                    {
                        **common_file_metadata,
                        "status": "complete",
                        "rules_scanned": len(findings_by_rule),
                        "rules_failed": 0,
                    }
                )

            for rule in rules:
                for finding in findings_by_rule.get(rule["id"], []):
                    finding_key = (
                        rule["id"],
                        path,
                        finding["start_offset"],
                        finding["end_offset"],
                        finding["match_hash"],
                    )

                    if finding_key in seen_findings:
                        continue

                    seen_findings.add(finding_key)
                    findings.append(
                        {
                            "rule_id": rule["id"],
                            "rule_name": rule.get("name", ""),
                            "rule_definition_hash": rule["_definition_hash"],
                            "owasp": rule.get("owasp", []),
                            "cwe": rule.get("cwe", []),
                            "severity": rule.get("severity", "unknown"),
                            "repository": full_name,
                            "commit_sha": commit_sha,
                            "blob_sha": blob_sha,
                            "file_path": path,
                            "html_url": make_github_file_url(
                                repo_html_url,
                                commit_sha,
                                path,
                                finding["line"],
                            ),
                            **finding,
                        }
                    )

            if request_delay_seconds:
                time.sleep(request_delay_seconds)
    finally:
        session.close()

    finished_at = utc_now_iso()
    files_not_attempted = max(len(files) - processed_file_count, 0)
    partial_reasons = []
    if not tree_complete:
        partial_reasons.append("repository tree recovery was incomplete")
    if partially_scanned_files:
        partial_reasons.append(
            f"{len(partially_scanned_files)} file(s) were partially scanned"
        )
    if failed_files:
        partial_reasons.append(f"{len(failed_files)} file(s) failed")
    if scan_aborted_reason:
        partial_reasons.append(f"scan aborted: {scan_aborted_reason}")
    if files_not_attempted:
        partial_reasons.append(f"{files_not_attempted} file(s) were not attempted")

    scan_complete = not partial_reasons
    if partially_scanned_files:
        append_warning(
            warnings,
            f"{len(partially_scanned_files)} file(s) were partially scanned; "
            "see partially_scanned_files.",
        )
    if failed_files:
        append_warning(
            warnings,
            f"{len(failed_files)} file(s) could not be scanned; see failed_files.",
        )

    result = {
        "target_repository": {
            "input": repo_input,
            "owner": parsed_repo["owner"],
            "name": parsed_repo["repo"],
            "full_name": full_name,
            "html_url": repo_html_url,
            "default_branch": default_branch,
            "commit_sha": commit_sha,
            "tree_sha": tree_sha,
        },
        "scan": {
            "started_at": started_at,
            "finished_at": finished_at,
            "status": "complete" if scan_complete else "partial",
            "scan_complete": scan_complete,
            "scope": "default_branch_head",
            "partial_reasons": partial_reasons,
            "rules_loaded": len(rules),
            "rule_set": {
                "title": rule_set["title"],
                "version": rule_set["version"],
                "sha256": rule_set_hash,
                "file": str(RULE_FILE.relative_to(PROJECT_ROOT)),
            },
            "files_discovered": len(files),
            "files_scanned": scanned_file_count,
            "files_partially_scanned": partially_scanned_file_count,
            "files_skipped": len(skipped_files),
            "files_failed": len(failed_files),
            "files_not_attempted": files_not_attempted,
            "tree_complete": tree_complete,
            "recursive_tree_truncated": recursive_tree_truncated,
            "max_file_bytes": max_file_bytes,
            "regex_scan_timeout_seconds": regex_scan_timeout_seconds,
            "included_extensions": sorted(SCANNABLE_EXTENSIONS),
        },
        "summary": build_summary(
            rules,
            findings,
            skipped_files,
            partially_scanned_files,
            failed_files,
        ),
        "findings": findings,
        "scanned_files": scanned_files,
        "skipped_files": skipped_files,
        "partially_scanned_files": partially_scanned_files,
        "failed_files": failed_files,
        "warnings": warnings,
    }

    return result


def main() -> None:
    result = scan_repository()
    while True:
        output_file = next_output_file()
        try:
            save_scan_result(result, output_file)
            break
        except FileExistsError:
            # Another crawler claimed this sequence number between discovery
            # and publication. Select the next available name without overwrite.
            continue

    print("[SUMMARY]")
    print(f"  repository: {result['target_repository']['full_name']}")
    print(f"  scan status: {result['scan']['status']}")
    print(f"  files scanned: {result['scan']['files_scanned']}")
    print(f"  findings: {result['summary']['total_findings']}")
    print(f"  skipped files: {result['summary']['total_skipped_files']}")
    print(
        "  partially scanned files: "
        f"{result['summary']['total_partially_scanned_files']}"
    )
    print(f"  failed files: {result['summary']['total_failed_files']}")

    for rule in result["summary"]["by_rule"]:
        if rule["count"] > 0:
            print(f"  {rule['rule_id']}: {rule['count']}")

    if result["warnings"]:
        print("[WARNINGS]")
        for warning in result["warnings"]:
            print(f"  - {warning}")

    completion_label = "DONE" if result["scan"]["scan_complete"] else "PARTIAL"
    print(f"[{completion_label}] Results saved to {output_file}")


if __name__ == "__main__":
    main()
