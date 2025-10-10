import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей (этап 1)"
    )

    parser.add_argument("--package", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--url", required=False, help="URL-адрес репозитория")
    parser.add_argument("--path", required=False, help="Путь к тестовому репозиторию")
    parser.add_argument("--mode", required=True, choices=["real", "test"], help="Режим работы (real или test)")
    parser.add_argument("--version", required=True, help="Версия пакета")
    parser.add_argument("--output", required=True, help="Имя файла с изображением графа (например, graph.svg)")

    args = parser.parse_args()

    # Проверки ошибок
    if args.mode == "real" and not args.url:
        print("❌ Ошибка: для режима 'real' нужно указать --url")
        sys.exit(1)
    if args.mode == "test" and not args.path:
        print("❌ Ошибка: для режима 'test' нужно указать --path")
        sys.exit(1)

    # Вывод параметров
    print("🔧 Настройки пользователя:")
    print(f"package = {args.package}")
    print(f"url = {args.url or '-'}")
    print(f"path = {args.path or '-'}")
    print(f"mode = {args.mode}")
    print(f"version = {args.version}")
    print(f"output = {args.output}")

if __name__ == "__main__":
    main()
