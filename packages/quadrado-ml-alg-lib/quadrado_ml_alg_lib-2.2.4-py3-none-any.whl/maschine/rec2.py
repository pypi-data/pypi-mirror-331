# %%
import numpy as np
import pandas as pd
from implicit.nearest_neighbours import TFIDFRecommender
from rectools import Columns
from rectools.dataset import Dataset
from rectools.metrics import (
    Precision, NDCG, Serendipity, IntraListDiversity,
    calc_metrics
)
from rectools.metrics.distances import PairwiseHammingDistanceCalculator
from rectools.models import *

# %%
# ======================================================
# 1. ПРЕДОБРАБОТКА ДАННЫХ
# ======================================================

# Загрузка данных о взаимодействиях пользователей
ratings = pd.read_csv(
    "ratings.dat",
    sep="::",
    engine="python",
    header=None,
    names=[Columns.User, Columns.Item, Columns.Weight, Columns.Datetime],
)
print("Raw ratings data:")
print(f"Shape: {ratings.shape}")
print(ratings.head(), "\n")

# Преобразование временной метки
ratings["datetime"] = pd.to_datetime(ratings["datetime"] * 10 ** 9)
print("Datetime range:", ratings["datetime"].min(), "-", ratings["datetime"].max())

# Загрузка метаданных фильмов
movies = pd.read_csv(
    "movies.dat",
    sep="::",
    engine="python",
    header=None,
    names=[Columns.Item, "title", "genres"],
    encoding_errors="ignore",
)
print("\nMovies metadata:")
print(f"Shape: {movies.shape}")
print(movies.head(), "\n")

# Разделение данных на train/test по временной метке
split_dt = pd.Timestamp("2003-02-01")
df_train = ratings.loc[ratings["datetime"] < split_dt]
df_test = ratings.loc[ratings["datetime"] >= split_dt]
print(f"Train size: {len(df_train)}, Test size: {len(df_test)}")

# Создание Dataset для обучения
dataset = Dataset.construct(df_train)


# %%
# ======================================================
# 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ОЦЕНКИ
# ======================================================

def prepare_genre_features(movies_df):
    """Подготовка жанровых признаков для расчета разнообразия рекомендаций"""
    movies_df = movies_df.copy()
    movies_df["genre"] = movies_df["genres"].str.split("|")
    genre_exploded = movies_df[[Columns.Item, "genre"]].set_index(Columns.Item).explode("genre")
    return pd.get_dummies(genre_exploded, prefix="", prefix_sep="").groupby(Columns.Item).sum()


genre_dummies = prepare_genre_features(movies)


def calculate_metrics(model_name, reco, df_test, df_train):
    """Вычисление и сохранение метрик качества рекомендаций"""
    # Общие параметры метрик
    k = 10
    catalog = df_train[Columns.Item].unique()

    # Инициализация метрик
    metrics = {
        "Precision@10": Precision(k=k, r_precision=True),
        "Serendipity@10": Serendipity(k=k),
        "NDCG@10": NDCG(k=k, log_base=3),
        "ILD@10": IntraListDiversity(
            k=k,
            distance_calculator=PairwiseHammingDistanceCalculator(genre_dummies)
        )
    }

    # Вычисление значений
    results = {}
    for name, metric in metrics.items():
        if name == "Serendipity@10":
            results[name] = metric.calc(
                reco=reco,
                interactions=df_test,
                prev_interactions=df_train,
                catalog=catalog
            )
        else:
            results[name] = metric.calc(reco=reco, interactions=df_test)

    # Добавление информации о модели
    results["Model"] = model_name

    return results


# %%
# ======================================================
# 3. ОБУЧЕНИЕ МОДЕЛЕЙ И ЭКСПОРТ РЕЗУЛЬТАТОВ
# ======================================================

# Список для сохранения результатов
all_results = []

# ------------------------------------------------------
# 3.1 LightFM модель
# ------------------------------------------------------
from rectools.models import LightFMWrapperModel
from lightfm import LightFM

model = LightFMWrapperModel(
    model=LightFM(no_components=30)  # Размерность векторных представлений
model.fit(dataset)
recos = model.recommend(
    users=ratings[Columns.User].unique(),
    dataset=dataset,
    k=5,
    filter_viewed=True,
)

results = calculate_metrics("LightFM", recos, df_test, df_train)
all_results.append(results)
print("\nLightFM Metrics:", results)

# ------------------------------------------------------
# 3.2 SASRec (Transformer-based модель)
# ------------------------------------------------------
model = SASRecModel(
    session_max_len=20,  # Максимальная длина сессии
    n_factors=64,  # Размерность эмбеддингов
    n_heads=4,  # Количество голов внимания
    dropout_rate=0.2,  # Регуляризация
    batch_size=128,  # Размер батча
    epochs=6,  # Количество эпох
)
model.fit(dataset)
recos = model.recommend(
    users=ratings[Columns.User].unique(),
    dataset=dataset,
    k=5,
    filter_viewed=True,
)

results = calculate_metrics("SASRec", recos, df_test, df_train)
all_results.append(results)
print("\nSASRec Metrics:", results)

# ------------------------------------------------------
# 3.3 BERT4Rec (BERT-like модель)
# ------------------------------------------------------
model = BERT4RecModel(
    mask_prob=0.15,  # Вероятность маскирования элементов
    deterministic=True,
)
model.fit(dataset)
recos = model.recommend(
    users=ratings[Columns.User].unique(),
    dataset=dataset,
    k=5,
    filter_viewed=True,
)
results = calculate_metrics("BERT4Rec", recos, df_test, df_train)
all_results.append(results)
print("\nBERT4Rec Metrics:", results)

# %%
# ======================================================
# 4. СОХРАНЕНИЕ И АНАЛИЗ РЕЗУЛЬТАТОВ
# ======================================================

# Конвертация результатов в DataFrame
results_df = pd.DataFrame(all_results).set_index("Model")

# Сохранение в CSV
results_df.to_csv("recommendation_metrics.csv")
print("\nSaved metrics to recommendation_metrics.csv")

# Визуализация результатов
print("\nFinal Results:")
print(results_df)

# %%
# ======================================================
# 5. КОММЕНТАРИИ И ПРИМЕНЕНИЕ
# ======================================================
'''
Где может применяться:
1. Соревнования по рекомендательным системам (MovieLens, Goodreads и др.)
2. Задачи прогнозирования пользовательских предпочтений
3. Оптимизация персонализации контента в e-commerce
4. Оценка качества алгоритмов в научных исследованиях
'''