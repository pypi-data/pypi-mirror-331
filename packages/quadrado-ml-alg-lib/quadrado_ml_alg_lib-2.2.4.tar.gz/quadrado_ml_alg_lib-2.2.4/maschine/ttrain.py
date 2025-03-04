# %% [markdown]
# # ***REGRESSION***

# %%
!pip install catboost
!pip install optuna

# %%
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor, Pool
from sklearn.metrics import mean_squared_error
import optuna
from sklearn.model_selection import train_test_split

# %%
train = pd.read_csv('/content/train (6).csv', index_col='Id')
train.head(3)

# %%
columns = list(train.columns)
categorical_features = []
for i in columns:
    if str(type(train[i].iloc[0])) == "<class 'str'>":
        categorical_features.append(i)

# %%
missing_values_table = train.isna().sum().reset_index()
missing_values_table.columns = ['Column', 'Missing Values']
missing_values_table['% of Total Values'] = (missing_values_table['Missing Values'] / len(train)) * 100

print(missing_values_table['% of Total Values'])

# %%
a = list(missing_values_table['% of Total Values'])
num = []
cat = []
drp = []
for i in range(len(columns)):
    if missing_values_table['% of Total Values'].iloc[i] > 0:
        if missing_values_table['% of Total Values'].iloc[i] > 40:
            drp.append(str(missing_values_table['Column'].iloc[i]))
        elif str(missing_values_table['Column'].iloc[i]) in categorical_features:
            print(missing_values_table['Column'].iloc[i], missing_values_table['% of Total Values'].iloc[i], "CATEGORICAL")
            cat.append(str(missing_values_table['Column'].iloc[i]))
        else:
            print(missing_values_table['Column'].iloc[i], missing_values_table['% of Total Values'].iloc[i])
            num.append(str(missing_values_table['Column'].iloc[i]))

print(drp)


# %%
train = train.drop(drp, axis = 1)

imputer = SimpleImputer(strategy='mean')
train[num] = imputer.fit_transform(train[num])

imputer_cat = SimpleImputer(strategy='most_frequent')
train[cat] = imputer_cat.fit_transform(train[cat])

# %%
y = train['SalePrice']
x = train.drop('SalePrice', axis =1)

train_x, val_x, train_y, val_y = train_test_split(x, y, test_size=0.2)

# %%
columns = list(train_x.columns)
categorical_features = []
for i in columns:
    if str(type(train[i].iloc[0])) == "<class 'str'>":
        categorical_features.append(i)

# %%
def objective(trial):
    params = {
        "iterations": trial.suggest_int("iterations", 500, 1000),
        "depth": trial.suggest_int("depth", 3, 6),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 5, log=True),
        "loss_function": "RMSE",
        "eval_metric": "RMSE",
        "random_seed": 42,
        "verbose": 0
    }

    model = CatBoostRegressor(**params)
    model.fit(train_x, train_y, eval_set=(val_x, val_y), verbose=1000, cat_features=categorical_features)

    preds = model.predict(val_x)
    rmse = mean_squared_error(val_y, preds)
    rmse = np.sqrt(rmse)
    return rmse

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=20)  # Количество итераций

# 📌 6. Обучение модели с лучшими параметрами
best_params = study.best_params
best_model = CatBoostRegressor(**best_params)
best_model.fit(train_x, train_y, eval_set=(val_x, val_y), verbose=100, cat_features=categorical_features)

# 📌 7. Оценка модели
final_preds = best_model.predict(val_x)
rmse = mean_squared_error(val_y, final_preds)
rmse = np.sqrt(rmse)
print(f"Final RMSE: {rmse}")

# %%
print(best_params)

# %%
test = pd.read_csv('/content/test (3).csv')
test.head(3)

# %%
test = test.drop(drp, axis = 1)

# %%
x = list(val_x.columns)
y = list(test.columns)
for i in y:
    if i not in x:
        print(i)

# %%
missing_values_table = test.isna().sum().reset_index()
missing_values_table.columns = ['Column', 'Missing Values']
missing_values_table['% of Total Values'] = (missing_values_table['Missing Values'] / len(test)) * 100

print(missing_values_table['% of Total Values'])

# %%
a = list(missing_values_table['% of Total Values'])
num = []
cat = []
drp = []
for i in range(len(columns)):
    if missing_values_table['% of Total Values'].iloc[i] > 0:
        if missing_values_table['% of Total Values'].iloc[i] > 40:
            drp.append(str(missing_values_table['Column'].iloc[i]))
        elif str(missing_values_table['Column'].iloc[i]) in categorical_features:
            print(missing_values_table['Column'].iloc[i], missing_values_table['% of Total Values'].iloc[i], "CATEGORICAL")
            cat.append(str(missing_values_table['Column'].iloc[i]))
        else:
            print(missing_values_table['Column'].iloc[i], missing_values_table['% of Total Values'].iloc[i])
            num.append(str(missing_values_table['Column'].iloc[i]))

# %%
imputer = SimpleImputer(strategy='mean')
test[num] = imputer.fit_transform(test[num])

imputer_cat = SimpleImputer(strategy='most_frequent')
test[cat] = imputer_cat.fit_transform(test[cat])

# %%
final_preds = best_model.predict(test)

# %%
final = pd.DataFrame({
    "Id": test['Id'],
    "SalePrice": final_preds
})
final.head(3)

# %%
final.to_csv('final_0.csv', index=False)

# %% [markdown]
# # Classification

# %%
!pip install optuna
!pip install catboost

# %%
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, Pool
import optuna
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# %%
train = pd.read_csv('/content/train (7).csv', index_col=False)
train = train.drop('PassengerId', axis=1)
test = pd.read_csv('/content/test (4).csv', index_col=False)

# %%
train.head(3)

# %%
missing_values_table = train.isna().sum().reset_index()
missing_values_table.columns = ['Column', 'Missing Values']
missing_values_table['% of Total Values'] = (missing_values_table['Missing Values'] / len(train)) * 100

print(missing_values_table['% of Total Values'])

# %%
columns = list(train.columns)
categorical_features = []
for i in columns:
    if str(type(train[i].iloc[0])) == "<class 'str'>":
        categorical_features.append(i)

# %%
a = list(missing_values_table['% of Total Values'])
num = []
cat = []
drp = []
for i in range(len(a)):
    if missing_values_table['% of Total Values'].iloc[i] > 0:
        if missing_values_table['% of Total Values'].iloc[i] > 40:
            drp.append(str(missing_values_table['Column'].iloc[i]))
        elif str(missing_values_table['Column'].iloc[i]) in categorical_features:
            print(missing_values_table['Column'].iloc[i], missing_values_table['% of Total Values'].iloc[i], "CATEGORICAL")
            cat.append(str(missing_values_table['Column'].iloc[i]))
        else:
            print(missing_values_table['Column'].iloc[i], missing_values_table['% of Total Values'].iloc[i])
            num.append(str(missing_values_table['Column'].iloc[i]))

print(drp)

# %%
train = train.drop(drp, axis = 1)

imputer = SimpleImputer(strategy='mean')
train[num] = imputer.fit_transform(train[num])

imputer_cat = SimpleImputer(strategy='most_frequent')
train[cat] = imputer_cat.fit_transform(train[cat])

# %%
y = train['Survived']
x = train.drop('Survived', axis =1)

train_x, val_x, train_y, val_y = train_test_split(x, y, test_size=0.2)

# %%
columns = list(train_x.columns)
categorical_features = []
for i in columns:
    if str(type(train[i].iloc[0])) == "<class 'str'>":
        categorical_features.append(i)

# %%
def objective(trial):
    params = {
        "iterations": trial.suggest_int("iterations", 500, 2000),
        "depth": trial.suggest_int("depth", 4, 7),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 5, log=True),
        "loss_function": "Logloss",
        "eval_metric": "Accuracy",
        "random_seed": 42,
        "verbose": 0
    }

    model = CatBoostClassifier(**params)
    model.fit(train_x, train_y, eval_set=(val_x, val_y), verbose=1000, cat_features=categorical_features)

    preds = model.predict(val_x)
    accuracy = accuracy_score(val_y, preds)
    return accuracy

# 📌 5. Оптимизация гиперпараметров
study = optuna.create_study(direction="maximize")  # Для классификации — максимизируем accuracy
study.optimize(objective, n_trials=20)  # Количество итераций

# 📌 6. Обучение модели с лучшими параметрами
best_params = study.best_params
best_model = CatBoostClassifier(**best_params)
best_model.fit(train_x, train_y, eval_set=(val_x, val_y), verbose=100, cat_features=categorical_features)

# 📌 7. Оценка модели
final_preds = best_model.predict(val_x)
accuracy = accuracy_score(val_y, final_preds)
print(f"Final Accuracy: {accuracy:.4f}")


# %%
print(best_params)

# %%
test.head(3)

# %%
a = list(test.columns)
num = []
cat = []
for i in range(len(a)):
    if missing_values_table['% of Total Values'].iloc[i] > 0:
        if missing_values_table['% of Total Values'].iloc[i] > 40:
            continue
        elif str(missing_values_table['Column'].iloc[i]) in categorical_features:
            print(missing_values_table['Column'].iloc[i], missing_values_table['% of Total Values'].iloc[i], "CATEGORICAL")
            cat.append(str(missing_values_table['Column'].iloc[i]))
        else:
            print(missing_values_table['Column'].iloc[i], missing_values_table['% of Total Values'].iloc[i])
            num.append(str(missing_values_table['Column'].iloc[i]))


# %%
test = test.drop(drp, axis = 1)

imputer = SimpleImputer(strategy='mean')
test[num] = imputer.fit_transform(test[num])

imputer_cat = SimpleImputer(strategy='most_frequent')
test[cat] = imputer_cat.fit_transform(test[cat])

# %%
id = test['PassengerId']
test = test.drop('PassengerId', axis = 1)

# %%
final_preds = best_model.predict(test)

final = pd.DataFrame({
    "PassengerId": id,
    "Survived": final_preds
})
final.head(3)

# %%
final.to_csv('final_2.csv', index=False)

# %% [markdown]
# # Classification YOLO

# %%
import pandas as pd
import os
from ultralytics import YOLO

DATA_DIR = "path/to/dataset"
TEST_DIR = "path/to/test"
OUTPUT_CSV = "submission.csv"
# n - s - m - l - x
model = YOLO("yolov11x-cls.pt")

model.train(
    data=DATA_DIR,
    epochs=10,
    imgsz=640,
    batch=16,
    lr0=1e-3,
    momentum=0.9,
    augment=True
)

model_path = "runs/train/exp/weights/best.pt"
model = YOLO(model_path)

test_images = [f for f in os.listdir(TEST_DIR) if f.endswith((".jpg", ".png"))]

predictions = []

for img_name in test_images:
    img_path = os.path.join(TEST_DIR, img_name)
    results = model(img_path)

    predicted_class = results[0].probs.top1
    predictions.append((img_name, predicted_class))

df = pd.DataFrame(predictions, columns=["filename", "class"])
df.to_csv(OUTPUT_CSV, index=False)

print(f"✅ Предсказания сохранены в {OUTPUT_CSV}")


# %% [markdown]
# # Detection YOLO

# %%
#Преобразование из csv в yaml
import os
import pandas as pd
from PIL import Image

images_dir = "path/to/images"
csv_file = "path/to/annotations.csv"
output_dir = "path/to/yolo_format"

annotations = pd.read_csv(csv_file)

def normalize_coordinates(x1, y1, x2, y2, img_width, img_height):
    x_center = (x1 + x2) / 2 / img_width
    y_center = (y1 + y2) / 2 / img_height
    width = (x2 - x1) / img_width
    height = (y2 - y1) / img_height
    return x_center, y_center, width, height

for img_name in annotations['filename'].unique():
    img_path = os.path.join(images_dir, img_name)
    img = Image.open(img_path)
    img_width, img_height = img.size

    txt_file = os.path.join(output_dir, img_name.replace('.jpg', '.txt').replace('.png', '.txt'))

    with open(txt_file, 'w') as f:
        img_annotations = annotations[annotations['filename'] == img_name]

        for _, row in img_annotations.iterrows():
            class_id = row['class']
            x_center, y_center, width, height = normalize_coordinates(
                row['x1'], row['y1'], row['x2'], row['y2'], img_width, img_height
            )
            f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")



# %%
# dataset.yaml
# train: path/to/dataset/images/train  # Путь к изображениям для обучения
# val: path/to/dataset/images/val      # Путь к изображениям для валидации
# test: path/to/dataset/images/test    # Путь к изображениям для тестирования

# nc: 3  # Количество классов
# names: ['car', 'person', 'dog']  # Имена классов


# %%
import os
import pandas as pd
from ultralytics import YOLO

# === 1. ПОДГОТОВКА ДАННЫХ ===
DATA_YAML = "path/to/dataset.yaml"  # Файл конфигурации датасета
TEST_DIR = "path/to/test"  # Папка с тестовыми изображениями
OUTPUT_CSV = "submission.csv"  # Файл для предсказаний

# === 2. ОБУЧЕНИЕ YOLOv11 ===
model = YOLO("yolov11n.pt")  # Используем Nano-версию для быстрого обучения

model.train(
    data=DATA_YAML,  # Путь к файлу .yaml с разметкой
    epochs=10,       # Количество эпох
    imgsz=640,       # Размер входного изображения
    batch=16,        # Размер батча
    lr0=1e-3,        # Начальный learning rate
    momentum=0.9,    # Стабильность градиентов
    augment=True     # Включаем встроенные аугментации
)

model_path = "runs/train/exp/weights/best.pt"
model = YOLO(model_path)

test_images = [f for f in os.listdir(TEST_DIR) if f.endswith((".jpg", ".png"))]

predictions = []

for img_name in test_images:
    img_path = os.path.join(TEST_DIR, img_name)
    results = model(img_path)

    for result in results:
        for box in result.boxes.data:
            x1, y1, x2, y2, conf, cls = box.tolist()
            predictions.append((img_name, int(cls), conf, x1, y1, x2, y2))

df = pd.DataFrame(predictions, columns=["filename", "class", "confidence", "x1", "y1", "x2", "y2"])
df.to_csv(OUTPUT_CSV, index=False)

# %% [markdown]
# # Segmentation YOLO

# %%
import pandas as pd
import os
from PIL import Image

csv_path = 'annotations.csv'
images_dir = 'path/to/images'
output_dir = 'yolo_annotations'

# Создаем папку для сохранения аннотаций
os.makedirs(output_dir, exist_ok=True)

data = pd.read_csv(csv_path)

def convert_to_yolo_format(image_width, image_height, x_min, y_min, x_max, y_max):
    x_center = (x_min + x_max) / 2 / image_width
    y_center = (y_min + y_max) / 2 / image_height
    width = (x_max - x_min) / image_width
    height = (y_max - y_min) / image_height
    return x_center, y_center, width, height

for image_name in os.listdir(images_dir):
    image_path = os.path.join(images_dir, image_name)

    with Image.open(image_path) as img:
        image_width, image_height = img.size

    image_annotations = data[data['image_name'] == image_name]

    annotation_file = os.path.join(output_dir, os.path.splitext(image_name)[0] + '.txt')
    with open(annotation_file, 'w') as f:
        for _, row in image_annotations.iterrows():
            class_id = row['class_id']
            x_min, y_min, x_max, y_max = row['x_min'], row['y_min'], row['x_max'], row['y_max']

            x_center, y_center, width, height = convert_to_yolo_format(image_width, image_height, x_min, y_min, x_max, y_max)

            f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")


# %%
# train: path/to/train/images
# val: path/to/val/images
# test: path/to/test/images

# nc: 2  # Количество классов
# names: ['class_0', 'class_1']  # Имена классов

# %%
from ultralytics import YOLO
import os
import pandas as pd

def mask_to_rle(mask):
    mask = mask.astype(np.uint8)

    rle = mask_util.encode(np.asfortranarray(mask))

    rle_string = str(rle['counts'], encoding='utf-8')
    return rle_string

data_path = 'path/to/data.yaml'

model = YOLO('yolo11n-seg.pt')

model.train(data=data_path, epochs=50, imgsz=640, batch_size=16, augment=True)

model.save('yolov11_segmentation_model.pt')

test_path = 'path/to/test/images'
results = model.predict(test_path, save=True)

predictions = []
for image_path, pred in zip(results.files, results.pred):
    file_name = os.path.basename(image_path)

    masks = pred.masks

    if masks is not None:
        for idx, mask in enumerate(masks):
            rle_string = mask_to_rle(mask)
            predictions.append([file_name, idx, rle_string])

df = pd.DataFrame(predictions, columns=['file_name', 'object_id', 'rle'])
df.to_csv('final.csv', index=False)


# %% [markdown]
# # Pose Detection

# %%
from ultralytics import YOLO
import os
import pandas as pd
import numpy as np
from PIL import Image

data_path = 'path/to/data.yaml'

model = YOLO('yolov11-pose.pt')

model.train(data=data_path, epochs=50, imgsz=640, batch_size=16)

test_path = 'path/to/test/images'
results = model.predict(test_path, save=True)

def extract_keypoints(pred):
    keypoints = []
    for i, person in enumerate(pred.keypoints):
        keypoints.append(list(person.xy))
    return keypoints

predictions = []
for image_path, pred in zip(results.files, results.pred):
    file_name = os.path.basename(image_path)

    keypoints = extract_keypoints(pred)

    if keypoints:
        for person_id, person_keypoints in enumerate(keypoints):
            # Сохраняем координаты точек для каждого человека
            for idx, (x, y) in enumerate(person_keypoints):
                predictions.append([file_name, person_id, idx, x, y])  # Добавляем все ключевые точки

df = pd.DataFrame(predictions, columns=['file_name', 'person_id', 'keypoint_id', 'x', 'y'])
df.to_csv('final.csv', index=False)


# %% [markdown]
# # RecSys Surprise

# %%
!pip install scikit-surprise optuna

# %%
import random
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy

# %%
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import cross_validate, GridSearchCV

# 📌 Загружаем MovieLens 100K
data = Dataset.load_builtin('ml-100k')

# 📌 Определяем параметры для Grid Search
param_grid = {
    'n_factors': [50, 100, 150],  # Количество латентных факторов
    'lr_all': [0.002, 0.005, 0.01],  # Скорость обучения
    'reg_all': [0.02, 0.05, 0.1]  # Регуляризация
}

# 📌 Запускаем Grid Search
gs = GridSearchCV(SVD, param_grid, measures=['rmse'], cv=5, n_jobs=-1)
gs.fit(data)

# 📌 Выводим лучшие параметры
print(f"📊 Лучший RMSE: {gs.best_score['rmse']:.4f}")
print(f"🔧 Лучшие параметры: {gs.best_params['rmse']}")

# 📌 Обучаем финальную модель с лучшими параметрами
best_model = SVD(**gs.best_params['rmse'])
cross_validate(best_model, data, cv=5, verbose=True)


# %%
import optuna
import pandas as pd
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import cross_validate

# 📌 Загружаем MovieLens 100K
data = Dataset.load_builtin('ml-100k')

# 📌 Функция для оптимизации гиперпараметров
def objective(trial):
    sim_options = {
        "name": trial.suggest_categorical("name", ["cosine", "pearson", "msd"]),
        "user_based": trial.suggest_categorical("user_based", [True, False])
    }

    model = KNNBasic(k=trial.suggest_int("k", 10, 50), sim_options=sim_options)

    cv_results = cross_validate(model, data, measures=["rmse"], cv=3, verbose=False)
    return cv_results["test_rmse"].mean()

# 📌 Оптимизация гиперпараметров с Optuna
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=30)

# 📌 Выводим лучшие параметры
best_params = study.best_params
print(f"📊 Лучший RMSE: {study.best_value:.4f}")
print(f"🔧 Лучшие параметры: {best_params}")

# 📌 Обучаем финальную модель с лучшими параметрами
final_sim_options = {"name": best_params["name"], "user_based": best_params["user_based"]}
best_model = KNNBasic(k=best_params["k"], sim_options=final_sim_options)

cross_validate(best_model, data, measures=["rmse"], cv=5, verbose=True)


# %% [markdown]
#
#   \begin{array}{|c|c|c|c|c|c|c|c|}\hline\\ \\
#   \mathcal{} & Movielens 100k & RMSE & MAE & Time  \\ \hline\\
#   a & SVD & 0.934 & 0.737 & 0:00:06   \\ \hline\\ \\
#   b & SVD++ (cache_ratings=False) & 0.919 & 0.721 & 0:01:39\\ \hline\\ \\
#   c & SVD++ (cache_ratings=True) & 0.919 & 0.721 & 0:01:22  \\ \hline\\ \\
#   d & NMF & 0.963 & 0.758 & 0:00:06 \\ \hline\\ \\
#   e & Slope One & 0.946 & 0.743 & 0:00:09 \\ \hline\\ \\
#   f & k-NN & 0.98 & 0.774 & 0:00:08 \\ \hline\\ \\
#   g & Slope One & 0.946 & 0.743 & 0:00:09 \\ \hline\\ \\
#   h & Centered k-NN & 0.951 & 0.749 & 0:00:09 \\ \hline\\ \\
#   i & k-NN Baseline & 0.931 & 0.733 & 0:00:13 \\ \hline\\ \\
#   j & Co-Clustering & 0.963 & 0.753 & 0:00:06 \\ \hline\\ \\
#   k & Random & 1.518 & 1.219 & 0:00:01 \\ \hline\\ \\
#   l & Baseline & 0.944 & 0.748 & 0:00:02 \\ \hline
#   \end{array}
#
#
#

# %% [markdown]
# # RecSys Rectools

# %%
!pip install rectools
!pip install rectools[all]
!pip install rectools[torch]

# %%
'''По факту от пользователя требуется обычная таблица, 
где каждая строка отражает одно взаимодействие: в первом столбце id юзера, во втором — айтема,
 а в третьем — скор взаимодействия (например, купил/ не купил). 
 Если есть данные по времени, их тоже можно добавить. '''

# %%
import numpy as np
import pandas as pd

from implicit.nearest_neighbours import TFIDFRecommender

from rectools import Columns
from rectools.dataset import Dataset
from rectools.metrics import (
    Precision,
    NDCG,
    AvgRecPopularity,
    Intersection,
    HitRate,
    SufficientReco,
    DebiasConfig,
    IntraListDiversity,
    Serendipity,
    calc_metrics,
)
from rectools.metrics.distances import PairwiseHammingDistanceCalculator
from rectools.models import *

# %%
ratings = pd.read_csv(
    "ratings.dat",
    sep="::",
    engine="python",  # Because of 2-chars separators
    header=None,
    names=[Columns.User, Columns.Item, Columns.Weight, Columns.Datetime],
)
print(ratings.shape)
ratings.head()

# %%
ratings["datetime"] = pd.to_datetime(ratings["datetime"] * 10 ** 9)
ratings["datetime"].min(), ratings["datetime"].max()

# %%
movies = pd.read_csv(
    "movies.dat",
    sep="::",
    engine="python",  # Because of 2-chars separators
    header=None,
    names=[Columns.Item, "title", "genres"],
    encoding_errors="ignore",
)
print(movies.shape)
split_dt = pd.Timestamp("2003-02-01")
df_train = ratings.loc[ratings["datetime"] < split_dt]
df_test = ratings.loc[ratings["datetime"] >= split_dt]
dataset = Dataset.construct(df_train)

# %%
from rectools.models import LightFMWrapperModel
from lightfm import LightFM

model = LightFMWrapperModel(
        # внутри модели указываем параметр no_components
        # это размезность эмбеддингов, которые выучит модель
        model=LightFM(no_components = 30)
        )

model.fit(dataset)
recos = model.recommend(
    users=ratings[Columns.User].unique(),
    dataset=dataset,
    k=5,
    filter_viewed=True,
)

serendipity = Serendipity(k=10)
precision = Precision(k=10, r_precision=True)  # r_precision means division by min(k, n_user_test_items)
ndcg = NDCG(k=10, log_base=3)

movies["genre"] = movies["genres"].str.split("|")
genre_exploded = movies[["item_id", "genre"]].set_index("item_id").explode("genre")
genre_dummies = pd.get_dummies(genre_exploded, prefix="", prefix_sep="").groupby("item_id").sum()

precision_value = precision.calc(reco=recos, interactions=df_test)
print(f"precision: {precision_value}")

catalog = df_train[Columns.Item].unique()

serendipity_value = serendipity.calc(
    reco=recos,
    interactions=df_test,
    prev_interactions=df_train,
    catalog=catalog
)
print("Serendipity: ", serendipity_value)

print("NDCG: ", ndcg.calc(reco=recos, interactions=df_test))

distance_calculator = PairwiseHammingDistanceCalculator(genre_dummies)
ild = IntraListDiversity(k=10, distance_calculator=distance_calculator)
print("ILD: ", ild.calc(reco=recos))

# %%
model = SASRecModel(
    session_max_len=20,
    loss="softmax",
    n_factors=64,
    n_blocks=1,
    n_heads=4,
    dropout_rate=0.2,
    lr=0.001,
    batch_size=128,
    epochs=6,
    verbose=1,
    deterministic=True,
)

model.fit(dataset)
recos = model.recommend(
    users=ratings[Columns.User].unique(),
    dataset=dataset,
    k=5,
    filter_viewed=True,
)

serendipity = Serendipity(k=10)
precision = Precision(k=10, r_precision=True)  # r_precision means division by min(k, n_user_test_items)
ndcg = NDCG(k=10, log_base=3)

movies["genre"] = movies["genres"].str.split("|")
genre_exploded = movies[["item_id", "genre"]].set_index("item_id").explode("genre")
genre_dummies = pd.get_dummies(genre_exploded, prefix="", prefix_sep="").groupby("item_id").sum()

precision_value = precision.calc(reco=recos, interactions=df_test)
print(f"precision: {precision_value}")

catalog = df_train[Columns.Item].unique()

serendipity_value = serendipity.calc(
    reco=recos,
    interactions=df_test,
    prev_interactions=df_train,
    catalog=catalog
)
print("Serendipity: ", serendipity_value)

print("NDCG: ", ndcg.calc(reco=recos, interactions=df_test))

distance_calculator = PairwiseHammingDistanceCalculator(genre_dummies)
ild = IntraListDiversity(k=10, distance_calculator=distance_calculator)
print("ILD: ", ild.calc(reco=recos))

# %%
model = BERT4RecModel(
    mask_prob=0.15,  # specify probability of masking tokens
    deterministic=True,
)

model.fit(dataset)
recos = model.recommend(
    users=ratings[Columns.User].unique(),
    dataset=dataset,
    k=5,
    filter_viewed=True,
)

serendipity = Serendipity(k=10)
precision = Precision(k=10, r_precision=True)  # r_precision means division by min(k, n_user_test_items)
ndcg = NDCG(k=10, log_base=3)

movies["genre"] = movies["genres"].str.split("|")
genre_exploded = movies[["item_id", "genre"]].set_index("item_id").explode("genre")
genre_dummies = pd.get_dummies(genre_exploded, prefix="", prefix_sep="").groupby("item_id").sum()

precision_value = precision.calc(reco=recos, interactions=df_test)
print(f"precision: {precision_value}")

catalog = df_train[Columns.Item].unique()

serendipity_value = serendipity.calc(
    reco=recos,
    interactions=df_test,
    prev_interactions=df_train,
    catalog=catalog
)
print("Serendipity: ", serendipity_value)

print("NDCG: ", ndcg.calc(reco=recos, interactions=df_test))

distance_calculator = PairwiseHammingDistanceCalculator(genre_dummies)
ild = IntraListDiversity(k=10, distance_calculator=distance_calculator)
print("ILD: ", ild.calc(reco=recos))

# %% [markdown]
#
#   \begin{array}{|c|c|c|c|c|c|c|c|}\hline\\ \\
#   \mathcal{} & Movielens 1m & Precision & Serendipity & NDCG & ILD  \\ \hline\\
#   a & SASRec (6 epochs) & 0.04781 & 4.5023e-05 & 0.03513 & 3.2877   \\ \hline\\ \\
#   b & BERT4Rec & 0.02630 & 1.1553e-05 & 0.03233 & 3.0311 \\ \hline\\ \\
#   c & implicit ALS Wrapper & 0.0515 & 5.4056e-05 & 0.05165 & 2.8392 \\ \hline\\ \\
#   d & implicit BPR-MF Wrapper & 0.02997 & 3.19868e-06 & 0.03615 & 3.86506 \\ \hline\\ \\
#   e & implicit ItemKNN Wrapper & 0.0456 & 3.0093e-05 & 0.04615 & 3.1726 \\ \hline\\ \\
#   f & LightFM Wrapper & 0.05858 & 4.7578e-06 & 0.0604 & 3.6395 \\ \hline\\ \\
#   g & EASE & 0.0367 & 3.0522e-05 & 0.03431 & 2.8200 \\ \hline\\ \\
#   h & PureSVD & 0.05952 & 2.5205e-05 & 0.05248 & 3.0020 \\ \hline\\ \\
#   j & Popular & 0.0330 & 4.1636e-06 & 0.04160 & 3.4595 \\ \hline\\ \\
#   l & Random & 0.0131 & 1.6940e-05 & 0.00487 & 2.6273 \\ \hline
#   \end{array}

# %% [markdown]
# # Детекция ботов

# %%
import numpy as np
import pandas as pd

from implicit.nearest_neighbours import TFIDFRecommender

from rectools import Columns
from rectools.dataset import Dataset
from rectools.metrics import (
    Precision,
    NDCG,
    IntraListDiversity,
    Serendipity,
    calc_metrics,
)
from rectools.metrics.distances import PairwiseHammingDistanceCalculator
from rectools.models import LightFMWrapperModel
from lightfm import LightFM

# 1️⃣ Загрузка данных
ratings = pd.read_csv(
    "ratings.dat",
    sep="::",
    engine="python",
    header=None,
    names=[Columns.User, Columns.Item, Columns.Weight, Columns.Datetime],
)

ratings["datetime"] = pd.to_datetime(ratings["datetime"] * 10 ** 9)

movies = pd.read_csv(
    "movies.dat",
    sep="::",
    engine="python",
    header=None,
    names=[Columns.Item, "title", "genres"],
    encoding_errors="ignore",
)

# 2️⃣ ДЕТЕКЦИЯ БОТОВ

# 2.1 Определение аномальной активности пользователей
user_activity = ratings.groupby(Columns.User).agg(
    num_ratings=(Columns.Item, "count"),  # Количество оценок
    unique_movies=(Columns.Item, "nunique"),  # Уникальные фильмы
    rating_std=(Columns.Weight, "std"),  # Разброс оценок
    first_rating_time=("datetime", "min"),
    last_rating_time=("datetime", "max")
)

# 2.2 Добавляем скорость оценивания (оценки в день)
user_activity["rating_speed"] = user_activity["num_ratings"] / (
    (user_activity["last_rating_time"] - user_activity["first_rating_time"]).dt.days + 1
)

# 2.3 Удаление ботов по критериям:
thresholds = {
    "num_ratings": user_activity["num_ratings"].quantile(0.99),  # > 99-го перцентиля
    "unique_movies": user_activity["unique_movies"].quantile(0.01),  # < 1-го перцентиля
    "rating_std": 0.1,  # Нет разброса в оценках
    "rating_speed": user_activity["rating_speed"].quantile(0.99),  # > 99-го перцентиля
}

bots = user_activity[
    (user_activity["num_ratings"] > thresholds["num_ratings"]) |
    (user_activity["unique_movies"] < thresholds["unique_movies"]) |
    (user_activity["rating_std"] < thresholds["rating_std"]) |
    (user_activity["rating_speed"] > thresholds["rating_speed"])
]

# Удаляем ботов
ratings_cleaned = ratings[~ratings[Columns.User].isin(bots.index)]
print(f"Удалено {len(bots)} подозрительных пользователей.")

# 3️⃣ Деление на train/test
split_dt = pd.Timestamp("2003-02-01")
df_train = ratings_cleaned.loc[ratings_cleaned["datetime"] < split_dt]
df_test = ratings_cleaned.loc[ratings_cleaned["datetime"] >= split_dt]

# 4️⃣ Обучение LightFM
dataset = Dataset.construct(df_train)

model = LightFMWrapperModel(
    model=LightFM(no_components=30)
)
model.fit(dataset)

# 5️⃣ Генерация рекомендаций
recos = model.recommend(
    users=df_test[Columns.User].unique(),
    dataset=dataset,
    k=5,
    filter_viewed=True,
)

# 6️⃣ Оценка метрик
serendipity = Serendipity(k=10)
precision = Precision(k=10, r_precision=True)
ndcg = NDCG(k=10, log_base=3)

movies["genre"] = movies["genres"].str.split("|")
genre_exploded = movies[[Columns.Item, "genre"]].set_index(Columns.Item).explode("genre")
genre_dummies = pd.get_dummies(genre_exploded, prefix="", prefix_sep="").groupby(Columns.Item).sum()

precision_value = precision.calc(reco=recos, interactions=df_test)
print(f"precision: {precision_value}")

catalog = df_train[Columns.Item].unique()
serendipity_value = serendipity.calc(
    reco=recos,
    interactions=df_test,
    prev_interactions=df_train,
    catalog=catalog
)
print("Serendipity: ", serendipity_value)

print("NDCG: ", ndcg.calc(reco=recos, interactions=df_test))

distance_calculator = PairwiseHammingDistanceCalculator(genre_dummies)
ild = IntraListDiversity(k=10, distance_calculator=distance_calculator)
print("ILD: ", ild.calc(reco=recos))


# %% [markdown]
#

# %% [markdown]
# # NLP NIR Natasha

# %%
!pip install natasha

# %%
import pandas as pd
from natasha import (
    Doc,
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
)

# Инициализация компонентов Natasha
segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

# Функция для обработки предложения и извлечения сущностей
def extract_entities(sentence, sentence_id):
    doc = Doc(sentence)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.tag_ner(ner_tagger)

    entities = []
    for span in doc.spans:
        entities.append({
            'sentence_id': sentence_id,
            'entity': span.text,
            'entity_type': span.type
        })
    return entities

# Пример предложения
sentence = "Бурятия и Забайкальский край переданы из Сибирского федерального округа (СФО) в состав Дальневосточного (ДФО). Соответствующий указ подписал президент Владимир Путин, документ опубликован на официальном интернет-портале правовой информации. Этим же указом глава государства поручил руководителю своей администрации утвердить структуру и штатную численность аппаратов полномочных представителей президента в этих двух округах. После исключения Бурятии и Забайкалья в составе СФО остались десять регионов: Алтай, Алтайский край, Иркутская, Кемеровская, Новосибирская, Омская и Томская области, Красноярский край, Тува и Хакасия. Действующим полпредом президента в этом округе является бывший губернатор Севастополя, экс-заместитель командующего Черноморским флотом России Сергей Меняйло. В составе ДФО отныне 11 субъектов. Помимо Бурятии и Забайкалья, это Камчатский, Приморский и Хабаровский края, Амурская, Еврейская автономная, Магаданская и Сахалинская области, а также Якутия и Чукотка. Дальневосточное полпредство возглавляет Юрий Трутнев, совмещающий эту должность с постом вице-премьера в правительстве России. Федеральные округа были созданы в мае 2000 года в соответствии с указом президента Путина."
sentence_id = 1  # ID предложения

# Извлечение сущностей
entities = extract_entities(sentence, sentence_id)

# Создание DataFrame
df = pd.DataFrame(entities)

# Вывод результата
df.head(20)

# %% [markdown]
# # Обработка + Word2Vec + TF-IDF

# %%
!pip install pymorphy3

# %%
categories = {
    "Жизнь человека": {
        "description": "Задания о ценности человеческой жизни, донорстве, осведомленности о заболеваниях",
        "examples": [
            "организация донорской акции",
            "переливание крови",
            "медицинское просвещение",
            "профилактика заболеваний",
            "первая помощь"
        ]
    },
    "Достоинство человека": {
        "description": "Задания об уважении к профессиям и людям разных социальных статусов",
        "examples": [
            "мастер-класс о уважении",
            "социальный статус",
            "профессиональная этика",
            "равенство возможностей",
            "толерантность",
            ""
        ]
    },
    "Права и свободы человека": {
        "description": "Изучение и защита прав человека",
        "examples": [
            "тест о правах человека",
            "конвенция о правах ребенка",
            "правовая грамотность",
            "защита свобод",
            "гражданские права"
        ]
    },
    "Патриотизм": {
        "description": "История государства, предки, патриотические организации",
        "examples": [
            "Россия",
            "Российская федерация",
            "СССР"
            "посещение военного музея",
            "волонтерство 9 мая",
            "история великой отечественной",
            "патриотический флешмоб",
            "герои россии"
        ]
    },
    "Гражданственность": {
        "description": "Процветание общества через личное участие",
        "examples": [
            "субботник",
            "экологическая акция",
            "гражданские инициативы",
            "благоустройство города",
            "общественный контроль"
        ]
    },
    "Служение Отечеству и ответственность за его судьбу": {
        "description": "История отечества и физическая подготовка граждан",
        "examples": [
            "военно-спортивные игры",
            "уроки мужества",
            "здоровье нации",
            "историческая реконструкция",
            "вахта памяти"
        ]
    },
    "Высокие нравственные идеалы": {
        "description": "Культура, идеи и творчество, формирующие мораль",
        "examples": [
            "обсуждение классической литературы",
            "нравственные дилеммы",
            "этические нормы",
            "моральный выбор",
            "духовные ценности",
            "история",
            "страны"
        ]
    },
    "Крепкая семья": {
        "description": "Совместная семейная деятельность и отношения",
        "examples": [
            "семейный квест",
            "генеалогическое древо",
            "совместный пикник",
            "семейные традиции",
            "родительский день"
        ]
    },
    "Созидательный труд": {
        "description": "Обучение практическим навыкам и физическая помощь",
        "examples": [
            "мастер-класс по ремеслам",
            "помощь пожилым",
            "трудовой десант",
            "профессиональные пробы",
            "социальный труд"
        ]
    },
    "Приоритет духовного над материальным": {
        "description": "Помощь нуждающимся вместо материальных благ",
        "examples": [
            "благотворительная акция",
            "помощь приюту",
            "духовные практики",
            "волонтерство в храме",
            "нематериальные ценности"
        ]
    },
    "Гуманизм": {
        "description": "Помощь людям и добрые дела",
        "examples": [
            "волонтерство в приюте",
            "помощь бездомным",
            "добрые письма",
            "поддержка инвалидов",
            "человеколюбие"
        ]
    },
    "Милосердие": {
        "description": "Помощь окружающим и информирование о болезнях",
        "examples": [
            "сбор вещей нуждающимся",
            "помощь пожилым",
            "донорство органов",
            "паллиативная помощь",
            "социальная поддержка"
        ]
    },
    "Справедливость": {
        "description": "Обсуждение и укрепление справедливости",
        "examples": [
            "дебаты о равенстве",
            "правовые квесты",
            "честное распределение",
            "борьба с дискриминацией",
            "равные возможности"
        ]
    },
    "Коллективизм": {
        "description": "Командная работа и взаимодействие в группе",
        "examples": [
            "групповой турпоход",
            "командный квиз",
            "совместный проект",
            "работа в команде",
            "коллективное решение"
        ]
    },
    "Взаимопомощь и взаимоуважение": {
        "description": "Волонтерство и поддержка окружающих",
        "examples": [
            "помощь одноклассникам",
            "тьюторство",
            "шефская помощь",
            "социальное наставничество",
            "взаимная поддержка"
        ]
    },
    "Историческая память и преемственность поколений": {
        "description": "История семьи и страны, связь поколений",
        "examples": [
            "интервью с ветеранами",
            "семейная летопись",
            "музей истории",
            "реконструкция событий",
            "устная история"
        ]
    },
    "Единство народов России": {
        "description": "Культурное многообразие и национальные традиции",
        "examples": [
            "фестиваль культур",
            "этнографический музей",
            "национальные ремесла",
            "межнациональный диалог",
            "традиционные обычаи"
        ]
    }
}

# %%
import pandas as pd
import numpy as np
import re
from string import punctuation
import pymorphy3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

morph = pymorphy3.MorphAnalyzer()
russian_stopwords = stopwords.words('russian')

def preprocess(text):
    text = text.lower()
    text = re.sub(f'[{punctuation}»«–…№©™•°]', '', text)
    words = re.findall(r'\b[a-zа-яё]+\b', text)
    lemmas = []
    for word in words:
        if word not in russian_stopwords and len(word) > 2:
            lemma = morph.parse(word)[0].normal_form
            lemmas.append(lemma)
    return ' '.join(lemmas)

# Создание корпуса документов
category_docs = []
for cat, data_s in categories.items():
    doc = f"{cat} {data_s['description']} {' '.join(data_s['examples'])}"
    category_docs.append(doc)

# Инициализация TF-IDF
vectorizer = TfidfVectorizer(tokenizer=preprocess)
tfidf_matrix = vectorizer.fit_transform(category_docs)

def classify_text(text):
    processed_text = preprocess(text)

    text_vector = vectorizer.transform([processed_text])
    print(text_vector)
    similarities = cosine_similarity(text_vector, tfidf_matrix)
    print(similarities)
    best_match_idx = similarities.argmax()
    best_category = list(categories.keys())[best_match_idx]
    accuracy = similarities[0][best_match_idx]


    return best_category, accuracy

# %%
input_text = "Организация группового турпохода с одноклассниками и работа в команде"
result = classify_text(input_text)
result

# %% [markdown]
# # Определение похожих запросов

# %%
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# ✅ Загружаем предобученную модель, поддерживающую русский язык
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

# 📌 Пример запросов
queries = [
    "Как приготовить борщ?",
    "Рецепт вкусного борща",
    "Где найти рецепт лазаньи?",
    "Как сварить суп?"
]

# 🔥 Получаем эмбеддинги
query_embeddings = model.encode(queries, convert_to_tensor=True)

# 🔥 Вычисляем матрицу косинусного сходства
similarity_matrix = cosine_similarity(query_embeddings.cpu().numpy())

# 📌 Выводим результаты
df = pd.DataFrame(similarity_matrix, index=queries, columns=queries)
print(df)


# %%
df.head()

# %% [markdown]
# # rubert (semi-final version; sentiment analysys/text classification)

# %%
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, Dataset
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

# %%
train=pd.read_csv(r'C:\VisualCode\T1\tr.csv', engine='python', encoding='utf-8', on_bad_lines="skip")
test=pd.read_csv(r'C:\VisualCode\T1\ts.csv', engine='python', encoding='utf-8', on_bad_lines = "skip")

# Разделение данных на признаки и метки
X_train, X_val, y_train, y_val = train_test_split(train['review'], train['sentiment'], test_size=0.2, random_state=42)

# %%
class ReviewsDataset(Dataset):
    def __init__(self, reviews, labels=None, tokenizer=None, max_len=128):
        self.reviews = reviews
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.reviews)

    def __getitem__(self, idx):
        review = self.reviews.iloc[idx]
        inputs = self.tokenizer.encode_plus(
            review,
            add_special_tokens=True,
            max_length=self.max_len,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        item = {key: val.squeeze(0) for key, val in inputs.items()}
        if self.labels is not None:
            item['labels'] = torch.tensor(self.labels.iloc[idx], dtype=torch.long)
        return item


# %%
tokenizer = BertTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
model = BertForSequenceClassification.from_pretrained(
    "DeepPavlov/rubert-base-cased",
    num_labels=3  # У нас три класса: 0, 1, 2
)

# %%
train_dataset = ReviewsDataset(X_train, y_train, tokenizer)
val_dataset = ReviewsDataset(X_val, y_val, tokenizer)
test_dataset = ReviewsDataset(test['review'], tokenizer=tokenizer)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16)
test_loader = DataLoader(test_dataset, batch_size=16)

# %%
from transformers import AdamW

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

optimizer = AdamW(model.parameters(), lr=2e-5)

# Функция обучения
def train_epoch(model, data_loader, optimizer, device):
    model.train()
    total_loss = 0
    for batch in data_loader:
        inputs = {key: val.to(device) for key, val in batch.items() if key != 'labels'}
        labels = batch['labels'].to(device)

        outputs = model(**inputs, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
    return total_loss / len(data_loader)

# %%
import time

epochs = 3  # Можно увеличить для лучшего результата

for epoch in range(epochs):
    start_time = time.time()

    train_loss = train_epoch(model, train_loader, optimizer, device)

    end_time = time.time()
    epoch_duration = end_time - start_time

    hours = int(epoch_duration // 3600)
    minutes = int((epoch_duration % 3600) // 60)
    seconds = int(epoch_duration % 60)

    torch.save(model.state_dict(), f"model_epoch_{epoch+1}.pth")
    print(f"Эпоха {epoch + 1}/{3} завершена.")
    print(f"Потеря: {train_loss:.4f}, Время выполнения: {epoch_duration:.2f} секунд.")


# %%
def predict(model, data_loader, device):
    model.eval()
    predictions = []
    with torch.no_grad():
        for batch in data_loader:
            inputs = {key: val.to(device) for key, val in batch.items()}
            outputs = model(**inputs)
            logits = outputs.logits
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            predictions.extend(preds)
    return predictions

# Предсказания
test['sentiment'] = predict(model, test_loader, device)


# %%
ans = test[['index', 'sentiment']]
ans.head(3)
ans.to_csv('poputka_0.csv', index = False)

# %% [markdown]
# # RuBert + Distilbert (for classification and sentiment analysys)

# %%
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from datasets import load_dataset
from transformers import Trainer, TrainingArguments
import torch

# Загрузка данных
train_dataset = load_dataset('csv', data_files='train.csv')['train']
test_dataset = load_dataset('csv', data_files='test.csv')['test']

# Токенизация
tokenizer = RobertaTokenizer.from_pretrained('DeepPavlov/rubert-base-cased')

def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True)

train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Загрузка модели для классификации текста
model = RobertaForSequenceClassification.from_pretrained('DeepPavlov/rubert-base-cased', num_labels=3)  # например, 3 класса

# Аргументы для тренировки
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    evaluation_strategy="epoch",
    logging_dir='./logs',
)

# Создаем Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# Обучаем модель
trainer.train()

# Получаем предсказания
predictions = trainer.predict(test_dataset)
pred_labels = torch.argmax(predictions.predictions, axis=1)
print(pred_labels)


# %%
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from transformers import Trainer, TrainingArguments
from datasets import load_dataset
import torch

# Загружаем датасет
train_dataset = load_dataset('csv', data_files='train.csv')['train']
test_dataset = load_dataset('csv', data_files='test.csv')['test']

# Токенизация
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True)

train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Загружаем модель для классификации текста
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=3)  # 3 класса для примера

# Аргументы для тренировки
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    evaluation_strategy="epoch",
    logging_dir='./logs',
)

# Создаем Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# Обучаем модель
trainer.train()

# Получаем предсказания
predictions = trainer.predict(test_dataset)
pred_labels = torch.argmax(predictions.predictions, axis=1)
print(pred_labels)
