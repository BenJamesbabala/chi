""" demo of chi.model
This is how we can use python functions to define and
scope TensorFlow models
"""
import tensorflow as tf
import chi
import numpy as np

from tensorflow.contrib import layers  # Keras-style layers
import os
from tensorflow.contrib import learn

chi.set_loglevel('debug')


@chi.model
def my_model(x: (None, 28*28)):
  x = layers.fully_connected(x, 100)
  z = layers.fully_connected(x, 10, None)
  p = layers.softmax(z)
  return z, p


@chi.function
def compute_forward(x):
  y = my_model(x)
  return y

# now that the model has been used once and
# its internal variables hav been created we can get

print('\n'.join([v.name for v in my_model.trainable_variables()]))
print(my_model.summaries())


# we can also use the model again, parameters are automatically shared
@chi.function
def train_my_model(x, labels: tf.int32):
  z, p = my_model(x)
  loss = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels, logits=z)
  return my_model.minimize(loss)


@chi.function
def test_my_model(x, labels: tf.int64):
  z, p = my_model(x)
  correct_prediction = tf.equal(tf.argmax(p, 1), labels)
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  return accuracy

# now we can use that to classify handwritten digits

datapath = os.path.join(os.path.expanduser('~'), '.chi', 'datasets', 'mnist')
dataset = learn.datasets.mnist.read_data_sets(datapath)

for i in range(10000):
  images, labels = dataset.train.next_batch(64)
  loss = train_my_model(images, labels)
  if i % 100 == 0:
    acc = test_my_model(*dataset.test.next_batch(1024))
    print(acc)
