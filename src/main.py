
import argparse
from pathlib import Path
from urllib.parse import urlparse

#создание парсера
def create_parser():
    parser = argparse.ArgumentParser(
        description="Визуализатор зависимостей npm-пакетов"
    )
    parser.add_argument(
        "--package",
        type=str, required=True,
        help="Название анализируемого npm-пакета"
    )
    parser.add_argument(
        "--repo-url",
        type=str, required=True,
        help="URL репозитория или путь к тестовому файлу"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Использовать тестовый репозиторий"
    )
    parser.add_argument(
        "--output",
        type=str, default="graph.svg",
        help="Имя выходного файла с изображением графа"
    )
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="Выводить зависимости в формате ASCII-дерева"
    )
    parser.add_argument(
        "--max-depth",
        type=int, default=3,
        help="Максимальная глубина анализа зависимостей"
    )
    parser.add_argument(
        "--filter",
        type=str, default="",
        help="Подстрока для исключения пакетов из анализа"
    )
    return parser

#проверка корректности значений
def validate_args(args, parser):
    if not args.package.strip():
        parser.error("Название пакета не может быть пустым")

    if args.max_depth < 0:
        parser.error("Глубина анализа не может быть отрицательной")

    if not args.output.lower().endswith(".svg"):
        parser.error("Выходной файл должен иметь расширение .svg")

    if args.test_mode:
        path = Path(args.repo_url)

        if not path.is_file():
            parser.error("Тестовый файл не существует")
    else:
        url = urlparse(args.repo_url)

        if url.scheme not in ("http", "https") or not url.netloc:
            parser.error("Некорректный URL репозитория")

#вывод параметров в консоль
def print_config(args):
    print(f"Пакет: {args.package}")
    print(f"Репозиторий: {args.repo_url}")
    print(f"Тестовый режим: {args.test_mode}")
    print(f"Выходной файл: {args.output}")
    print(f"ASCII-дерево: {args.ascii_tree}")
    print(f"Максимальная глубина: {args.max_depth}")
    print(f"Фильтр: {args.filter}")


def main():
    parser = create_parser()
    args = parser.parse_args()

    validate_args(args, parser)
    print_config(args)


if __name__ == "__main__":
    main()
