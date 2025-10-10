import argparse
import sys
import os

def parse_dependencies(cargo_path):
    """Парсит секцию [dependencies] из Cargo.toml простым способом"""
    dependencies = []
    in_deps_section = False

    try:
        with open(cargo_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                # Найдена секция [dependencies]
                if line.startswith("[dependencies]"):
                    in_deps_section = True
                    continue

                # Если нашли другую секцию — значит, вышли из блока зависимостей
                if in_deps_section and line.startswith("[") and not line.startswith("[dependencies]"):
                    break

                # Если мы в секции зависимостей — извлекаем пары "имя = версия"
                if in_deps_section and "=" in line:
                    parts = line.split("=")
                    name = parts[0].strip()
                    version = parts[1].strip().strip('"')
                    dependencies.append((name, version))
    except FileNotFoundError:
        print(f"❌ Ошибка: файл {cargo_path} не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка при чтении зависимостей: {e}")
        sys.exit(1)

    return dependencies


def main():
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей (этап 2 — сбор данных)"
    )

    parser.add_argument("--package", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--url", required=False, help="URL-адрес репозитория")
    parser.add_argument("--path", required=False, help="Путь к тестовому репозиторию (по умолчанию текущая папка)")
    parser.add_argument("--mode", required=True, choices=["real", "test"], help="Режим работы (real или test)")
    parser.add_argument("--version", required=True, help="Версия пакета")
    parser.add_argument("--output", required=True, help="Имя файла с изображением графа (например, graph.svg)")

    args = parser.parse_args()

    # Проверки ошибок
    if args.mode == "real" and not args.url:
        print("❌ Ошибка: для режима 'real' нужно указать --url")
        sys.exit(1)
    if args.mode == "test" and not args.path:
        args.path = "."  # если путь не указан — использовать текущую папку

    # Вывод параметров
    print("Настройки пользователя:")
    print(f"package = {args.package}")
    print(f"url = {args.url or '-'}")
    print(f"path = {args.path}")
    print(f"mode = {args.mode}")
    print(f"version = {args.version}")
    print(f"output = {args.output}")
    print()

    # ===== Этап 2: сбор данных о зависимостях =====
    if args.mode == "test":
        cargo_path = os.path.join(args.path, "Cargo.toml")
        dependencies = parse_dependencies(cargo_path)

        print("Найденные прямые зависимости:")
        if dependencies:
            for name, version in dependencies:
                print(f" - {name} = {version}")
        else:
            print(" (нет прямых зависимостей)")
    else:
        print("Режим 'real' пока не реализован на этом этапе.")


if __name__ == "__main__":
    main()
