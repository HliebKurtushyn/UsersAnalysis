# Дані про поведінку користувачів

Проєкт використовує датасет **E-commerce behavior data from a
multi-category store** за листопад 2019 року. Він містить події взаємодії
користувачів з товарами: перегляди, додавання до кошика та покупки.

Джерело:
[Kaggle — E-commerce behavior data](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store)

## Розташування файлу

Завантажений файл потрібно покласти сюди:

```text
data/
└── raw/
    └── 2019-Nov.csv
```

Файл не зберігається в репозиторії, оскільки це великий набір даних.
Директорії `data/raw/` і `data/cleaned/` можуть створюватися локально під час
роботи з pipeline.

## Структура CSV

Для роботи проєкту потрібні такі колонки:

| Колонка | Призначення |
|---|---|
| `event_type` | тип події: `view`, `cart` або `purchase` |
| `user_id` | ідентифікатор користувача |
| `event_time` | дата й час події |
| `product_id` | ідентифікатор товару |
| `category_code` | категорія товару |
| `brand` | бренд товару |
| `price` | ціна товару |

Один рядок CSV описує одну подію. Один користувач або товар може мати багато
рядків із різними типами взаємодії.

## Як дані проходять pipeline

1. `data_loader.py` читає CSV і перевіряє наявність обов’язкових колонок.
2. `eda_and_cleaning.py` видаляє дублікати, перетворює `event_time`, заповнює
   пропущені `brand` і `category_code` значенням `Unknown`.
3. Підготовлений файл зберігається як `data/cleaned/2019-Nov.csv`.
4. `feature_engineering.py` агрегує події:
   - `view` → `views`;
   - `cart` → `carts`;
   - `purchase` → `purchases`.
5. На цих ознаках будуються user/product features, кластери та ML-модель.

Під час підготовки можна обробити не весь файл, а лише перші `n` рядків. Це
зручно для швидкої перевірки:

```python
from ml_pipeline.prepare_data import prepare_data

prepare_data(rows=100_000)
```

Повний опис запуску та подальшого використання даних є в
[основному README](../README.md#дані-для-ml-пайплайна).
