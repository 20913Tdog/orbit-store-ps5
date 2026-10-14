"""Restore the exact, reviewed Orbit commits from verified release sources."""
import argparse
import base64
import hashlib
import io
import json
import os
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path


def git(repo, *args, data=None):
    return subprocess.check_output(["git", "-C", str(repo), *args], input=data).decode().strip()


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def write_file(root, item, data):
    path = Path(item["path"])
    if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
        raise ValueError("Unsafe repository path")
    if blob_sha(data) != item["sha"]:
        raise ValueError("File checksum mismatch: " + item["path"])
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    target.chmod(int(item["mode"], 8) & 0o777)


def record_commit(repo, info):
    actual_tree = git(repo, "write-tree")
    if actual_tree != info["tree"]:
        raise ValueError("Repository tree differs from the reviewed source: " + actual_tree)
    raw = base64.b64decode(info["raw"], validate=True)
    actual = git(repo, "hash-object", "-t", "commit", "-w", "--stdin", data=raw)
    if actual != info["sha"]:
        raise ValueError("Commit checksum mismatch")
    git(repo, "reset", "--hard", actual)
    print("Verified commit", actual, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-tar", type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args()
    instructions = Path(__file__).resolve().parent
    plan = json.loads((instructions / "plan.json").read_text())
    source_manifest = json.loads((instructions / "source-manifest.json").read_text())
    feature_patch = (instructions / "feature.patch").read_bytes()
    if hashlib.sha256(feature_patch).hexdigest() != plan["feature_patch_sha256"]:
        raise ValueError("Feature patch checksum mismatch")
    repository = args.repository.resolve()
    if not args.no_push:
        remote = git(repository, "ls-remote", "origin", "refs/heads/" + plan["branch"])
        current = remote.split()[0] if remote else None
        if current == plan["feature"]["sha"]:
            print("The reviewed commits are already published.")
            return
        if current != plan["base"]:
            raise ValueError("Target branch has changed; refusing to overwrite it")
    if args.source_tar:
        source_bytes = args.source_tar.read_bytes()
    else:
        print("Downloading the pinned official Orbit 1.3.0 source bundle", flush=True)
        with tempfile.TemporaryDirectory(prefix="orbit-source-bundle-") as temporary:
            bundle = Path(temporary) / "source.zip"
            digest = hashlib.sha256()
            request = urllib.request.Request(plan["source_url"], headers={"User-Agent": "Orbit-source-publication"})
            with urllib.request.urlopen(request, timeout=180) as response, bundle.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    digest.update(chunk)
                    output.write(chunk)
            if digest.hexdigest() != plan["bundle_sha256"]:
                raise ValueError("Official source bundle checksum mismatch")
            with zipfile.ZipFile(bundle) as archive:
                source_bytes = archive.read("orbit-store-1.3.0-source.tar.gz")
    if hashlib.sha256(source_bytes).hexdigest() != plan["source_tar_sha256"]:
        raise ValueError("Official source tar checksum mismatch")
    with tempfile.TemporaryDirectory(prefix="orbit-publication-") as temporary:
        working = Path(temporary) / "repository"
        git(repository, "worktree", "add", "--detach", str(working), plan["base"])
        try:
            with tarfile.open(fileobj=io.BytesIO(source_bytes), mode="r:gz") as archive:
                for item in source_manifest:
                    member = archive.getmember("orbit-store-1.3.0/" + item["path"])
                    if not member.isfile():
                        raise ValueError("Unexpected source archive member")
                    write_file(working, item, archive.extractfile(member).read())
            git(working, "add", "--all")
            record_commit(working, plan["import"])
            git(working, "apply", "--index", "-", data=feature_patch)
            record_commit(working, plan["feature"])
            if not args.no_push:
                # A normal fast-forward push rejects intervening branch changes.
                git(working, "push", "origin", plan["feature"]["sha"] + ":refs/heads/" + plan["branch"])
                print("Published the complete reviewed Orbit prototype", flush=True)
            else:
                print("Local verification passed; no remote changes made.", flush=True)
        finally:
            git(repository, "worktree", "remove", "--force", str(working))


if __name__ == "__main__":
    main()
