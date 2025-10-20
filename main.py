import argparse
import os
import sys
import subprocess
from collections import deque
import requests


def parse_test_graph(path):
    graph = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            pkg, deps = line.split(":", 1)
            deps_list = [d.strip() for d in deps.split() if d.strip()]
            graph[pkg.strip()] = deps_list
    return graph

def parse_dependencies(cargo_path):
    deps = {}
    in_deps = False
    try:
        with open(cargo_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("[dependencies]"):
                    in_deps = True
                    continue
                if in_deps and line.startswith("["):
                    break
                if in_deps and "=" in line:
                    name, version = line.split("=", 1)
                    deps[name.strip()] = version.strip().strip('"')
    except FileNotFoundError:
        print(f"❌ Файл {cargo_path} не найден.")
        sys.exit(1)
    return {"main": list(deps.keys()), **{k: [] for k in deps.keys()}}

def parse_crates_io(url):
    print(f"Загружаем данные с {url}")
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"❌ Ошибка: не удалось получить данные (status {resp.status_code})")
            sys.exit(1)

        data = resp.json()
        deps = [d["crate_id"] for d in data.get("dependencies", [])]

        print(f"Найдено зависимостей: {len(deps)}")
        if deps:
            for dep in deps:
                print(f" - {dep}")

        return {"main": deps, **{dep: [] for dep in deps}}

    except Exception as e:
        print(f"❌ Ошибка при подключении к API crates.io: {e}")
        sys.exit(1)

def bfs_collect(graph, start):
    visited, queue = set(), deque([start])
    edges = []
    while queue:
        pkg = queue.popleft()
        if pkg in visited:
            continue
        visited.add(pkg)
        for dep in graph.get(pkg, []):
            edges.append((pkg, dep))
            if dep not in visited:
                queue.append(dep)
    return edges

def generate_d2_text(edges):
    lines = [f"{src} -> {dst}" for src, dst in edges]
    return "\n".join(lines)

def save_and_render_d2(d2_text, output_svg):
    d2_path = os.path.splitext(output_svg)[0] + ".d2"
    with open(d2_path, "w", encoding="utf-8") as f:
        f.write(d2_text)
    print(f"D2-файл сохранён: {d2_path}")

    try:
        subprocess.run(["d2", d2_path, output_svg], check=True)
        print(f"SVG-файл создан: {output_svg}")
    except FileNotFoundError:
        print("⚠️  Утилита D2 не найдена. Сохранён только .d2-файл.")
    except subprocess.CalledProcessError:
        print("❌ Ошибка при генерации SVG-файла.")

def main():
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей (этап 5 — визуализация)"
    )
    parser.add_argument("--package", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--url", required=False, help="URL API crates.io для получения зависимостей")
    parser.add_argument("--path", help="Путь к тестовому репозиторию или файлу")
    parser.add_argument("--mode", required=True, choices=["real", "test"], help="Режим работы: real (crates.io) или test")
    parser.add_argument("--version", required=True, help="Версия пакета")
    parser.add_argument("--output", required=True, help="Имя SVG-файла вывода")

    args = parser.parse_args()

    print("Настройки пользователя:")
    print(f"package = {args.package}")
    print(f"mode = {args.mode}")
    print(f"version = {args.version}")
    print(f"url = {args.url or '-'}")
    print(f"path = {args.path or '-'}")
    print(f"output = {args.output}")
    print()

    if args.mode == "real":
        if not args.url:
            print("❌ Для режима 'real' необходимо указать --url (ссылка на crates.io)")
            sys.exit(1)
        graph = parse_crates_io(args.url)
    elif args.mode == "test":
        if not args.path:
            print("❌ Укажите --path для режима test (путь к test_repo.txt или папке).")
            sys.exit(1)
        if args.path.endswith(".txt"):
            graph = parse_test_graph(args.path)
        else:
            graph = parse_dependencies(os.path.join(args.path, "Cargo.toml"))
    else:
        print("❌ Неизвестный режим.")
        sys.exit(1)

    edges = bfs_collect(graph, "main")
    d2_text = generate_d2_text(edges)
    save_and_render_d2(d2_text, args.output)

if __name__ == "__main__":
    main()
