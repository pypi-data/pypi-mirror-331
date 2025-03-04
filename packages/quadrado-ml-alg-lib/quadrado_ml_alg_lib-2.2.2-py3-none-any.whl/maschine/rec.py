import random
import csv
import os
from tqdm import tqdm  # Для визуализации прогресса


def train_model(params):
    """Функция для обучения модели с заданными параметрами (заглушка)"""
    lr = params['lr']
    batch_size = params['batch_size']

    # Здесь должна быть ваша реальная логика обучения модели
    # Для примера используем случайную метрику
    loss = random.uniform(0.1, 10.0)  # Имитация функции потерь
    accuracy = random.uniform(0.5, 1.0)  # Имитация точности

    return {'loss': loss, 'accuracy': accuracy}


# Настройки эксперимента
filename = 'hpo_results.csv'
n_trials = 100
search_space = {
    'lr': (0.0001, 0.1),
    'batch_size': [16, 32, 64, 128],
    'optimizer': ['adam', 'sgd', 'rmsprop']
}

# Проверяем, нужно ли писать заголовок
write_header = not os.path.exists(filename) or os.stat(filename).st_size == 0

with open(filename, 'a', newline='') as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow(['trial', 'lr', 'batch_size', 'optimizer', 'loss', 'accuracy'])

    best_accuracy = 0.0
    best_params = {}

    for trial in tqdm(range(1, n_trials + 1)):
        # Генерация случайных параметров
        params = {
            'lr': random.uniform(*search_space['lr']),
            'batch_size': random.choice(search_space['batch_size']),
            'optimizer': random.choice(search_space['optimizer'])
        }

        # Обучение модели
        results = train_model(params)

        # Запись результатов
        row = [
            trial,
            params['lr'],
            params['batch_size'],
            params['optimizer'],
            results['loss'],
            results['accuracy']
        ]
        writer.writerow(row)

        # Обновление лучшего результата
        if results['accuracy'] > best_accuracy:
            best_accuracy = results['accuracy']
            best_params = params

print("\nBest trial results:")
print(f"Accuracy: {best_accuracy:.4f}")
print("Parameters:")
for k, v in best_params.items():
    print(f"  {k}: {v}")