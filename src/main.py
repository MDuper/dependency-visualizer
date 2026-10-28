import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

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

def fetch_package_data(package, repo_url):
    url = f"{repo_url.rstrip('/')}/{package}"

    try:
        with urlopen(url) as response:
            data = response.read()

    except HTTPError as error:
        print("Произошла ошибка на сервере")
        return None
    except URLError as error:
        print("Ошибка: проблемы с соединением")
        return None

    return data

def get_dependencies(data):
    try:
        package_data = json.loads(data)
        latest_version = package_data["dist-tags"]["latest"]
        version_data = package_data["versions"][latest_version]
        dependencies = version_data.get("dependencies", {})

    except json.JSONDecodeError:
        print("Некорректный JSON")
        return None

    except KeyError as error:
        print(f"Отсутствует необходимый ключ: {error}")
        return None

    return dependencies


def main():
    parser = create_parser()
    args = parser.parse_args()

    validate_args(args, parser)

    if args.test_mode:
        print("Тестовый режим пока не реализован")
        return

    data = fetch_package_data(args.package, args.repo_url)

    if data is None:
        return

    dependencies = get_dependencies(data)

    if dependencies is None:
        return

    if not dependencies:
        print("У пакета нет прямых зависимостей")
        return

    print("Прямые зависимости:")
    for name, version in dependencies.items():
        print(f"{name}: {version}")


if __name__ == "__main__":
    main()
