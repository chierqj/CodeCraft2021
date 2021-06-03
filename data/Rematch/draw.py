# -*- coding: utf-8 -*-
# Author: wolfkin
# File  : radioAnalysis

import os
from tqdm import tqdm
from matplotlib import pyplot as plt


class Virtual:
    def __init__(self, name, cpu, memory, node):
        self.name = name
        self.cpu = cpu
        self.memory = memory
        self.node = node

        self.selected = []
        self.passed = []
        self.match = []

    def set_selected(self, lis):
        self.selected.extend(lis)

    def set_passed(self, lis):
        self.passed.extend(lis)

    def set_match(self, lis):
        self.match.extend(lis)

    def show(self, path):
        x1 = [i+1 for i in range(len(self.selected))]
        x2 = [i+1+len(x1) for i in range(len(self.passed))]
        plt.plot(x1, self.selected, c='r', linestyle='--', marker='o')
        plt.plot(x2, self.passed, c='b', linestyle='-.', marker='>')

        plt.legend(['selected', 'passed'])
        for svr in self.match:
            plt.vlines(svr, max(self.selected + self.passed), min(self.selected + self.passed), color="k")
        plt.title(self.name+' cpu-'+str(self.cpu)
                  +' mem-'+str(self.memory)+' node-'+str(self.node))
        plt.vlines((len(x1)+len(x2))*0.4, max(self.selected+self.passed), min(self.selected+self.passed), color="g")  # 竖线
        plt.savefig(path + '/' + self.name + ".png")
        # plt.show()
        plt.clf()


class Analyzer:
    def __init__(self, input_path, save_path):
        self.input_path = input_path
        self.save_path = save_path
        self.m_virtuals = {}

        self.run()

    def read_data(self):
        with open(self.input_path, 'r', encoding="utf-8") as f:
            line = f.readline()
            while line:
                line = line.strip()[6:-1].split(sep=', ')
                # s = list(map(int, line[1:]))
                virtual = Virtual(line[0], int(line[2].split(':')[1]),
                                  int(line[3].split(':')[1]),
                                  int(line[4].split(':')[1]))
                self.m_virtuals[line[0]] = virtual
                line = f.readline().strip()[:-1]
                virtual.set_selected(list(map(float, line.split(','))))
                line = f.readline().strip()[:-1].split(',')
                if line[0] != "":
                    virtual.set_passed(list(map(float, line)))
                line = f.readline().strip()
                virtual.set_match(list(map(int, line.split(','))))
                line = f.readline()

    def plot_radio(self):
        for vir_name, vir in tqdm(self.m_virtuals.items()):
            vir.show(self.save_path)

    def run(self):
        self.read_data()
        self.plot_radio()
        # self.m_virtuals['vmII5P5'].show(self.save_path)
        pass


if __name__ == '__main__':
    answer_path = ["./ratio1.txt", "./ratio2.txt"]
    out_path = "./analysis"
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    for ans in answer_path:
        print("ploting... ", ans)
        if not os.path.exists(out_path + '/' + ans[-5]):
            os.mkdir(out_path + '/' + ans[-5])
        analyzer = Analyzer(ans, out_path + '/' + ans[-5])
