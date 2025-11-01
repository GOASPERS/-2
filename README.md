# Инструмент визуализации графа зависимостей  
**Этап 5 — Визуализация графа зависимостей**

## Общее описание

Программа представляет собой консольный инструмент для анализа и визуализации графа зависимостей пакетов.  
Она позволяет получать данные о зависимостях из файлов конфигурации, строить граф связей, определять порядок загрузки пакетов и визуализировать их в формате D2/SVG.

Программа полностью работает через параметры командной строки и поддерживает два режима работы:  
- **test** — используется локальный файл (`Cargo.toml` или тестовый `.txt`)  
- **real** — предназначен для работы с настоящими репозиториями (через crates.io API)

На данном этапе реализована визуализация графа зависимостей через генерацию D2 и SVG.

## Основные возможности

- Чтение зависимостей из файла `Cargo.toml` (формат пакетов Rust)  
- Работа с тестовыми графами зависимостей в формате `.txt`  
- Получение зависимостей из crates.io через URL  
- Построение графа зависимостей и вывод порядка обхода (**BFS**)  
- Генерация графа зависимостей в формате **D2** и сохранение в **SVG**  
- Сообщение о циклических зависимостях, если они обнаружены  

## Настраиваемые параметры

Программа принимает следующие параметры командной строки:

- **--package** — имя анализируемого пакета  
- **--url** — адрес API crates.io (используется в режиме `real`)  
- **--path** — путь к локальному репозиторию или тестовому файлу зависимостей  
- **--mode** — режим работы программы: `real` или `test`  
- **--version** — версия анализируемого пакета  
- **--output** — имя выходного файла, где будет сохранено изображение графа (например, `graph.svg`)  
- **--operation** — тип выполняемой операции:  
  - `bfs` — обход графа зависимостей  
  - `visualize` — генерация графа зависимостей в формате D2 и SVG  

## Описание работы

В режиме **test** программа анализирует зависимости локально.  
Если указан путь к директории, ищется файл `Cargo.toml`, из которого извлекаются прямые зависимости пакета.  
Если указан путь к `.txt` файлу, используется тестовый граф зависимостей в виде:  
A: B C  
B: D  
C:  
D:  

В режиме **real** программа получает зависимости пакета через API crates.io, используя URL вида:  
`https://crates.io/api/v1/crates/<имя_пакета>/<версия>/dependencies`

При запуске можно выбрать операцию:  

- `bfs` — обход графа в ширину (BFS)  
- `visualize` — генерация графа зависимостей в формате D2 и SVG

При наличии циклических зависимостей программа выводит предупреждение.

## Примеры запуска программы
1
Пример 1 — обычный обход графа (BFS):

```bash
python3 main.py --package A --path test_repo.txt --mode test --version 1.0.0 --output graph.svg --operation bfs
```
Пример 2 — генерация визуализации графа (SVG):

python3 main.py --package A --path test_repo.txt --mode test --version 1.0.0 --output graph.svg --operation visualize


Пример 3 — реализация реального режима с указанием URL и генерацией SVG:

python3 main.py \
    --package sql2viz \
    --version 0.1.0 \
    --mode real \
    --url "https://crates.io/api/v1/crates/sql2viz/0.1.0/dependencies" \
    --output graph_sql2viz.svg


Пример 4 — популярный пакет serde:

python3 main.py \
    --package serde \
    --version 1.0.210 \
    --mode real \
    --url "https://crates.io/api/v1/crates/serde/1.0.210/dependencies" \
    --output graph_serde.svg


Пример 5 — крупный пакет tokio:

python3 main.py \
    --package tokio \
    --version 1.42.0 \
    --mode real \
    --url "https://crates.io/api/v1/crates/tokio/1.42.0/dependencies" \
    --output graph_tokio.svg


Пример 6 — тест ошибки (несуществующая версия):

python3 main.py \
    --package tokio \
    --version 99.99.99 \
    --mode real \
    --url "https://crates.io/api/v1/crates/tokio/99.99.99/dependencies" \
    --output graph_error.svg


Пример 7 — пакет anyhow:

python3 main.py \
    --package anyhow \
    --version 1.0.89 \
    --mode real \
    --url "https://crates.io/api/v1/crates/anyhow/1.0.89/dependencies" \
    --output graph_anyhow.svg

Пример тестового репозитория

Файл test_repo.txt:

A: B C
B: D
C:
D:


Файл Cargo.toml:

[package]
name = "my_crate"
version = "1.0.0"

[dependencies]
serde = "1.0"
rand = "0.8"
regex = "1.5"


Файл main.rs:

fn main() {
    println!("Hello, world!");
}

Примеры результатов

graph_test.d2 — текстовое описание графа зависимостей

graph_test.svg — визуализация графа (создаётся автоматически при наличии утилиты D2)

Возможные ошибки

❌ Файл не найден — неверно указан путь к Cargo.toml или test_repo.txt

❌ Ошибка: не удалось получить данные (status 404) — указан несуществующий пакет или версия

⚠️ Утилита D2 не найдена — установите D2 или используйте только .d2-файл

❌ Для режима 'real' необходимо указать --url — не указан URL crates.io




Пример вывода при использовании режима 'real'
Загружаем данные с https://crates.io/api/v1/crates/sql2viz/0.1.0/dependencies
Найдено зависимостей: 5
 - anyhow
 - duckdb
 - thiserror
 - tokio
 - iced
D2-файл сохранён: graph_sql2viz.d2
success: successfully compiled graph_sql2viz.d2 to graph_sql2viz.svg in 45.452126ms
SVG-файл создан: graph_sql2viz.svg

![](graph_tokio.svg)
