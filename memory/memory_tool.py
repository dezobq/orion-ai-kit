# SPDX-License-Identifier: Apache-2.0
#!/usr/bin/env python3
from pathlib import Path
import shutil
from dataclasses import dataclass, field
from typing import Optional, Tuple

DEFAULT_ROOT = Path('.ai/memories').resolve()
MAX_READ_CHARS = 200_000
MAX_FILE_CHARS = 500_000

@dataclass
class MemoryTool:
    root: Path = field(default_factory=lambda: DEFAULT_ROOT)
    def __post_init__(self):
        self.root.mkdir(parents=True, exist_ok=True)
    def _norm(self, path: str) -> Path:
        if not path: raise ValueError('path is required')
        if path.startswith('/'): path = path.lstrip('/')
        if not path.startswith('memories') and path != 'memories':
            raise ValueError('all paths must begin with /memories')
        p = (self.root / Path(path).relative_to('memories')).resolve()
        if self.root not in p.parents and self.root != p: raise ValueError('path traversal detected')
        return p
    def cmd_view(self, path: str, view_range: Optional[Tuple[int,int]]=None) -> str:
        p = self._norm(path)
        if p.is_dir():
            lines = [f'Directory: /memories{str(p.relative_to(self.root)) if str(p)!=str(self.root) else ""}']
            for e in sorted(p.iterdir()):
                lines.append(f"- {e.name}{'/' if e.is_dir() else ''}")
            return "\n".join(lines)
        if not p.exists(): raise FileNotFoundError('file not found')
        text = p.read_text(errors='ignore')
        if view_range:
            s,e = view_range; L = text.splitlines()
            text = "\n".join(L[max(0,s-1):min(len(L),e)])
        return text[:MAX_READ_CHARS]
    def cmd_create(self, path: str, file_text: str) -> str:
        if len(file_text) > MAX_FILE_CHARS: raise ValueError('file too large')
        p = self._norm(path); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(file_text)
        return f'wrote {len(file_text)} chars to /memories/{p.relative_to(self.root)}'
    def cmd_str_replace(self, path: str, old_str: str, new_str: str) -> str:
        p = self._norm(path)
        if not p.exists(): raise FileNotFoundError('file not found')
        text = p.read_text(); new = text.replace(old_str, new_str)
        if len(new) > MAX_FILE_CHARS: raise ValueError('file too large after replace')
        p.write_text(new); return f'replaced in /memories/{p.relative_to(self.root)}'
    def cmd_insert(self, path: str, insert_line: int, insert_text: str) -> str:
        p = self._norm(path)
        if not p.exists(): raise FileNotFoundError('file not found')
        L = p.read_text().splitlines(); idx = max(0, min(len(L), insert_line-1))
        L[idx:idx] = insert_text.splitlines(); new = "\n".join(L)
        if len(new) > MAX_FILE_CHARS: raise ValueError('file too large after insert')
        p.write_text(new); return f'inserted at line {insert_line} in /memories/{p.relative_to(self.root)}'
    def cmd_delete(self, path: str) -> str:
        p = self._norm(path)
        if p.is_dir(): shutil.rmtree(p); return f'deleted dir /memories/{p.relative_to(self.root)}'
        if p.exists(): p.unlink(); return f'deleted file /memories/{p.relative_to(self.root)}'
        raise FileNotFoundError('not found')
    def cmd_rename(self, old_path: str, new_path: str) -> str:
        a = self._norm(old_path); b = self._norm(new_path); b.parent.mkdir(parents=True, exist_ok=True)
        if not a.exists(): raise FileNotFoundError('old path not found')
        a.rename(b); return f'renamed /memories/{a.relative_to(self.root)} -> /memories/{b.relative_to(self.root)}'
    def handle(self, payload: dict) -> dict:
        cmd = payload.get('command')
        try:
            if cmd=='view': content = self.cmd_view(payload['path'], payload.get('view_range'))
            elif cmd=='create': content = self.cmd_create(payload['path'], payload.get('file_text',''))
            elif cmd=='str_replace': content = self.cmd_str_replace(payload['path'], payload['old_str'], payload['new_str'])
            elif cmd=='insert': content = self.cmd_insert(payload['path'], payload['insert_line'], payload['insert_text'])
            elif cmd=='delete': content = self.cmd_delete(payload['path'])
            elif cmd=='rename': content = self.cmd_rename(payload['old_path'], payload['new_path'])
            else: raise ValueError('unsupported command')
            return {'ok': True, 'content': content}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
