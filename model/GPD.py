import pandas as pd
import tensorflow as tf
import tensorflow_probability as tfp

from helpers.outputs import Metric


class GPD:

    def __init__(self, data_path: str, metric: Metric, learning_rate: float):
        self.metric = metric
        self.data = pd.read_csv(data_path, names=['timestamp', metric])
        self.data = self.data[metric].values

        self.threshold = tf.Variable(0.0, dtype=tf.float32)
        self.scale = tf.Variable(1.0, dtype=tf.float32)
        self.concentration = tf.Variable(0.0, dtype=tf.float32)

        self.gp_dist = tfp.distributions.GeneralizedPareto(self.threshold, self.scale, self.concentration)

        self.loss_fn = lambda: self.negative_log_likelihood()
        self.optimizer = tf.optimizers.Adam(learning_rate=learning_rate)
    
    def negative_log_likelihood(self):
        return -tf.reduce_mean(self.gp_dist.log_prob(self.data))

    def train(self, epochs: int):
        for _ in range(epochs):
            self.optimizer.minimize(self.loss_fn, var_list=[self.threshold, self.scale, self.concentration])
    
    def parameters(self):
        threshold = self.threshold.numpy()
        scale = self.scale.numpy()
        concentration = self.concentration.numpy()
        return threshold, scale, concentration

    def distribution(self):
        return self.gp_dist
