#!/usr/bin/env python3
"""Verified native Windows source preparation and portable build (no global installs)."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

BINARIES = ('coucou.exe', 'coucou-hook.exe')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_lock(root):
    lock = json.loads((root/'source-lock.json').read_text(encoding='utf-8-sig'))
    if not re.fullmatch(r'[A-Za-z0-9._-]+', lock['version']):
        raise ValueError('Unsafe version in source-lock.json')
    for name, field in [('sendoa.patch', 'patchSha256'), ('desktop.patch', 'desktopPatchSha256')]:
        if digest(root/'patches'/name) != lock[field]:
            raise ValueError(f'Patch checksum mismatch: {name}')
    return lock


def extract_source(archive, destination):
    """Strip the codeload root and reject links, devices and traversal before writing."""
    with tarfile.open(archive, 'r:gz') as tar:
        members = []
        roots = set()
        for member in tar.getmembers():
            path = PurePosixPath(member.name)
            if not path.parts or path.is_absolute() or '..' in path.parts or '\\' in member.name or ':' in member.name:
                raise ValueError('Unsafe source archive path')
            roots.add(path.parts[0])
            if not member.isfile() and not member.isdir():
                raise ValueError('Source archive contains a link or special file')
            relative = Path(*path.parts[1:])
            if len(path.parts) > 1:
                members.append((member, relative))
        if len(roots) != 1:
            raise ValueError('Expected one source archive root')
        for member, relative in members:
            target = destination/relative
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError('Source archive escapes destination')
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source, target.open('wb') as output:
                    shutil.copyfileobj(source, output)


def run(command, cwd):
    subprocess.run([str(arg) for arg in command], cwd=cwd, check=True)


def prepare(root, lock, archive=None):
    build = root/'.build'; build.mkdir(exist_ok=True)
    destination = build/('source-windows-' + lock['version'])
    if destination.exists():
        raise ValueError(f'{destination} already exists; preserve it or move it before rebuilding')
    with tempfile.TemporaryDirectory(prefix='windows-source-', dir=build) as temp:
        temp = Path(temp)
        if archive is None:
            archive = temp/'source.tar.gz'
            with urllib.request.urlopen(lock['sourceUrl'], timeout=120) as response, archive.open('wb') as output:
                shutil.copyfileobj(response, output)
        if digest(archive) != lock['sourceSha256']:
            raise ValueError('Source archive checksum mismatch')
        source = temp/'source'; source.mkdir()
        extract_source(archive, source)
        run(['git', '-c', 'core.autocrlf=false', 'init', '--quiet'], source)
        run(['git', 'config', 'core.autocrlf', 'false'], source)
        # A nested git repo prevents git apply from finding the parent setup repo.
        for name in ('sendoa.patch', 'desktop.patch'):
            run(['git', 'apply', '--check', root/'patches'/name], source)
            run(['git', 'apply', root/'patches'/name], source)
        source.rename(destination)
    return destination


def verify_release(release, lock):
    if (release/'VERSION').read_text(encoding='utf-8').strip() != lock['version']:
        raise ValueError('Release version does not match source-lock.json')
    if json.loads((release/'source-lock.json').read_text(encoding='utf-8-sig')) != lock:
        raise ValueError('Release provenance does not match source-lock.json')
    expected = set(BINARIES)
    if (release/'codex-bridge.mjs').exists():
        expected.add('codex-bridge.mjs')
    seen = set()
    for line in (release/'SHA256SUMS').read_text(encoding='utf-8').splitlines():
        checksum, name = line.split()
        if name not in expected or name in seen:
            raise ValueError('Unexpected or duplicate release checksum')
        seen.add(name)
        if digest(release/name) != checksum:
            raise ValueError(f'Binary checksum mismatch: {name}')
    if seen != expected:
        raise ValueError('Missing binary checksums')


def check_toolchain():
    if os.name != 'nt':
        raise ValueError('Native Windows builds require Windows and the MSVC toolchain')
    for executable in ('node', 'npm.cmd', 'cargo', 'rustc', 'cl.exe'):
        if not shutil.which(executable):
            raise ValueError(f'Missing {executable}. Use an x64 Native Tools/Developer PowerShell with Node, Rust MSVC and Windows SDK installed.')
    if int(subprocess.check_output(['node', '--version'], text=True).strip().lstrip('v').split('.')[0]) < 22:
        raise ValueError('Node 22 or newer is required')
    rust = subprocess.check_output(['rustc', '-vV'], text=True)
    if 'host: x86_64-pc-windows-msvc' not in rust:
        raise ValueError('Use the x86_64-pc-windows-msvc Rust host/toolchain')


def build_windows(root, source, lock, bundle=False):
    check_toolchain()
    windows = source/'windows'
    run(['npm.cmd', 'ci'], windows)
    run(['npm.cmd', 'test'], windows)
    run(['cargo', 'test', '--locked', '-p', 'coucou-hook'], windows)
    run(['cargo', 'build', '--release', '--locked', '-p', 'coucou-hook'], windows)
    args = ['npm.cmd', 'run', 'tauri', '--', 'build', '--ci']
    args += ['--bundles', 'nsis,msi'] if bundle else ['--no-bundle']
    run(args + ['--', '--locked'], windows)
    release = root/'.build/release-windows'
    if release.exists():
        raise ValueError(f'{release} already exists; preserve or move it before exporting')
    release.mkdir()
    for name in BINARIES:
        shutil.copy2(windows/'target/release'/name, release/name)
    bridge = windows/'scripts/codex-bridge.mjs'
    if bridge.is_file():
        shutil.copy2(bridge, release/'codex-bridge.mjs')
    for name in ('LICENSE', 'LICENSE-ASSETS.md', 'LICENSE-ANDROID', 'source-lock.json'):
        shutil.copy2(root/name, release/name)
    (release/'VERSION').write_text(lock['version']+'\n', encoding='utf-8')
    (release/'SHA256SUMS').write_text(''.join(digest(release/name)+'  '+name+'\n' for name in (*BINARIES, *(['codex-bridge.mjs'] if bridge.is_file() else []))), encoding='utf-8')
    versions = {}
    for executable in ('node', 'npm.cmd', 'cargo', 'rustc'):
        versions[executable] = subprocess.check_output([executable, '--version'], text=True).strip()
    (release/'BUILD-INFO.json').write_text(json.dumps({'platform':'windows', 'tools':versions, 'upstreamCommit':lock['upstreamCommit']}, indent=2)+'\n', encoding='utf-8')
    if bundle:
        shutil.copytree(windows/'target/release/bundle', release/'bundle')
    verify_release(release, lock)
    return release


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--bundle', action='store_true', help='Also produce NSIS/MSI installers')
    parser.add_argument('--archive', type=Path, help='Use a local archive, still SHA-256 verified')
    parser.add_argument('--verify-release', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    lock = read_lock(root)
    if args.verify_release:
        verify_release(root/'.build/release-windows', lock)
        print('Windows release checksums and provenance verified.')
    elif args.dry_run:
        print(f"Would verify/download {lock['sourceUrl']}, apply both pinned patches and build {lock['version']} for Windows.")
        print('Requires Git, Python 3.11+, Node 22+, Rust MSVC, Visual Studio C++ Build Tools + Windows SDK; runtime needs WebView2.')
        print('No global tools are installed automatically. Output: .build/release-windows')
    else:
        if not args.prepare_only:
            check_toolchain()
        source = prepare(root, lock, args.archive)
        print(f'Verified source and patches: {source}')
        if not args.prepare_only:
            print(f'Windows build: {build_windows(root, source, lock, args.bundle)}')

if __name__ == '__main__':
    main()
