import argparse
import sys
import os
from collections import deque, defaultdict

def parse_dependencies(cargo_path):
    """Парсит секцию [dependencies] из Cargo.toml"""
    dependencies = []
    in_deps_section = False

    try:
        with open(cargo_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.startswith("[dependencies]"):
                    in_deps_section = True
                    continue
                if in_deps_section and line.startswith("[") and not line.startswith("[dependencies]"):
                    break
                if in_deps_section and line and not line.startswith("#") and "=" in line:
                    parts = line.split("=", 1)
                    name = parts[0].strip()
                    version = parts[1].strip().strip('"').strip()
                    dependencies.append((name, version))
    except FileNotFoundError:
        print(f"❌ Ошибка: файл {cargo_path} не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка при чтении зависимостей: {e}")
        sys.exit(1)
    return dependencies


def parse_test_graph(path):
    """Читает тестовый файл зависимостей в формате:
       A: B C
       B: D
       C:
       D:
    """
    graph = {}
    try:
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                pkg, deps = line.split(":", 1)
                pkg = pkg.strip()
                deps_list = [d.strip() for d in deps.split() if d.strip()]
                graph[pkg] = deps_list
    except FileNotFoundError:
        print(f"❌ Ошибка: файл {path} не найден.")
        sys.exit(1)
    return graph


def build_dependency_graph(graph, start_pkg):
    """Обходит граф зависимостей в ширину (BFS)"""
    visited = set()
    queue = deque([start_pkg])
    order = []

    while queue:
        pkg = queue.popleft()
        if pkg in visited:
            continue
        visited.add(pkg)
        order.append(pkg)
        for dep in graph.get(pkg, []):
            if dep not in visited:
                queue.append(dep)
    return order


def load_order_for_package(graph, start_pkg):
    """Вычисляет порядок загрузки зависимостей (топосорт + проверка циклов)"""
    indegree = defaultdict(int)
    reverse_graph = defaultdict(list)

    all_nodes = set(graph.keys())
    for pkg, deps in graph.items():
        all_nodes.update(deps)
        for dep in deps:
            reverse_graph[dep].append(pkg)
            indegree[pkg] += 1
        if pkg not in indegree:
            indegree[pkg] = 0
    for node in all_nodes:
        indegree[node] += 0

    queue = deque([node for node in indegree if indegree[node] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in reverse_graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    has_cycle = len(order) < len(indegree)
    cycle_nodes = [n for n in indegree if indegree[n] > 0] if has_cycle else []
    if not order and has_cycle:
        order = list(cycle_nodes)

    order = list(order)
    return order, has_cycle, cycle_nodes


def main():
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей (этап 4 — дополнительные операции)"
    )

    parser.add_argument("--package", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--url", required=False, help="URL-адрес репозитория")
    parser.add_argument("--path", required=False, help="Путь к тестовому репозиторию или файлу зависимостей")
    parser.add_argument("--mode", required=True, choices=["real", "test"], help="Режим работы (real или test)")
    parser.add_argument("--version", required=True, help="Версия пакета")
    parser.add_argument("--output", required=True, help="Имя файла с изображением графа")
    parser.add_argument("--operation", required=False, choices=["bfs", "load-order"], default="bfs",
                        help="Тип операции: bfs (обход) или load-order (порядок загрузки)")

    args = parser.parse_args()

    # Проверки ошибок
    if args.mode == "real" and not args.url:
        print("❌ Ошибка: для режима 'real' нужно указать --url")
        sys.exit(1)
    if args.mode == "test" and not args.path:
        print("❌ Ошибка: для режима 'test' нужно указать --path (путь к test_repo.txt)")
        sys.exit(1)

    # Вывод параметров
    print("Настройки пользователя:")
    print(f"package = {args.package}")
    print(f"url = {args.url or '-'}")
    print(f"path = {args.path}")
    print(f"mode = {args.mode}")
    print(f"version = {args.version}")
    print(f"output = {args.output}")
    print(f"operation = {args.operation}")
    print()

    # Работа в тестовом режиме
    if args.mode == "test":
        if args.path.endswith(".txt"):
            graph = parse_test_graph(args.path)
            print("Тестовый граф зависимостей:")
            for pkg, deps in graph.items():
                deps_str = ", ".join(deps) if deps else "(нет зависимостей)"
                print(f"{pkg} -> {deps_str}")
            print()

            if args.operation == "bfs":
                order = build_dependency_graph(graph, args.package)
                print("Порядок обхода зависимостей (BFS):")
                print(" -> ".join(order))
            elif args.operation == "load-order":
                order, has_cycle, cycle_nodes = load_order_for_package(graph, args.package)
                print("Порядок загрузки зависимостей (deps сначала):")
                print(" -> ".join(order))
                if has_cycle:
                    print()
                    print("⚠️ Обнаружены циклические зависимости:")
                    print(", ".join(cycle_nodes))
                    print("Порядок загрузки может быть неполным из-за цикла.")
                else:
                    print("\n Циклов не обнаружено — порядок корректен.")
        else:
            cargo_path = os.path.join(args.path, "Cargo.toml")
            dependencies = parse_dependencies(cargo_path)
            print("Найденные прямые зависимости:")
            if dependencies:
                for name, version in dependencies:
                    print(f"{name} = {version}")
            else:
                print("(нет прямых зависимостей)")
    else:
        print("Режим 'real' пока не реализован.")


if __name__ == "__main__":
    main()
