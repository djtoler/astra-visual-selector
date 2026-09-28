#!/usr/bin/env python3
"""Run mapped documentary templates through After Effects' scripting API."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent
APP = '/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app'
TEMPLATE = Path('/Volumes/onn. Drive/AE Templates/03 Documentary & Archival/Documentary Trailer/Documentary Trailer.aepx')


def prepare(job_path, mode):
    job_path = Path(job_path).resolve()
    job = json.loads(job_path.read_text())
    def path(value):
        p = Path(value).expanduser()
        return str((job_path.parent / p).resolve() if not p.is_absolute() else p.resolve())
    job['template'] = path(job.get('template', str(TEMPLATE)))
    if not Path(job['template']).is_file():
        raise ValueError('Template does not exist: ' + job['template'])
    if job.get('prepared_project'):
        job['prepared_project'] = path(job['prepared_project'])
        if not Path(job['prepared_project']).is_file():
            raise ValueError('Prepared project does not exist: ' + job['prepared_project'])
    if job.get('inspection_save'):
        job['inspection_save'] = path(job['inspection_save'])
    cpu = job.get('max_cpu_percent')
    if cpu is not None and (isinstance(cpu, bool) or not isinstance(cpu, (int, float)) or not 1 <= cpu <= 100):
        raise ValueError('max_cpu_percent must be between 1 and 100')
    if job.get('gpu_acceleration') not in (None, 'Metal'):
        raise ValueError('gpu_acceleration must be Metal when supplied')
    if job.get('font_policy', 'strict') not in ('strict', 'substitute_and_flag'):
        raise ValueError('font_policy must be strict or substitute_and_flag')
    job['mode'] = mode
    if not isinstance(job.get('demo', False), bool):
        raise ValueError('demo must be true or false')
    preview = job.get('preview_seconds')
    if preview is not None and (isinstance(preview, bool) or not isinstance(preview, (int, float)) or not 0 < preview <= 3600):
        raise ValueError('preview_seconds must be greater than zero and at most 3600')
    render_start = job.get('render_start_seconds')
    if render_start is not None and (isinstance(render_start, bool) or not isinstance(render_start, (int, float)) or render_start < 0):
        raise ValueError('render_start_seconds must be zero or greater')
    render_duration = job.get('render_duration_seconds')
    if render_duration is not None and (isinstance(render_duration, bool) or not isinstance(render_duration, (int, float)) or not 0 < render_duration <= 3600):
        raise ValueError('render_duration_seconds must be greater than zero and at most 3600')
    if preview is not None and render_duration is not None:
        raise ValueError('Use preview_seconds or render_duration_seconds, not both')
    if job.get('render_range', 'full') not in ('full', 'work_area'):
        raise ValueError('render_range must be full or work_area')
    job.setdefault('images', {})
    job.setdefault('texts', {})
    if job.get('image_fit', 'cover') not in ('cover', 'contain'):
        raise ValueError('image_fit must be cover or contain')
    job['output_dir'] = path(job.get('output_dir', 'output/demo'))
    for key in ('images', 'texts'):
        if not isinstance(job.get(key, {}), dict):
            raise ValueError(key + ' must be an object keyed by composition name')
    for comp, value in job.get('images', {}).items():
        if not isinstance(comp, str) or not comp:
            raise ValueError('Unknown image slot: ' + comp)
        job['images'][comp] = path(value)
        if not Path(job['images'][comp]).is_file():
            raise ValueError('Asset does not exist: ' + job['images'][comp])
    for comp, value in job.get('texts', {}).items():
        if not isinstance(comp, str) or not comp or not isinstance(value, str):
            raise ValueError('Invalid text slot/value: ' + comp)
    media = Path(job['template']).parent
    candidates = {}
    if media.is_dir():
        for p in media.rglob('*'):
            if p.is_file() and not p.name.startswith('.'):
                candidates.setdefault(p.name, []).append(str(p))
    explicit_relink = {name: path(value) for name, value in job.get('relink', {}).items()}
    for value in explicit_relink.values():
        if not Path(value).is_file():
            raise ValueError('Relink asset does not exist: ' + value)
    job['relink'] = {name: paths[0] for name, paths in candidates.items() if len(paths) == 1}
    job['relink'].update(explicit_relink)
    return job


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['validate', 'inspect', 'build', 'render'])
    parser.add_argument('job', nargs='?', default=str(ROOT / 'demo.json'))
    parser.add_argument('--script-only', action='store_true', help='Prepare a standalone JSX file without contacting After Effects')
    args = parser.parse_args()
    # Fail before creating output directories, scripts, or contacting AE.
    if args.mode != 'inspect':
        sys.path.insert(0, str(ROOT.parent))
        from render_policy import enforce
        raw = json.loads(Path(args.job).read_text())
        review = raw.get('selection_review')
        if review and not Path(review).is_absolute():
            review = str((Path(args.job).resolve().parent / review).resolve())
        gate_receipt = enforce(raw, review)
    job = prepare(args.job, args.mode)
    if args.mode != 'inspect': job['selection_gate'] = gate_receipt
    if args.mode == 'validate':
        print(json.dumps(job, indent=2))
        return
    out = Path(job['output_dir'])
    if args.mode != 'inspect':
        out.mkdir(parents=True, exist_ok=False)
    reports = ROOT / 'reports'
    reports.mkdir(exist_ok=True)
    report_path = (out / 'report.json') if args.mode != 'inspect' else reports / (uuid.uuid4().hex + '.json')
    job['report_file'] = str(report_path)
    source = (ROOT / 'documentary.jsx').read_text().replace('/*JOB*/', json.dumps(job, ensure_ascii=True), 1)
    script_path = (out if args.mode != 'inspect' else reports) / 'run-in-after-effects.jsx'
    script_path.write_text(source)
    if args.script_only:
        print(script_path)
        return
    # Pass code as argv, never interpolate job text into shell or AppleScript code.
    bridge = '''on run argv
    with timeout of 21600 seconds
        tell application "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app"
            return DoScript (item 1 of argv)
        end tell
    end timeout
end run'''
    result = subprocess.run(['osascript', '-e', bridge, source], capture_output=True, text=True, timeout=21660)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    # AppleScript can return a status code instead of the script's expression value.
    deadline = time.monotonic() + 30
    while not report_path.exists() and time.monotonic() < deadline:
        time.sleep(0.5)
    if not report_path.exists():
        raise RuntimeError('After Effects did not write a report. Check its startup/error dialogs and scripting file-write permission. Prepared script: ' + str(script_path))
    report = json.loads(report_path.read_text())
    print(json.dumps(report, indent=2))
    if not report.get('ok'):
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
