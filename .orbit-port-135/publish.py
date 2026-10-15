"""Publish the reviewed 1.3.5 source tree without rewriting branch history."""
import argparse
import base64
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path


def git(repo, *args, data=None):
    return subprocess.check_output(["git", "-C", str(repo), *args], input=data).decode().strip()


def safe_path(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
        raise ValueError("Unsafe source path")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-tar", type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args()
    instructions = Path(__file__).resolve().parent
    plan = json.loads((instructions / "plan.json").read_text())
    patch = (instructions / "feature.patch").read_bytes()
    if hashlib.sha256(patch).hexdigest() != plan["patch_sha256"]:
        raise ValueError("Feature patch checksum mismatch")
    repo = args.repository.resolve()
    if not args.no_push:
        current = git(repo, "ls-remote", "origin", "refs/heads/" + plan["branch"]).split()[0]
        if current == plan["result"]["sha"]:
            print("Reviewed integration is already published.")
            return
        if current != plan["base"]:
            raise ValueError("Development branch changed; refusing to overwrite it")
    if args.source_tar:
        source = args.source_tar.read_bytes()
    else:
        with tempfile.TemporaryDirectory(prefix="orbit-135-source-") as tmp:
            bundle = Path(tmp) / "source.zip"
            digest = hashlib.sha256()
            with urllib.request.urlopen(plan["source_url"], timeout=180) as response, bundle.open("wb") as out:
                while chunk := response.read(1024 * 1024):
                    digest.update(chunk)
                    out.write(chunk)
            if digest.hexdigest() != plan["bundle_sha256"]:
                raise ValueError("Official source bundle checksum mismatch")
            with zipfile.ZipFile(bundle) as archive:
                source = archive.read(plan["tar_name"])
    if hashlib.sha256(source).hexdigest() != plan["source_tar_sha256"]:
        raise ValueError("Official source tar checksum mismatch")
    with tempfile.TemporaryDirectory(prefix="orbit-135-publication-") as tmp:
        work = Path(tmp) / "repository"
        git(repo, "worktree", "add", "--detach", str(work), plan["base"])
        try:
            for name in plan["reset_paths"]:
                target = work / safe_path(name)
                target.unlink(missing_ok=True)
            with tarfile.open(fileobj=io.BytesIO(source), mode="r:gz") as archive:
                for member in archive.getmembers():
                    if member.isdir():
                        continue
                    if not member.isfile() or not member.name.startswith(plan["prefix"]):
                        raise ValueError("Unexpected source archive member")
                    target = work / safe_path(member.name[len(plan["prefix"]):])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.extractfile(member).read())
                    target.chmod(member.mode & 0o777)
            git(work, "apply", "-", data=patch)
            for item in plan["files"]:
                target = work / safe_path(item["path"])
                data = target.read_bytes()
                actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                if actual != item["sha"] or (target.stat().st_mode & 0o111 != 0) != (item["mode"] == "100755"):
                    raise ValueError("Reviewed source differs: " + item["path"])
            git(work, "add", "--all")
            actual = git(work, "write-tree")
            if actual != plan["result"]["tree"]:
                raise ValueError("Reviewed repository tree differs: " + actual)
            raw = base64.b64decode(plan["result"]["raw"], validate=True)
            commit = git(work, "hash-object", "-t", "commit", "-w", "--stdin", data=raw)
            if commit != plan["result"]["sha"]:
                raise ValueError("Reviewed commit differs")
            if not args.no_push:
                git(work, "push", "origin", commit + ":refs/heads/" + plan["branch"])
            print("Verified Orbit 1.3.5 PC-link integration:", commit, flush=True)
        finally:
            git(repo, "worktree", "remove", "--force", str(work))


if __name__ == "__main__":
    main()
