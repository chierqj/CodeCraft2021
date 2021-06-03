# -*- coding: utf-8 -*-
# Author: wolfkin
# File  : regression

import numpy as np
import random
from matplotlib import pyplot as plt
from copy import deepcopy


class Regression:
    def __init__(self, lr, epochs, bias = False):
        self.lr = lr
        self.epochs = epochs
        self.bias = bias

    def score(self, X, y):
        mse = 0
        y_mean = sum(y) / len(y)
        v = 0
        for i in range(len(y)):
            pred = self.predict(X[i])
            mse += (y[i] - pred) ** 2
            v += (y[i] - y_mean) ** 2
        return 1 - mse/v

    def predict(self, x):
        pred = 0
        for i in range(len(self.W)):
            pred += self.W[i] * x[i] / 100
        if self.bias:
            pred += self.b
        return pred

    def feature_norm(self, X):
        res = deepcopy(X)
        for j in range(len(X[0])):
            for i in range(len(X)):
                res[i][j] = X[i][j]/100
        return res

    def fit(self, X, y):
        # 权重初始化
        self.W = []
        for i in range(len(X[0])):
            self.W.append(0)
        self.b = 0

        # 特征预处理
        X_norm = self.feature_norm(X)

        for epoch in range(self.epochs):
            y_pred = []
            for i in range(len(y)):
                y_pred.append(self.predict(X[i]))

            # 计算梯度
            gradient_w = []
            gradient_b = 0
            for j in range(len(X_norm[0])):
                tmp = 0
                for i in range(len(y)):
                    tmp += (y[i] - y_pred[i]) * X_norm[i][j]
                gradient_w.append(tmp/len(y))
            if self.bias:
                for i in range(len(y)):
                    gradient_b += (y[i] - y_pred[i])
                gradient_b /= len(y)

            # 更新权重
            for i in range(len(self.W)):
                self.W[i] += self.lr * gradient_w[i]
            if self.bias:
                self.b += self.lr * gradient_b

            score = self.score(X, y)
            if epoch % 100 == 0:
                print("epoch{} score: {}".format(epoch, score))
        return [w / 100 for w in self.W], self.b / 100


class Server:
    def __init__(self, name, cpu, memory, hardware_cost, energy_cost):
        self.name = name
        self.hardware_cost = hardware_cost
        self.energy_cost = energy_cost
        self.max_cpu = cpu
        self.max_memory = memory


def get_old_servers_virtuals(input_data):
    with open(input_data, 'r') as f:
        n = int(f.readline())
        for i in range(n):
            line = f.readline().strip()[1:-1].split(sep=', ')
            s = list(map(int, line[1:]))
            server = Server(line[0], s[0], s[1], s[2], s[3])
            m_servers[line[0]] = server


if __name__ == '__main__':
    # X = [[random.random() * 1039, random.random() * 2495] for i in range(100)]
    # y = [2 * x[0] - 8 * x[1] + 0.3 for x in X]

    input_data = './training-2.txt'
    m_servers = {}
    get_old_servers_virtuals(input_data)
    X, y = [], []
    for svr in m_servers.values():
        cpu = svr.max_cpu
        mem = svr.max_memory
        hc = svr.hardware_cost
        ec = svr.energy_cost
        X.append([cpu, mem])
        y.append(hc/100)

    model = Regression(0.01, 1000, bias=False)  # 梯度下降解
    W, b = model.fit(X, y)
    print(W, b)

    y_pred = []
    for i in range(len(y)):
        y_pred.append(model.predict(X[i]))

    xx = [i for i in range(len(y))]
    plt.plot(xx, y, c='r', label='y')
    plt.plot(xx, y_pred, c='b', label='y_train')
    plt.legend()
    plt.show()




