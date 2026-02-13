from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

@dataclass
class PreprocessorState:
    output_lines: List[str]
    defines: Dict[str, str]
    skip_depth: int = 0
    included_files: set = None # type: ignore
    
    # Для отслеживания маркеров
    current_file: Optional[Path] = None
    last_output_line: int = 0  # последняя строка, которую мы вывели из исходника

def process_file(path: Path, initial_defines: Dict[str, str] = None) -> str: # type: ignore
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    state = PreprocessorState(
        output_lines=[],
        defines=dict(initial_defines or {}),
        included_files=set(),
        current_file=path,
        last_output_line=0
    )
    
    _process_file_into(path, state)
    return "\n".join(state.output_lines) + ("\n" if state.output_lines else "")

def _process_file_into(file_path: Path, state: PreprocessorState):
    if file_path in state.included_files:
        raise ValueError(f"Circular include: {file_path}")
    state.included_files.add(file_path)
    
    lines = file_path.read_text().splitlines()
    i = 0
    
    while i < len(lines):
        line = lines[i]
        original_line_num = i + 1
        
        # Удаляем комментарии ПЕРЕД проверкой на директиву
        clean_line = _remove_comments(line)
        stripped = clean_line.lstrip()
        
        if stripped.startswith('#'):
            # Это директива — парсим её
            directive = stripped[1:].lstrip()
            parts = directive.split(maxsplit=1)
            cmd = parts[0] if parts else ""
            
            if cmd == "define":
                _handle_define(state, directive)
            elif cmd == "undef":
                _handle_undef(state, directive)
            elif cmd == "include":
                _handle_include(state, directive, file_path)
            elif cmd == "ifdef":
                _handle_ifdef(state, directive)
            elif cmd == "ifndef":
                _handle_ifndef(state, directive)
            elif cmd == "else":
                _handle_else(state)
            elif cmd == "endif":
                _handle_endif(state)
            # другие директивы игнорируем
            
            # После обработки директивы — НЕ выводим ничего
            # Но запоминаем, что следующая строка кода будет на original_line_num + 1
            i += 1
            continue
        
        # Обычная строка кода
        if state.skip_depth == 0 and stripped:
            # Проверяем, нужно ли вставить маркер
            should_emit_marker = False
            
            if state.current_file != file_path:
                # Сменили файл (после include)
                state.current_file = file_path
                state.last_output_line = original_line_num - 1
                should_emit_marker = True
            elif original_line_num != state.last_output_line + 1:
                # Скачок в номере строки
                should_emit_marker = True
            
            if should_emit_marker:
                marker = f"# {file_path} {original_line_num}"
                state.output_lines.append(marker)
                state.last_output_line = original_line_num - 1
            
            # Добавляем саму строку кода
            state.output_lines.append(stripped)
            state.last_output_line += 1
        
        i += 1

def _remove_comments(line: str) -> str:
    # Удаляем /* ... */
    while '/*' in line and '*/' in line:
        start = line.find('/*')
        end = line.find('*/', start)
        if end == -1:
            break
        line = line[:start] + line[end+2:]
    # Удаляем // до конца строки
    if '//' in line:
        line = line.split('//', 1)[0]
    return line

# Обработчики директив (упрощённые)
def _handle_define(state: PreprocessorState, directive: str):
    parts = directive.split(maxsplit=2)
    if len(parts) >= 3:
        state.defines[parts[1]] = parts[2]

def _handle_undef(state: PreprocessorState, directive: str):
    parts = directive.split(maxsplit=1)
    if len(parts) >= 2:
        state.defines.pop(parts[1], None)

def _handle_include(state: PreprocessorState, directive: str, current_file: Path):
    # Извлекаем путь: "#include \"file\"" или "#include <file>"
    path_str = directive.split(maxsplit=1)[1].strip('"<>')
    is_system = directive.strip().endswith('>')
    
    if is_system:
        include_path = Path("stdlib") / path_str
    else:
        include_path = (current_file.parent / path_str).resolve()
    
    # Рекурсивно обрабатываем включённый файл
    _process_file_into(include_path, state)

def _handle_ifdef(state: PreprocessorState, directive: str):
    parts = directive.split(maxsplit=1)
    name = parts[1] if len(parts) > 1 else ""
    if name not in state.defines:
        state.skip_depth += 1

def _handle_ifndef(state: PreprocessorState, directive: str):
    parts = directive.split(maxsplit=1)
    name = parts[1] if len(parts) > 1 else ""
    if name in state.defines:
        state.skip_depth += 1

def _handle_else(state: PreprocessorState):
    # Инвертируем самый верхний уровень пропуска
    pass  # для v0 можно упростить

def _handle_endif(state: PreprocessorState):
    if state.skip_depth > 0:
        state.skip_depth -= 1