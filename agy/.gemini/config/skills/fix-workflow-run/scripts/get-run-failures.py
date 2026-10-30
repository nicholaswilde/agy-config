#!/usr/bin/env python3
"""
Extract concise, actionable failure diagnostics from all failed jobs in a GitHub Actions workflow run.
Usage:
    python3 get-run-failures.py <run_id>
    gh run view <run_id> --log-failed | python3 get-run-failures.py
"""

import sys
import re
import subprocess
import shutil
from collections import defaultdict

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


def parse_job_lines(lines: list[str]) -> list[tuple[str, str]]:
    """Parse raw log lines into (step_name, clean_message)."""
    parsed = []
    for line in lines:
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


def get_failed_jobs_from_run(run_id: str, gh_path: str) -> list[dict]:
    """Parse gh run view <run_id> for failed jobs and their failing steps."""
    proc = subprocess.run(
        [gh_path, 'run', 'view', run_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        sys.exit(f"Error querying run view: {proc.stderr.strip()}")

    failed_jobs = []
    current_job = None

    for raw_line in proc.stdout.splitlines():
        line = clean_line(raw_line)
        # Check if line is indented step or top-level job
        if raw_line.startswith('  ') or raw_line.startswith('\t'):
            if current_job:
                stripped = line.strip()
                if stripped.startswith('X ') and not stripped.startswith('X Process completed'):
                    current_job['failing_step'] = stripped[2:].strip()
            continue

        # Top-level entry
        m = re.match(r'^[Xx]\s+(.+?)(?:\s+in\s+[^\s]+)?\s+\(ID\s+(\d+)\)', line.strip())
        if m:
            current_job = {
                'name': m.group(1).strip(),
                'id': m.group(2).strip(),
                'failing_step': 'UNKNOWN',
            }
            failed_jobs.append(current_job)
        else:
            current_job = None

    return failed_jobs


def fetch_job_log(job_id: str, gh_path: str) -> str:
    """Fetch --log-failed for a specific job."""
    proc = subprocess.run(
        [gh_path, 'run', 'view', '--job', job_id, '--log-failed'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ('--help', '-h'):
        print(__doc__.strip())
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] != '-':
        run_id = sys.argv[1].strip()
        gh_path = shutil.which('gh')
        if not gh_path:
            sys.exit("Error: 'gh' (GitHub CLI) not found in PATH.")

        failed_jobs = get_failed_jobs_from_run(run_id, gh_path)
        if not failed_jobs:
            print(f"No failed jobs found in run {run_id}.")
            sys.exit(0)

        print(f"Run ID: {run_id}")
        print(f"Failed Jobs Count: {len(failed_jobs)}")

        for job in failed_jobs:
            print("\n" + "=" * 80)
            print(f"Job: {job['name']} (ID: {job['id']})")

            raw_log = fetch_job_log(job['id'], gh_path)
            if not raw_log.strip():
                print(f"Failing Step: {job['failing_step']}")
                print("No failure log retrieved.")
                continue

            parsed = parse_job_lines(raw_log.splitlines())
            step, block = extract_failure_block(parsed)
            failing_step = job['failing_step'] if job.get('failing_step') != 'UNKNOWN' else step

            print(f"Failing Step: {failing_step}")
            print("-" * 80)
            for line in block:
                print(line)

    else:
        # Read from stdin
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print("No log content found.")
            sys.exit(0)

        # Group lines by job name if present in column 1
        lines_by_job = defaultdict(list)
        for line in raw_input.splitlines():
            cleaned = clean_line(line)
            if not cleaned:
                continue
            parts = cleaned.split('\t', 1)
            if len(parts) > 1 and parts[1]:
                job_name = parts[0].strip()
                lines_by_job[job_name].append(cleaned)
            else:
                lines_by_job['Standard Input'].append(cleaned)

        print(f"Failed Jobs Detected: {len(lines_by_job)}")
        for job_name, job_lines in lines_by_job.items():
            print("\n" + "=" * 80)
            print(f"Job: {job_name}")
            parsed = parse_job_lines(job_lines)
            step, block = extract_failure_block(parsed)
            print(f"Failing Step: {step}")
            print("-" * 80)
            for line in block:
                print(line)


if __name__ == '__main__':
    main()
