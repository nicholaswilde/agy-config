#!/usr/bin/env python3
"""
Extract concise, actionable failure diagnostics from a GitHub Actions workflow job log.
Usage:
    python3 get-job-failure.py <job_id>
    gh run view --job <job_id> --log-failed | python3 get-job-failure.py
"""

import sys
import re
import subprocess
import shutil

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
OSC_ESCAPE = re.compile(r'\x1B\][^\x07\x1b]*(?:\x07|\x1b\\\\)')
CARET_ESCAPE = re.compile(r'\^\[\[[0-9;]*[a-zA-Z]|\^\[\][^\^]*\^G')
TIMESTAMP_PREFIX = re.compile(r'^\S+Z\s*')

# Lines to ignore as runner infrastructure noise
RUNNER_NOISE_PREFIXES = (
    '##[group]',
    '##[endgroup]',
    'Current runner version',
    'Hosted Compute Agent',
    'Image:',
    'Version:',
    'Commit:',
    'Build Date:',
    'Worker ID:',
    'Region:',
    'Cloud:',
    'Operating System',
    'Included Software:',
    'Image Release:',
    'GITHUB_TOKEN Permissions',
    'Secret source:',
    'Cache mode:',
    'Prepare workflow directory',
    'Prepare all required actions',
    'Getting action download info',
    'Download action repository',
    'Complete job name:',
    'Removing HTTP extra header',
    'Removing credentials config',
    'Removing includeIf entries',
    'Cleaning up orphan processes',
    'Terminate orphan process',
    'Temporarily overriding HOME',
    'Adding repository directory',
    'Removing SSH command configuration',
)

FAILURE_INDICATORS = (
    'failures:',
    'FAILED',
    'panicked at',
    'assertion failed',
    'assertion `left == right` failed',
    'error[E',
    'error: ',
    'Error: ',
    'panic:',
    'fatal error:',
    'Traceback (most recent call last):',
    'FAIL ',
    'FAIL:',
    'npm ERR!',
)

TRUNCATE_MARKERS = (
    'Post job cleanup.',
    'Post Checkout repository',
    'Cleaning up orphan processes',
    '##[group]Run actions/upload-artifact',
)


def clean_line(line: str) -> str:
    cleaned = OSC_ESCAPE.sub('', line)
    cleaned = ANSI_ESCAPE.sub('', cleaned)
    cleaned = CARET_ESCAPE.sub('', cleaned)
    return cleaned.rstrip('\r\n')


def is_noise(msg: str) -> bool:
    for prefix in RUNNER_NOISE_PREFIXES:
        if msg.startswith(prefix):
            return True
    if any(k in msg for k in ('git-credentials', 'core.sshCommand', 'extraheader', 'includeif.gitdir')):
        return True
    return False


def parse_job_log(raw_log: str) -> list[tuple[str, str]]:
    """Parse raw log lines into (step_name, clean_message)."""
    parsed = []
    for line in raw_log.splitlines():
        line = clean_line(line)
        if not line:
            continue
        parts = line.split('\t', 2)
        step = parts[1].strip() if len(parts) > 1 else 'UNKNOWN'
        raw_msg = parts[2] if len(parts) > 2 else line
        msg = TIMESTAMP_PREFIX.sub('', raw_msg).strip()
        if not is_noise(msg):
            parsed.append((step, msg))
    return parsed


def extract_failure_block(parsed: list[tuple[str, str]], max_lines: int = 60) -> tuple[str, list[str]]:
    """Extract failing step name and the most relevant diagnostic block."""
    failing_step = 'UNKNOWN'

    failure_indices = []
    for idx, (step, msg) in enumerate(parsed):
        if any(ind in msg for ind in FAILURE_INDICATORS):
            failure_indices.append((idx, step))
            if failing_step == 'UNKNOWN' and step not in ('UNKNOWN', 'UNKNOWN STEP'):
                failing_step = step

    if not failure_indices:
        tail = [msg for _, msg in parsed[-max_lines:]]
        step = parsed[-1][0] if parsed else 'UNKNOWN'
        return step, tail

    chosen_idx, chosen_step = failure_indices[-1]
    for idx, step in failure_indices:
        msg = parsed[idx][1]
        if any(core in msg for core in ('panicked at', 'failures:', 'error[E', 'Traceback')):
            chosen_idx, chosen_step = idx, step
            break

    if chosen_step not in ('UNKNOWN', 'UNKNOWN STEP'):
        failing_step = chosen_step

    start = max(0, chosen_idx - 3)
    extracted = []
    for i in range(start, min(len(parsed), start + max_lines)):
        msg = parsed[i][1]
        if any(term in msg for term in TRUNCATE_MARKERS):
            break
        extracted.append(msg)

    return failing_step, extracted


def get_job_metadata(job_id: str) -> dict:
    """Fetch job overview metadata via gh run view --job."""
    meta = {'name': 'Unknown', 'failing_step': 'UNKNOWN'}
    gh_path = shutil.which('gh')
    if not gh_path:
        return meta

    try:
        proc = subprocess.run(
            [gh_path, 'run', 'view', '--job', job_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            for raw_l in proc.stdout.splitlines():
                l = clean_line(raw_l)
                l_str = l.strip()
                m_job = re.match(r'^[Xx]\s+(.+?)(?:\s+in\s+[^\s]+)?\s+\(ID\s+(\d+)\)', l_str)
                if m_job and m_job.group(2) == job_id:
                    meta['name'] = m_job.group(1).strip()
                elif (raw_l.startswith('  X ') or raw_l.startswith('    X ')) and not l_str.startswith('X Process completed'):
                    # Failing step listed under job
                    step_name = l_str[2:].strip()
                    meta['failing_step'] = step_name
    except Exception:
        pass
    return meta


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ('--help', '-h'):
        print(__doc__.strip())
        sys.exit(0)

    job_id = None
    if len(sys.argv) > 1 and sys.argv[1] != '-':
        job_id = sys.argv[1].strip()
        gh_path = shutil.which('gh')
        if not gh_path:
            sys.exit("Error: 'gh' (GitHub CLI) not found in PATH.")

        meta = get_job_metadata(job_id)

        proc = subprocess.run(
            [gh_path, 'run', 'view', '--job', job_id, '--log-failed'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            sys.exit(f"Error executing gh: {proc.stderr.strip()}")
        raw_log = proc.stdout
    else:
        raw_log = sys.stdin.read()
        meta = {'name': 'Stdin', 'failing_step': 'UNKNOWN'}

    if not raw_log.strip():
        print("No log content found.")
        sys.exit(0)

    parsed = parse_job_log(raw_log)
    step, block = extract_failure_block(parsed)

    failing_step = meta['failing_step'] if meta.get('failing_step') != 'UNKNOWN' else step

    print(f"Job ID: {job_id if job_id else 'stdin'}")
    if meta.get('name') != 'Unknown':
        print(f"Job Name: {meta['name']}")
    print(f"Failing Step: {failing_step}")
    print("--- Failure Diagnostics ---")
    for line in block:
        print(line)


if __name__ == '__main__':
    main()
