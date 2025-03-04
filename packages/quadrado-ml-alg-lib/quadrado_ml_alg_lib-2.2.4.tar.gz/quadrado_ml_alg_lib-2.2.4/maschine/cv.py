# Preprocessing
import os
from PIL import Image

def convert_to_yolo_format(image_dir, label_dir, output_label_dir):
    # Создаем директорию для выходных аннотаций
    os.makedirs(output_label_dir, exist_ok=True)

    for image_name in os.listdir(image_dir):
        if not image_name.endswith(('.jpg', '.png')):
            continue

        # Пути к файлам
        image_path = os.path.join(image_dir, image_name)
        label_path = os.path.join(label_dir, os.path.splitext(image_name)[0] + '.txt')
        output_path = os.path.join(output_label_dir, os.path.splitext(image_name)[0] + '.txt')

        # Получаем размеры изображения
        with Image.open(image_path) as img:
            img_w, img_h = img.size

        # Читаем исходные аннотации (формат: class_id x_min y_min x_max y_max)
        with open(label_path, 'r') as f:
            lines = f.readlines()

        # Конвертация
        yolo_lines = []
        for line in lines:
            parts = line.strip().split()
            class_id = parts[0]
            x_min = float(parts[1])
            y_min = float(parts[2])
            x_max = float(parts[3])
            y_max = float(parts[4])

            # Вычисляем нормализованные координаты
            x_center = (x_min + x_max) / 2 / img_w
            y_center = (y_min + y_max) / 2 / img_h
            width = (x_max - x_min) / img_w
            height = (y_max - y_min) / img_h

            yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        # Сохраняем результат
        with open(output_path, 'w') as f:
            f.writelines(yolo_lines)

# Пример использования:
convert_to_yolo_format(
    image_dir="dataset/train/images",
    label_dir="dataset/train/old_labels",  # исходные аннотации (абсолютные координаты)
    output_label_dir="dataset/train/labels"  # выходные аннотации (YOLO-формат)
)


# ЙОЛО

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

