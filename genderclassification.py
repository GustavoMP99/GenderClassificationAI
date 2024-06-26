# -*- coding: utf-8 -*-
"""GenderClassification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IQel7VIm5FMgC6ixODbYZLvYmIk7EQxj

## Análisis del Problema
Se quiere identificar caras de personas y con la información obtenida de poder decir si es hombre o mujer, esto por medio de un sistema CNN.

#CNN
### Autores
   * Daniela Alvarado
   * Gustavo Méndez

##Librerias
"""

import numpy as np
import pandas as pd
from glob import glob
import os
import PIL
import tensorflow as tf
import pathlib
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

"""## Entendimiento de los Datos"""

!wget https://www.dropbox.com/s/s5n3rb4sg6twuyq/faces.zip

!unzip "/content/faces.zip"

all_faces = glob('/content/faces/*/*')

image_count = len(list(all_faces))
print(image_count)

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
  '/content/faces',
  validation_split=0.25,
  subset="training",
  seed=123,
  image_size=(32, 32),
  batch_size=180)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
   '/content/faces',
  validation_split=0.25,
  subset="validation",
  seed=123,
  image_size=(32, 32),
  batch_size=180)

"""## Exploración de los Datos"""

import matplotlib.pyplot as plt
class_names = train_ds.class_names
plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
  for i in range(9):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(images[i].numpy().astype("uint8"))
    plt.title(class_names[labels[i]])
    plt.axis("off")

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

normalization_layer = layers.experimental.preprocessing.Rescaling(1./255)

normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_ds))
first_image = image_batch[0]
print(np.min(first_image), np.max(first_image))

num_classes = 2
data_augmentation = keras.Sequential(
  [
    layers.experimental.preprocessing.RandomFlip("horizontal",
                                                 input_shape=(32,
                                                              32,
                                                              3)),
    layers.experimental.preprocessing.RandomRotation(0.1),
    layers.experimental.preprocessing.RandomZoom(0.1),
  ]
)

plt.figure(figsize=(10, 10))
for images, _ in train_ds.take(1):
  for i in range(9):
    augmented_images = data_augmentation(images)
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(augmented_images[0].numpy().astype("uint8"))
    plt.axis("off")

"""##Modelo CNN"""

model = Sequential([
  data_augmentation,
  layers.experimental.preprocessing.Rescaling(1./255),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Dropout(0.2),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])
model.summary()

epochs = 15
history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)

"""##Evaluación"""

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.savefig('figure_1.png')
plt.show()

model.save('gender_classification')

def Average(lst):
    return sum(lst) / len(lst)

Average(val_acc)

"""#Resultados
Al final se pudo ver como el modelo pudo clasificar satisfactoriamente el genero de las personas por medio de su cara con un 86% de presición aproximadamente.
"""