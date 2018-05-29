from sklearn.datasets import fetch_mldata
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import tensorflow as tf

import numpy as np
import os
import argparse
import urllib.request

from azureml.core.run import Run

parser = argparse.ArgumentParser()

parser.add_argument('--batch-size', type = int, dest='batch_size', default = 50, help = 'mini batch size for training')
parser.add_argument('--first-layer-neurons', type = int, dest='n_hidden_1', default = 100, help = '# of neurons in the first layer')
parser.add_argument('--second-layer-neurons', type = int, dest='n_hidden_2', default = 100, help = '# of neurons in the second layer')
parser.add_argument('--learning-rate', type = float, dest='learning_rate', default = 0.01, help = 'learning rate')

args = parser.parse_args()

data_path = '/tmp'
print('data path:', data_path)

# create outputs folder
os.makedirs('./outputs', exist_ok = True)
# create tmp folder to buffer MNIST dataset
os.makedirs(os.path.join(data_path, 'mldata'), exist_ok = True)

run = Run.get_submitted_run()

print('fetching MNIST data...')
# MNIST data set hosted in Azure
url = 'https://airontime.blob.core.windows.net/data/mnist-original.mat?st=2018-05-09T09%3A36%3A00Z&se=2019-05-10T09%3A36%3A00Z&sp=r&sv=2017-04-17&sr=b&sig=FVLLa5AYOB%2BWuvdA5P0o3gAtleQ9hcFO%2Fp%2BkMcQ%2ByS0%3D'

urllib.request.urlretrieve(url, os.path.join(data_path, 'mldata', 'mnist-original.mat'))
print('MNIST dataset downloaded.')

mnist = fetch_mldata('MNIST original', data_home = data_path)
print('MNIST dataset loaded in memory.')

# use the full set with 70,000 records, normalize X pixel intensity values to 0-1
X_mnist, y_mnist = mnist['data'] / 255.0, mnist['target']

print('X: ', X_mnist.shape)
print('y: ', y_mnist.shape)
print('labels: ', np.unique(y_mnist))

X_train, X_test, y_train, y_test = train_test_split(X_mnist, y_mnist, test_size = 15000, random_state = 42)

print("training a tensorflow model...")

n_inputs = 28 * 28
n_hidden1 = args.n_hidden_1
n_hidden2 = args.n_hidden_2
n_outputs = 10

X = tf.placeholder(tf.float32, shape=(None, n_inputs), name='X')
y = tf.placeholder(tf.int64, shape=(None), name='y')

# set up DNN architecture
with tf.name_scope('dnn'):
    hidden1 = tf.layers.dense(X, n_hidden1, name='hidden1', activation=tf.nn.relu)
    hidden2 = tf.layers.dense(hidden1, n_hidden2, name='hidden2', activation=tf.nn.relu)
    logits = tf.layers.dense(hidden2, n_outputs, name='outputs')

# define loss
with tf.name_scope('loss'):
    xentropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=y, logits=logits)
    loss = tf.reduce_mean(xentropy, name='loss')

learning_rate = args.learning_rate
run.log('learning_rate', np.float64(learning_rate))

# define training operation
with tf.name_scope('train'):
    optimizer = tf.train.GradientDescentOptimizer(learning_rate = learning_rate)
    training_op = optimizer.minimize(loss)

# define evaluation operation
with tf.name_scope('eval'):
    correct = tf.nn.in_top_k(logits, y, 1)
    accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))

init = tf.global_variables_initializer()

n_epochs = 25
train_size = X_train.shape[0]
batch_size = args.batch_size
n_batches = train_size // batch_size

print(X_train.shape, y_train.shape)

print('batch_size:', batch_size)
print('n_batches:', n_batches)
print('first layer neurons:', n_hidden1)
print('second layer neurons:', n_hidden2)

run.log('batch_size', batch_size)
run.log('first_layer_neurons', n_hidden1)
run.log('second_layer_neurons', n_hidden2)

with tf.Session() as sess:
    init.run()
    for epoch in range(n_epochs):
        batch_count = 0
        # random permutation
        perm = np.arange(train_size)
        np.random.shuffle(perm)
        # shuffle X and y at the beginning of every epoch
        X_train, y_train = X_train[perm], y_train[perm]
        b_start = 0
        b_end = b_start + batch_size
        for _ in range(n_batches):
            X_batch, y_batch = X_train[b_start:b_end], y_train[b_start:b_end]
            b_start = b_start + batch_size
            b_end = min(b_start + batch_size, train_size)
            # train on mini batch
            sess.run(training_op, feed_dict={X: X_batch, y: y_batch})
        acc_train = accuracy.eval(feed_dict={X: X_train, y: y_train})
        acc_val = accuracy.eval(feed_dict={X: X_test, y: y_test})
        print(epoch, 'Train accuracy:', acc_train, ', Val accuracy;', acc_val)
        run.log('epoch_train_acc', np.float64(acc_train))
        run.log('epoch_val_acc', np.float64(acc_val))
        
    # predicted value
    y_hat = np.argmax(logits.eval(feed_dict = {X: X_test}), axis = 1)

# overall accuracy
acc = np.average(np.int32(y_hat == y_test))
run.log('accuracy', acc)
print('Overall accuracy:', acc)

# calculate confusion matrix
conf_mx = confusion_matrix(y_test, y_hat)
print('Confusion matrix:')
print(conf_mx)


