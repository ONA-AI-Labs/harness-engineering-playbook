#!/usr/bin/env python3
"""PreToolUse guard: deny or ask before destructive commands and edits. Fails open.

Drop-in for Claude Code and Codex. Reads the hook JSON on stdin, prints a
permissionDecision JSON for deny/ask, prints nothing for allow, always exits 0
(a broken guard must never block work). Every decision is appended to the
metrics file (default ~/.claude/metrics/harness.jsonl, override with
HARNESS_METRICS_FILE) so you can see whether the harness fires. The file is
private (mode 0600) and rotates at 5 MB. Command text is written only for ask
and deny decisions, with known secret shapes redacted; set HARNESS_LOG_COMMANDS
to `none` to log decisions only, or `full` on a machine where the log is as
protected as your shell history.

Policy (per segment of a compound command; the strongest decision wins):
  deny  force-push to main/master; recursive force-delete of /, ~, .git, or
        anything outside the workspace and temp dirs; database resets and
        migration pushes (supabase db reset|push, prisma migrate reset|deploy);
        deleting the main branch; gh repo delete; terraform destroy -auto-approve
  ask   other force-pushes and remote branch deletes; git reset --hard,
        checkout/restore of the whole tree, git clean -f, stash drop/clear;
        recursive force-delete inside the workspace except build folders;
        psql/mysql/sqlite with DROP/TRUNCATE/DELETE/UPDATE/ALTER or a script file;
        ssh running destructive commands; docker prune or volume removal;
        kubectl delete, terraform destroy, cloud CLI delete commands;
        gh pr merge, gh release; package publish; editing .env* files or an
        existing migration file
  allow everything else, and any input the guard cannot parse

The workspace is CLAUDE_PROJECT_DIR (set by Claude Code); the hook's cwd stands
in when it is missing. Shell variables assigned in the same command are
resolved; unknown variables ask. Heredoc bodies are data, not commands.

The named tools (supabase, prisma, kubectl, terraform, the cloud CLIs) are a starting
list: add the migration and infrastructure tools your repository uses. Codex documents
`deny` for a hook's decision; treat an `ask` there as a deny until confirmed.
"""
import hashlib
import json
import os
import re
import shlex
import sys
import time
from pathlib import Path

METRICS = Path(os.environ.get("HARNESS_METRICS_FILE") or (Path.home() / ".claude" / "metrics" / "harness.jsonl"))
BUILD_DIRS = {"node_modules", "dist", "build", "out", ".next", ".dart_tool", "coverage",
              "target", ".turbo", ".cache", "tmp", ".parcel-cache", "Pods", "DerivedData", ".venv", "venv", "__pycache__", ".pytest_cache"}
TEMP_ROOTS = ["/tmp", "/private/tmp", "/var/folders", "/private/var/folders"]
RANK = {"allow": 0, "ask": 1, "deny": 2}


LOG_MODE = os.environ.get("HARNESS_LOG_COMMANDS", "redacted")  # none | redacted | full
SECRET_PATTERNS = [
    (re.compile(r"(?i)(authorization:\s*bearer\s+)\S+"), r"\1[redacted]"),
    (re.compile(r"(?i)\b([A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|API_?KEY|PRIVATE_KEY|ACCESS_KEY)[A-Z0-9_]*)=(\"[^\"]*\"|'[^']*'|\S+)"), r"\1=[redacted]"),
    (re.compile(r"(?i)(--?(?:password|passwd|token|api[-_]?key|secret|access[-_]?key)[= ]+)(\"[^\"]*\"|'[^']*'|\S+)"), r"\1[redacted]"),
    (re.compile(r"(?i)\b(password|passwd|token|secret|api_?key|access_?key)=([^\s&\"']+)"), r"\1=[redacted]"),
    (re.compile(r"://([^/\s:@]+):([^@\s/]+)@"), r"://\1:[redacted]@"),
    (re.compile(r"\b(sk-[A-Za-z0-9_-]{8,}|ghp_[A-Za-z0-9]{8,}|gho_[A-Za-z0-9]{8,}|github_pat_[A-Za-z0-9_]{8,}|AKIA[A-Z0-9]{12,}|xox[abprs]-[A-Za-z0-9-]{8,}|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,})"), "[redacted]"),
]


def redact(text):
    """Scrub known secret shapes before anything is written to disk."""
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def log(record):
    """Append one JSON line; the file is private (0600) and rotates at 5 MB. Never raises."""
    try:
        METRICS.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(METRICS.parent, 0o700)
        if METRICS.is_file() and METRICS.stat().st_size > 5_000_000:
            METRICS.replace(METRICS.with_suffix(METRICS.suffix + ".1"))
        fd = os.open(str(METRICS), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a") as handle:
            handle.write(json.dumps(record) + "\n")
        os.chmod(METRICS, 0o600)
    except OSError:
        pass


def worse(a, b):
    return a if RANK[a[0]] >= RANK[b[0]] else b


HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1[^\n]*\n.*?\n[ \t]*\2[ \t]*(?=\n|$)", re.S)


def strip_heredocs(cmd):
    """Heredoc bodies are data being written, not commands: drop them before judging."""
    def omit(match):
        first_line = match.group(0).split("\n", 1)[0]
        return first_line[:first_line.find("<<")] + "<<HEREDOC_BODY_OMITTED"
    return HEREDOC.sub(omit, cmd)


def split_segments(cmd):
    # shortcut: splits on shell operators without respecting quotes, enough for guarding
    return [s.strip() for s in re.split(r"&&|\|\||;|\||\n", cmd) if s.strip()]


def tokens_of(segment):
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


ASSIGNMENT = re.compile(r"(?:^|[;&|\s])(?:export\s+)?([A-Za-z_]\w*)=(\"[^\"]*\"|'[^']*'|[^\s;&|]+)")


def shell_assignments(cmd):
    """VAR=value assignments made in the command itself (the hook cannot see the shell's variables)."""
    return {name: value.strip("\"'") for name, value in ASSIGNMENT.findall(cmd)}


def expand_local(path, local):
    for name, value in local.items():
        path = path.replace("${%s}" % name, value).replace("$%s" % name, value)
    return path


def norm(path, cwd):
    expanded = os.path.expanduser(os.path.expandvars(path))
    if not os.path.isabs(expanded):
        expanded = os.path.join(cwd, expanded)
    return os.path.normpath(expanded)


def inside(path, root):
    return bool(root) and (path == root or path.startswith(root.rstrip("/") + "/"))


def judge_rm(tokens, cwd, roots, local=None):
    flags = [t for t in tokens[1:] if t.startswith("-")]
    joined = "".join(f.lstrip("-") for f in flags if not f.startswith("--"))
    recursive = ("r" in joined or "R" in joined or "--recursive" in flags)
    forced = ("f" in joined or "--force" in flags)
    if not (recursive and forced):
        return ("allow", "")
    targets = [t for t in tokens[1:] if not t.startswith("-")]
    if not targets:
        return ("allow", "")
    home = os.path.expanduser("~")
    decision = ("allow", "")
    for raw in targets:
        if raw in {"/", "/*", "~", "~/", "$HOME", "${HOME}", "*", ".", "..", "./", "../"}:
            return ("deny", "rm -rf on %s would destroy far more than a build folder" % raw)
        resolved = expand_local(raw, local or {})
        if "$" in os.path.expandvars(resolved):
            decision = worse(decision, ("ask", "rm -rf %s: the guard cannot resolve that variable; confirm" % raw))
            continue
        path = norm(resolved, cwd)
        if path in {"/", home} or os.path.basename(path) == ".git":
            return ("deny", "rm -rf on %s (root, home or a .git directory)" % raw)
        if any(inside(path, r) for r in roots if r):
            if os.path.basename(path) in BUILD_DIRS:
                continue
            decision = worse(decision, ("ask", "rm -rf %s is inside the workspace but not a build folder; confirm" % raw))
        elif any(inside(path, t) for t in TEMP_ROOTS):
            continue
        else:
            return ("deny", "rm -rf %s is outside the workspace and temp dirs" % raw)
    return decision


def git_subcommand(tokens):
    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t in {"-C", "--git-dir", "--work-tree", "-c"}:
            i += 2
            continue
        if t.startswith("-"):
            i += 1
            continue
        return t, tokens[i + 1:]
    return "", []


def judge_git(tokens):
    sub, args = git_subcommand(tokens)
    lower = [a.lower() for a in args]
    if sub == "push":
        force = any(a in {"-f", "--force"} or a.startswith("--force-with-lease") or a.startswith("--force-if-includes") for a in args)
        force = force or any(a.startswith("+") for a in args)
        names_main = any(re.search(r"(^|[:+/])(main|master)$", a) for a in lower)
        if force and names_main:
            return ("deny", "force-push to main/master rewrites shared history")
        if any(a in {"-d", "--delete"} for a in args) or any(re.match(r"^:\S+$", a) for a in args):
            return ("ask", "git push is deleting a remote branch; confirm")
        if force:
            return ("ask", "force-push rewrites history on the remote branch; confirm")
    if sub == "reset" and "--hard" in lower:
        return ("ask", "git reset --hard discards uncommitted work; confirm")
    if sub in {"checkout", "restore"}:
        if "--staged" in lower and len([a for a in args if not a.startswith("-")]) == 1 and "." in args:
            return ("allow", "")
        if "." in args or ("--" in args and args[-1] == "."):
            return ("ask", "git %s of the whole tree discards uncommitted work; confirm" % sub)
    if sub == "clean" and any(re.match(r"^-[a-z]*f", a) for a in lower):
        return ("ask", "git clean deletes untracked files; confirm")
    if sub == "branch" and any(a in {"-D", "-d"} for a in args) and any(a in {"main", "master"} for a in lower):
        return ("deny", "deleting the main branch")
    if sub == "stash" and any(a in {"drop", "clear"} for a in lower):
        return ("ask", "git stash %s throws work away; confirm" % [a for a in lower if a in {"drop", "clear"}][0])
    return ("allow", "")


SQL_DESTRUCTIVE = re.compile(r"\b(drop\s+(table|schema|database|index|function|policy)|truncate|delete\s+from|update\s+\w+\s+set|alter\s+table)\b", re.I)
SSH_DESTRUCTIVE = re.compile(r"(\brm\s|docker(-|\s)compose\s+down|\bsystemctl\b|\bkill\s|\breboot\b|\bshutdown\b|\btruncate\b|\bdrop\s+table\b)", re.I)


def judge_segment(segment, cwd, roots, local=None):
    tokens = tokens_of(segment)
    # drop leading VAR=value words so `S=/tmp/x rm -rf $S` is judged as rm
    while tokens and ASSIGNMENT.match(" " + tokens[0]) and "=" in tokens[0]:
        tokens = tokens[1:]
    if not tokens:
        return ("allow", "")
    head = os.path.basename(tokens[0])
    if head in {"sudo", "env", "nohup", "time"} and len(tokens) > 1:
        return judge_segment(" ".join(tokens[1:]), cwd, roots, local)
    if head == "rm":
        return judge_rm(tokens, cwd, roots, local)
    if head == "git":
        return judge_git(tokens)
    joined = " ".join(tokens[1:]).lower()
    whole = " ".join(tokens).lower()
    if head == "supabase" and (re.search(r"\bdb\s+(reset|push)\b", joined) or re.search(r"\bmigration\s+up\b", joined)):
        return ("deny", "database resets and migration pushes are applied by a person, never by an agent")
    if re.search(r"\bprisma\s+migrate\s+(reset|deploy)\b", whole):
        return ("deny", "database resets and migration deploys are applied by a person, never by an agent")
    if head in {"psql", "mysql", "sqlite3", "supabase"} and (SQL_DESTRUCTIVE.search(segment) or any(t in {"-f", "--file"} for t in tokens)):
        return ("ask", "destructive SQL or a script file against a database; confirm")
    if head == "kubectl" and joined.startswith("delete"):
        return ("ask", "kubectl delete removes live resources; confirm")
    if head == "terraform" and joined.startswith("destroy"):
        return ("deny", "terraform destroy with auto-approve") if "-auto-approve" in joined else ("ask", "terraform destroy; confirm")
    if head in {"aws", "gcloud", "az"} and re.search(r"\b(delete|rm|remove|destroy)\b", joined):
        return ("ask", "cloud delete command; confirm")
    if head == "ssh":
        remote = " ".join(tokens[2:]) if len(tokens) > 2 else ""
        if SSH_DESTRUCTIVE.search(remote):
            return ("ask", "remote command on a server can destroy state; confirm")
    if head in {"docker", "docker-compose"}:
        joined = " ".join(tokens).lower()
        if re.search(r"compose\s+down.*(\s-v\b|--volumes)", joined) or "docker-compose down -v" in joined:
            return ("ask", "docker compose down -v deletes volumes; confirm")
        if re.search(r"\b(system|volume|image|container)\s+prune\b", joined) or re.search(r"\bvolume\s+rm\b", joined):
            return ("ask", "docker prune/volume rm deletes data; confirm")
    if head == "gh":
        joined = " ".join(tokens[1:]).lower()
        if joined.startswith("repo delete"):
            return ("deny", "deleting a GitHub repository")
        if joined.startswith("pr merge"):
            return ("ask", "merging may deploy automatically; confirm")
        if joined.startswith("release"):
            return ("ask", "publishing a release; confirm")
    if (head in {"npm", "cargo", "dart", "flutter", "pnpm", "yarn"} and "publish" in tokens[1:4]) or (head == "npm" and "unpublish" in tokens):
        return ("ask", "publishing a package is public and hard to undo; confirm")
    return ("allow", "")


def judge_command(cmd, cwd, roots):
    decision = ("allow", "")
    cmd = strip_heredocs(cmd)
    local = shell_assignments(cmd)
    for segment in split_segments(cmd):
        decision = worse(decision, judge_segment(segment, cwd, roots, local))
    return decision


def judge_file(tool_input):
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not path:
        return ("allow", "")
    path = path.replace("\\", "/")
    name = os.path.basename(path)
    if re.match(r"^\.env(\..+)?$", name) and name not in {".env.example", ".env.sample", ".env.template"}:
        return ("ask", "%s holds secrets; confirm the edit" % name)
    if re.search(r"/migrations?/", path) and os.path.exists(path):
        return ("ask", "editing an existing migration; applied migrations are frozen, add a new numbered one instead")
    return ("allow", "")


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except ValueError:
        log({"ts": time.time(), "event": "PreToolUse", "decision": "allow", "reason": "unparseable input"})
        return
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()
    # the workspace is the project dir Claude Code sets; cwd stands in only when it is missing (hand tests)
    project = os.environ.get("CLAUDE_PROJECT_DIR", "")
    roots = [project] if project else [cwd]
    record = {"ts": time.time(), "event": "PreToolUse", "tool": tool, "session": data.get("session_id"),
              "agent_type": data.get("agent_type")}
    if tool in {"Bash", "shell", "bash"}:
        cmd = tool_input.get("command", "") or ""
        decision, reason = judge_command(cmd, cwd, roots)
        first = tokens_of(split_segments(cmd)[0]) if split_segments(cmd) else []
        record["program"] = os.path.basename(first[0]) if first else ""
        record["cmd_hash"] = hashlib.sha256(cmd.encode("utf-8", "replace")).hexdigest()[:12]
        # the command text itself is written only for ask/deny, and redacted unless HARNESS_LOG_COMMANDS=full
        if decision != "allow" and LOG_MODE != "none":
            record["subject"] = (cmd if LOG_MODE == "full" else redact(cmd))[:200]
    elif tool in {"Edit", "Write", "MultiEdit", "NotebookEdit", "apply_patch"}:
        decision, reason = judge_file(tool_input)
        record["subject"] = (tool_input.get("file_path") or tool_input.get("notebook_path") or "")[:200]
    else:
        return
    record.update({"decision": decision, "reason": reason})
    log(record)
    if decision != "allow":
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                 "permissionDecision": decision,
                                                 "permissionDecisionReason": reason}}))


if __name__ == "__main__":
    try:
        main()
    except Exception as err:  # fail open, never block on a guard bug
        log({"ts": time.time(), "event": "PreToolUse", "decision": "allow", "reason": "guard error: %r" % (err,)})
    sys.exit(0)
