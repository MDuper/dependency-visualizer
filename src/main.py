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
        print(f"HTTP-ошибка: {error.code}")
        return None

    except URLError as error:
        print(f"Ошибка соединения: {error.reason}")
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

def build_dependency_graph(
        package, repo_url, max_depth, filter_text, test_mode):
    graph = {}
    stack = [(package, 0)]
    visited_depth = {}
    test_graph = load_test_graph(repo_url) if test_mode else None
    if test_mode and test_graph is None: return None

    while stack:
        current, depth = stack.pop()

        if current in visited_depth:
            if visited_depth[current] <= depth:
                continue

        visited_depth[current] = depth

        if depth == max_depth:
            graph[current] = []
            continue

        if test_mode:
            dependencies = test_graph.get(current, [])
        else:
            data = fetch_package_data(current, repo_url)
            if data is None:
                return None

            dependencies = get_dependencies(data)
            if dependencies is None:
                return None

        names = [
            name for name in dependencies
            if not filter_text or filter_text not in name
        ]

        graph[current] = names

        for dependency in names:
            stack.append((dependency, depth + 1))

    return graph

def load_test_graph(path):
    graph = {}

    try:
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                name, dependencies = line.split(":", 1)
                graph[name.strip()] = dependencies.split()

    except OSError as error:
        print(f"Ошибка чтения файла: {error}")
        return None

    except ValueError:
        print("Некорректный формат тестового файла")
        return None

    return graph


def main():
    parser = create_parser()
    args = parser.parse_args()

    validate_args(args, parser)

    graph = build_dependency_graph(
        args.package,
        args.repo_url,
        args.max_depth,
        args.filter,
        args.test_mode
    )

    if graph is None:
        return

if __name__ == "__main__":
    main()
