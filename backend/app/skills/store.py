from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

import yaml


VALID_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
ALLOWED_SUBDIRS = {"references", "templates", "scripts", "assets"}


class SkillStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.skills_dir = root / "skills"
        self.archive_dir = self.skills_dir / ".archive"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[dict[str, Any]]:
        items = []
        for skill_md in sorted(self.skills_dir.rglob("SKILL.md")):
            if ".archive" in skill_md.parts:
                continue
            content = skill_md.read_text(encoding="utf-8")
            meta = self._frontmatter(content)
            items.append(
                {
                    "name": skill_md.parent.name,
                    "path": str(skill_md.parent),
                    "description": meta.get("description", ""),
                }
            )
        return items

    def view(self, name: str) -> dict[str, Any]:
        path = self._find(name)
        content = (path / "SKILL.md").read_text(encoding="utf-8")
        return {"name": name, "path": str(path), "content": content, "files": self._files(path)}

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        terms = [term.lower() for term in re.findall(r"[a-zA-Z0-9_/-]+", query) if len(term) > 2]
        scored = []
        for item in self.list():
            content = self.view(item["name"])["content"]
            haystack = f"{item['name']} {item.get('description', '')} {content}".lower()
            score = sum(1 for term in terms if term in haystack)
            if score:
                scored.append((score, {**item, "content": content}))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def create(self, name: str, description: str, content: str | None = None) -> dict[str, Any]:
        self._validate_name(name)
        path = self.skills_dir / name
        if path.exists():
            raise FileExistsError(f"Skill already exists: {name}")
        path.mkdir(parents=True)
        for subdir in ALLOWED_SUBDIRS:
            (path / subdir).mkdir()
        body = content or self._default_content(name, description)
        (path / "SKILL.md").write_text(body, encoding="utf-8")
        return self.view(name)

    def patch(self, name: str, old: str, new: str, file_path: str = "SKILL.md") -> dict[str, Any]:
        target = self._resolve_file(name, file_path)
        text = target.read_text(encoding="utf-8")
        if old not in text:
            raise ValueError("Patch target text not found")
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        return self.view(name)

    def write_file(self, name: str, file_path: str, content: str) -> dict[str, Any]:
        target = self._resolve_file(name, file_path, allow_create=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return self.view(name)

    def archive(self, name: str, reason: str = "") -> dict[str, Any]:
        path = self._find(name)
        destination = self.archive_dir / name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(path), str(destination))
        if reason:
            (destination / "ARCHIVED_REASON.txt").write_text(reason, encoding="utf-8")
        return {"name": name, "archived": True, "path": str(destination)}

    def _find(self, name: str) -> Path:
        self._validate_name(name)
        path = self.skills_dir / name
        if not (path / "SKILL.md").exists():
            raise FileNotFoundError(f"Skill not found: {name}")
        return path

    def _resolve_file(self, name: str, file_path: str, allow_create: bool = False) -> Path:
        root = self._find(name)
        if file_path == "SKILL.md":
            return root / "SKILL.md"
        candidate = (root / file_path).resolve()
        if root.resolve() not in [candidate, *candidate.parents]:
            raise PermissionError("Skill path traversal blocked")
        if Path(file_path).parts[0] not in ALLOWED_SUBDIRS:
            raise ValueError(f"Skill file must be under one of: {sorted(ALLOWED_SUBDIRS)}")
        if not allow_create and not candidate.exists():
            raise FileNotFoundError(str(candidate))
        return candidate

    @staticmethod
    def _validate_name(name: str) -> None:
        if not VALID_NAME.match(name):
            raise ValueError(f"Invalid skill name: {name}")

    @staticmethod
    def _frontmatter(content: str) -> dict[str, Any]:
        if not content.startswith("---"):
            return {}
        end = content.find("\n---", 3)
        if end == -1:
            return {}
        data = yaml.safe_load(content[3:end]) or {}
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _files(path: Path) -> list[str]:
        return [str(item.relative_to(path)).replace("\\", "/") for item in path.rglob("*") if item.is_file()]

    @staticmethod
    def _default_content(name: str, description: str) -> str:
        return (
            f"---\nname: {name}\ndescription: {description}\n---\n\n"
            f"# {name}\n\n"
            "Use this skill when the task matches the description above.\n\n"
            "## Procedure\n\n"
            "- Identify the reusable class of work.\n"
            "- Apply the steps that were proven in prior sessions.\n"
            "- Update this skill when the procedure changes.\n"
        )
