# -*- coding: utf-8 -*-
# Author: wolfkin
# File  : judge_v04

import os
import sys
from copy import deepcopy
from matplotlib import pyplot as plt
import numpy as np


class Node:
    def __init__(self, cpu, memory):
        self.cpu = cpu
        self.memory = memory

        self.max_cpu = cpu
        self.max_memory = memory

        self.cpu_per_day = []
        self.memory_per_day = []
        self.cpu_rate_per_day = []
        self.memory_rate_per_day = []

    def deploy(self, cpu_cost, memory_cost):
        self.cpu -= cpu_cost
        self.memory -= memory_cost
        if self.cpu < 0:
            print('cpu 部署超出容量!')
            return False
        if self.memory < 0:
            print('memory 部署超出容量!')
            return False
        return True

    def release(self, cpu_cost, memory_cost):
        self.cpu += cpu_cost
        self.memory += memory_cost
        if self.cpu > self.max_cpu:
            print('cpu 释放后超出最大容量!')
            return False
        if self.memory > self.max_memory:
            print('memory 释放后超出最大容量!')
            return False
        return True

    def check_self(self):
        self.cpu_per_day.append(self.cpu)
        self.memory_per_day.append(self.memory)
        self.cpu_rate_per_day.append(1 - self.cpu / self.max_cpu)
        self.memory_rate_per_day.append(1 - self.memory / self.max_memory)


class Server:
    def __init__(self, name, cpu, memory, hardware_cost, energy_cost):
        self.name = name
        self.nodes = [Node(cpu/2, memory/2), Node(cpu/2, memory/2)]
        self.hardware_cost = hardware_cost
        self.energy_cost = energy_cost
        self.max_cpu = cpu / 2
        self.max_memory = memory / 2
        self.working = 0

        self.true_cost = 0

        self.cpu_per_day = []
        self.memory_per_day = []
        self.cpu_rate_per_day = []
        self.memory_rate_per_day = []

        self.num_virs = 0
        self.m_virs = []

    def add_2nodes(self, vir, vir_id, day, svr_id):
        for node in self.nodes:
            flag = node.deploy(vir.cpu/2, vir.memory/2)
            if not flag:
                print("部署超出容量: day: {}  vir_id: {}  svr_id: {}  server_nodes: A[{}, {}] B[{}, {}]".format(
                    day, vir_id, svr_id, self.nodes[0].cpu, self.nodes[0].memory, self.nodes[1].cpu, self.nodes[1].memory))
                exit()
        self.working = 1
        self.num_virs += 1
        self.m_virs.append(vir_id)

    def add_1node(self, vir, node, vir_id, day, svr_id):
        if node not in ['A', 'B']:
            print("部署时解析节点错误")
        node = 0 if node == 'A' else 1
        flag = self.nodes[node].deploy(vir.cpu, vir.memory)
        if not flag:
            print("部署超出容量: day: {}  vir_id: {}  svr_id: {}  server_nodes: A[{}, {}] B[{}, {}]".format(
                day, vir_id, svr_id, self.nodes[0].cpu, self.nodes[0].memory, self.nodes[1].cpu, self.nodes[1].memory))
            exit()
        self.working = 1
        self.num_virs += 1
        self.m_virs.append(vir_id)

    def release_2nodes(self, vir, vir_id):
        for node in self.nodes:
            node.release(vir.cpu/2, vir.memory/2)
        self.num_virs -= 1
        self.m_virs.remove(vir_id)
        for node in self.nodes:
            if node.cpu < self.max_cpu or node.memory < self.max_memory:
                return
        self.working = 0

    def release_1node(self, vir, node, vir_id):
        if node not in ['A', 'B']:
            print("释放时解析节点错误")
        node = 0 if node == 'A' else 1
        self.nodes[node].release(vir.cpu, vir.memory)
        self.m_virs.remove(vir_id)
        for node in self.nodes:
            if node.cpu < self.max_cpu or node.memory < self.max_memory:
                return
        self.working = 0
        self.num_virs -= 1

    def check_self(self):
        for node in self.nodes:
            node.check_self()

        cpu = self.nodes[0].cpu+self.nodes[1].cpu
        memory = self.nodes[0].memory+self.nodes[1].memory
        self.cpu_per_day.append(cpu)
        self.memory_per_day.append(memory)
        self.cpu_rate_per_day.append(1 - cpu / (self.max_cpu * 2))
        self.memory_rate_per_day.append(1 - memory / (self.max_memory * 2))

    def show_info(self, rank='null', node='ALL', save_path='./'):
        """
        :param node: ALL: 全部  S: 只看总体 A: 只看node_A  B: 只看node_B
        :return:
        """
        xx = [i + 1 for i in range(len(self.cpu_per_day))]
        if node == "ALL":
            plt.plot(xx, self.cpu_rate_per_day, color='red',
                     label='total_cpu_rate_per_day')
            plt.plot(xx, self.memory_rate_per_day, color='blue',
                     label='total_memory_rate_per_day')
            plt.plot(xx, self.nodes[0].cpu_rate_per_day,
                     color='green', label='A_cpu_rate_per_day')
            plt.plot(xx, self.nodes[0].memory_rate_per_day,
                     color='sienna', label='A_memory_rate_per_day')
            plt.plot(xx, self.nodes[1].cpu_rate_per_day,
                     color='purple', label='B_cpu_rate_per_day')
            plt.plot(xx, self.nodes[1].memory_rate_per_day,
                     color='black', label='B_memory_rate_per_day')
            plt.legend()
            plt.title("server--cost-rank--" + str(rank) +
                      "--" + self.name + "--" + node)
            plt.xlabel("day")
            # plt.show()
            plt.savefig(save_path + '/cost-rank-' +
                        str(rank) + "_working_status.jpg")
            plt.clf()

            return

        if node == "S":
            # cpu_per_day = self.cpu_per_day
            # memory_per_day = self.memory_per_day
            cpu_rate_per_day = self.cpu_rate_per_day
            memory_rate_per_day = self.memory_rate_per_day
        elif node == "A":
            # cpu_per_day = self.nodes[0].cpu_per_day
            # memory_per_day = self.nodes[0].memory_per_day
            cpu_rate_per_day = self.nodes[0].cpu_rate_per_day
            memory_rate_per_day = self.nodes[0].memory_rate_per_day
        elif node == "B":
            # cpu_per_day = self.nodes[1].cpu_per_day
            # memory_per_day = self.nodes[1].memory_per_day
            cpu_rate_per_day = self.nodes[1].cpu_rate_per_day
            memory_rate_per_day = self.nodes[1].memory_rate_per_day
        else:
            print("选择节点错误")
        # plt.plot(xx, cpu_per_day, color='black', label='cpu_per_day')
        # plt.plot(xx, memory_per_day, color='green', label='memory_per_day')
        plt.plot(xx, cpu_rate_per_day, color='red', label='cpu_rate_per_day')
        plt.plot(xx, memory_rate_per_day, color='blue',
                 label='memory_rate_per_day')
        plt.legend()
        plt.title("server--" + self.name + "--" + node)
        plt.xlabel("day")
        # plt.show()
        plt.savefig(save_path + '/cost-rank-' +
                    str(rank) + "_working_status.jpg")
        plt.clf()


class Virtual:
    def __init__(self, name, cpu, memory, node):
        self.name = name
        self.cpu = cpu
        self.memory = memory
        self.node = node


class Request:
    def __init__(self, type_req, vir_id, vir_name=None):
        self.type_req = type_req
        self.vir_id = vir_id
        self.vir_name = vir_name


class Judge:
    def __init__(self, input_data, answer_data, log_path='./log'):
        self.hardware_cost_per_day = []
        self.energy_cost_per_day = []
        self.all_cost_per_day = []
        self.pur_num_per_day = []
        self.mig_times_per_day = []
        self.servers_working_rate_per_day = []  # 服务器总体工作率
        self.servers_cpu_rate_per_day = []  # 服务器总体cpu占用率
        self.servers_memory_rate_per_day = []  # 服务器总体内存占用率

        self.svr_num_per_day = []
        self.req_num_per_day = []
        self.add_num_pur_day = []
        self.del_num_pur_day = []

        self.hardware_cost = 0
        self.energy_cost = 0
        self.total_cost = 0
        self.total_mig_times = 0
        self.total_pur_nums = 0

        self.m_servers = {}  # svr_name: svr
        self.m_virtuals = {}
        self.m_requests = []

        self.svr_pool = []
        self.vir_pool = {}  # vir_id: vir_name
        self.vir_pos = {}  # vir_id: [svr_4_vir, node]

        self.input_data = input_data
        self.answer_data = answer_data
        self.log_path = log_path
        self.pic_cost_status_path = self.log_path + '/pic_cost_status'
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        self.read_data(self.input_data)
        self.run_judge(self.answer_data)
        self.show_scores()
        if VIEW:
            # plotting
            if not os.path.exists(self.pic_cost_status_path):
                os.mkdir(self.pic_cost_status_path)
            self.plot_cost()
            self.plot_working_status()
            self.plot_nums_pur_day()
            #
            # self.plot_svr_info(i)
            #
            self.plot_topK_cost_svr(10)  # top K

    def read_data(self, input_data):
        with open(input_data, 'r') as f:
            n = int(f.readline())
            for i in range(n):
                line = f.readline().strip()[1:-1].split(sep=', ')
                s = list(map(int, line[1:]))
                server = Server(line[0], s[0], s[1], s[2], s[3])
                self.m_servers[line[0]] = server

            m = int(f.readline())
            for i in range(m):
                line = f.readline().strip()[1:-1].split(sep=', ')
                s = list(map(int, line[1:]))
                virtual = Virtual(line[0], s[0], s[1], s[2])
                self.m_virtuals[line[0]] = virtual

            t = int(f.readline())
            for i in range(t):
                r = int(f.readline())
                reqs = []
                for j in range(r):
                    line = f.readline().strip()[1:-1].split(sep=', ')
                    if len(line) == 3:
                        req = Request("ADD", int(line[2]), line[1])
                    else:
                        req = Request("DEL", int(line[1]))
                    reqs.append(req)
                self.m_requests.append(reqs)

    def run_judge(self, answer_data):
        t = len(self.m_requests)
        f = open(answer_data, 'r')
        if VIEW:
            servers_info_per_day_statistics_path = self.log_path + '/' + \
                self.input_data.split('/')[1][:-4] + \
                '_servers_statistics_info.txt'
            with open(servers_info_per_day_statistics_path, 'w') as sf:
                sf.write(
                    '{}---servers statistics info per day \n'.format(self.input_data.split('/')[1][:-4]))
                sf.write('---------------------------------------\n')
                sf.write('\n')

        vir_watch = []
        for i in range(t):  # per_day
            # deal purchase:
            tmp_hardware_cost = 0
            opt, pur_num = f.readline().strip()[1:-1].split(sep=', ')
            if opt == "purchase":
                tmp_pur_num = 0
                for j in range(int(pur_num)):
                    svr_name, buy_num = f.readline().strip()[
                        1:-1].split(sep=', ')
                    tmp_pur_num += int(buy_num)
                    for _ in range(int(buy_num)):
                        self.svr_pool.append(
                            deepcopy(self.m_servers[svr_name]))
                        tmp_hardware_cost += self.svr_pool[-1].hardware_cost
                        self.svr_pool[-1].true_cost += self.svr_pool[-1].hardware_cost
                self.hardware_cost_per_day.append(tmp_hardware_cost)
                self.pur_num_per_day.append(tmp_pur_num)
            else:
                print("购买解析错误")
            # deal migration
            opt, mig_num = f.readline().strip()[1:-1].split(sep=', ')
            self.mig_times_per_day.append(int(mig_num))
            if int(mig_num) > (5 * len(self.vir_pool) // 1000):
                print("迁移数量超出限制")
            if opt == "migration":
                for j in range(int(mig_num)):
                    line = f.readline().strip()[1:-1].split(sep=', ')
                    vir_id = int(line[0])
                    svr_4_vir_new = int(line[1])
                    vir = self.m_virtuals[self.vir_pool[vir_id]]
                    # 迁移
                    if vir.node == 1:
                        svr_4_vir_old = self.vir_pos[vir_id][0]
                        if svr_4_vir_new == svr_4_vir_old:
                            print("error: 迁移到同一台虚拟机")
                        self.svr_pool[svr_4_vir_old].release_2nodes(
                            vir, vir_id)
                        self.svr_pool[svr_4_vir_new].add_2nodes(
                            vir, vir_id, i, svr_4_vir_new)
                        self.vir_pos[vir_id] = [svr_4_vir_new, "S"]
                    else:
                        node_new = line[2]
                        svr_4_vir_old, node_old = self.vir_pos[vir_id]
                        if svr_4_vir_new == svr_4_vir_old and node_old == node_new:
                            print("error: 迁移到同一台虚拟机")
                        self.svr_pool[svr_4_vir_old].release_1node(
                            vir, node_old, vir_id)
                        self.svr_pool[svr_4_vir_new].add_1node(
                            vir, node_new, vir_id, i, svr_4_vir_new)
                        self.vir_pos[vir_id] = [svr_4_vir_new, node_new]
            else:
                print("迁移解析错误")

            # deal request
            tmp_add_num = 0
            tmp_del_num = 0
            for req in self.m_requests[i]:
                if req.type_req == "ADD":
                    tmp_add_num += 1
                    vir = self.m_virtuals[req.vir_name]
                    self.vir_pool[req.vir_id] = vir.name
                    if vir.node == 1:
                        svr_id = f.readline().strip()[1:-1]
                        svr_4_vir = int(svr_id)
                        self.svr_pool[svr_4_vir].add_2nodes(
                            vir, req.vir_id, i, svr_4_vir)
                        self.vir_pos[req.vir_id] = [svr_4_vir, "S"]
                    else:
                        svr_id, node = f.readline().strip()[
                            1:-1].split(sep=', ')
                        svr_4_vir = int(svr_id)
                        self.svr_pool[svr_4_vir].add_1node(
                            vir, node, req.vir_id, i, svr_4_vir)
                        self.vir_pos[req.vir_id] = [svr_4_vir, node]
                elif req.type_req == "DEL":
                    tmp_del_num += 1
                    svr_4_vir, node = self.vir_pos[req.vir_id]
                    vir = self.m_virtuals[self.vir_pool[req.vir_id]]
                    if vir.node == 1:
                        self.svr_pool[svr_4_vir].release_2nodes(
                            vir, req.vir_id)
                    else:
                        self.svr_pool[svr_4_vir].release_1node(
                            vir, node, req.vir_id)
                    self.vir_pool.pop(req.vir_id)
                    self.vir_pos.pop(req.vir_id)
                else:
                    print("决策解析错误")
            # cost energy cost per day
            tmp_energy_cost = 0
            tmp_cpu_occupy = 0
            tmp_cpu_resource = 0
            tmp_memory_occupy = 0
            tmp_memory_resource = 0
            working_num = 0
            tmp_svr_count_vir_nums = []
            for _, svr in enumerate(self.svr_pool):
                if svr.working == 1:
                    tmp_energy_cost += svr.energy_cost
                    working_num += 1
                    svr.true_cost += tmp_energy_cost
                    tmp_svr_count_vir_nums.append(svr.num_virs)

                if VIEW:
                    svr.check_self()
                    if svr.working == 1:
                        tmp_cpu_occupy += svr.cpu_per_day[-1]
                        tmp_cpu_resource += svr.max_cpu * 2
                        tmp_memory_occupy += svr.memory_per_day[-1]
                        tmp_memory_resource += svr.max_memory * 2
            self.energy_cost_per_day.append(tmp_energy_cost)
            self.all_cost_per_day.append(tmp_energy_cost + tmp_hardware_cost)
            if VIEW:
                self.servers_working_rate_per_day.append(
                    working_num/len(self.svr_pool))
                self.servers_cpu_rate_per_day.append(
                    1 - tmp_cpu_occupy / tmp_cpu_resource)
                self.servers_memory_rate_per_day.append(
                    1 - tmp_memory_occupy / tmp_memory_resource)

                self.svr_num_per_day.append(len(self.svr_pool))
                self.req_num_per_day.append(len(self.m_requests[i]))
                self.add_num_pur_day.append(tmp_add_num)
                self.del_num_pur_day.append(tmp_del_num)

                nv_mean, nv_sum, nv_var, nv_median, nv_min, nv_max = self.get_statistics_info(
                    tmp_svr_count_vir_nums)

                with open(servers_info_per_day_statistics_path, 'a') as sf:
                    sf.write('day[{}] 服务器总数量:   {}'.format(
                        i, len(self.svr_pool)) + '\n')
                    sf.write('day[{}] 服务器开机数量:   {}'.format(
                        i, working_num) + '\n')
                    sf.write('day[{}] 服务器关机数量:   {}'.format(
                        i, len(self.svr_pool)-working_num) + '\n')
                    sf.write('day[{}] 针对所有开机服务器统计:   '.format(i) + '\n')
                    sf.write('day[{}] 平均部署虚拟机数量:   {}'.format(
                        i, nv_mean) + '\n')
                    sf.write('day[{}] 部署虚拟机数量总数:   {}'.format(
                        i, nv_sum) + '\n')
                    sf.write('day[{}] 部署虚拟机数量方差:   {}'.format(
                        i, nv_var) + '\n')
                    sf.write('day[{}] 部署虚拟机数量中位数:  {}'.format(
                        i, nv_median) + '\n')
                    sf.write('day[{}] 部署虚拟机数量最大值:  {}'.format(
                        i, nv_max) + '\n')
                    sf.write('day[{}] 部署虚拟机数量最小值:  {}'.format(
                        i, nv_min) + '\n')
                    sf.write('--------------------------------------------\n')

        f.close()

    @staticmethod
    def get_statistics_info(lis):
        arr = np.array(lis)
        return np.mean(arr), np.sum(arr), np.var(arr), np.median(arr), np.min(arr), np.max(arr)

    def show_scores(self):
        self.hardware_cost = sum(self.hardware_cost_per_day)
        self.energy_cost = sum(self.energy_cost_per_day)
        self.total_cost = sum(self.all_cost_per_day)
        self.total_pur_nums = sum(self.pur_num_per_day)
        self.total_mig_times = sum(self.mig_times_per_day)

        svr_poor_kind = [svr.name for svr in self.svr_pool]
        svr_kind_num = {}
        for svr in svr_poor_kind:
            svr_kind_num[svr] = svr_kind_num.get(svr, 0) + 1

        print('total hardware_cost: ', self.hardware_cost)
        print('total energy_cost: ', self.energy_cost)
        print('total cost: ', self.total_cost)
        print('total migration times: ', self.total_mig_times)
        print('total purchase kind_nums: ', len(set(svr_poor_kind)))
        print('total purchase nums: ', self.total_pur_nums)

        with open(self.log_path+'/'+self.input_data.split('/')[1][:-4]+'_scores.txt', 'w') as f:
            f.write('total hardware_cost: ' + str(self.hardware_cost) + '\n')
            f.write('total energy_cost: ' + str(self.energy_cost) + '\n')
            f.write('total cost: ' + str(self.total_cost) + '\n')
            f.write('total migration times: ' +
                    str(self.total_mig_times) + '\n')
            f.write('total purchase kind_nums: ' +
                    str(len(set(svr_poor_kind))) + '\n')
            f.write('total purchase nums: ' + str(self.total_pur_nums) + '\n')
            f.write('server kind nums: \n')
            for svr, num in svr_kind_num.items():
                f.write('\t' + svr + ' :   ' + str(num) + '\n')

    def plot_cost(self):
        xx = [i+1 for i in range(len(self.m_requests))]
        plt.plot(xx, self.hardware_cost_per_day,
                 color='red', label='hardware_cost')
        plt.plot(xx, self.energy_cost_per_day,
                 color='green', label='energy_cost')
        plt.plot(xx, self.all_cost_per_day, color='blue', label='total_cost')
        plt.legend()
        plt.title("all server cost")
        plt.xlabel("day")
        plt.savefig(self.pic_cost_status_path + '/' +
                    self.input_data.split('/')[1][:-4] + "_cost.jpg")
        # plt.show()
        plt.clf()

    def plot_working_status(self):
        xx = [i + 1 for i in range(len(self.m_requests))]
        plt.plot(xx, self.servers_working_rate_per_day,
                 color='red', label='total_servers_working_rate')
        plt.plot(xx, self.servers_cpu_rate_per_day,
                 color='green', label='total_servers_cpu_rate')
        plt.plot(xx, self.servers_memory_rate_per_day,
                 color='blue', label='total_servers_memory_rate')
        plt.legend()
        plt.title("all server working status")
        plt.xlabel("day")
        # plt.show()
        plt.savefig(self.pic_cost_status_path + '/' +
                    self.input_data.split('/')[1][:-4] + "_working_status.jpg")
        plt.clf()

    def plot_nums_pur_day(self):
        xx = [i + 1 for i in range(len(self.m_requests))]
        plt.plot(xx, self.pur_num_per_day,
                 color='red', label='servers_pur_num')
        plt.legend()
        plt.title("servers_pur_num")
        plt.xlabel("day")
        # plt.show()
        plt.savefig(self.pic_cost_status_path + '/' +
                    self.input_data.split('/')[1][:-4] + "_servers_pur_num.jpg")
        plt.clf()

        plt.plot(xx, self.svr_num_per_day, color='green',
                 label='servers_total_num')
        plt.legend()
        plt.title("servers_total_num")
        plt.xlabel("day")
        # plt.show()
        plt.savefig(self.pic_cost_status_path + '/' +
                    self.input_data.split('/')[1][:-4] + "_servers_total_num.jpg")
        plt.clf()

        plt.plot(xx, self.req_num_per_day, color='blue',
                 label='requests_total_pur_num')
        plt.plot(xx, self.add_num_pur_day, color='red',
                 label='requests_add_pur_num')
        plt.plot(xx, self.del_num_pur_day, color='green',
                 label='requests_del_pur_num')
        plt.legend()
        plt.title("requests_pur_num")
        plt.xlabel("day")
        # plt.show()
        plt.savefig(self.pic_cost_status_path + '/' +
                    self.input_data.split('/')[1][:-4] + "_requests_pur_num.jpg")
        plt.clf()

    def plot_svr_info(self, i, node="ALL"):
        self.svr_pool[i].show_info(node=node)

    def plot_topK_cost_svr(self, K, node="ALL"):
        save_path = self.pic_cost_status_path + '/' + \
            self.input_data.split('/')[1][:-4] + '_topK_servers'
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        sorted_svr_pool = sorted(
            self.svr_pool, key=lambda x: x.true_cost, reverse=True)
        for i, svr in enumerate(sorted_svr_pool[:K]):
            svr.show_info(rank=i+1, node=node, save_path=save_path)


if __name__ == '__main__':
    VIEW = False
    if len(sys.argv) != 1 and sys.argv[1] == 'view':
        VIEW = True

    DATA_PATH = ['./training-1.txt', './training-2.txt']
    ANSWER_PATH = ['./answer1.txt', './answer2.txt']

    # DATA_PATH = ['./training-2.txt']
    # ANSWER_PATH = ['./answer2.txt']

    all_cost = 0
    for i, (dp, ap) in enumerate(zip(DATA_PATH, ANSWER_PATH)):
        print("training-data", i+1)
        j = Judge(input_data=dp, answer_data=ap)
        all_cost += j.total_cost
        print('-' * 30)
        print()
    print("training data 1+2: ", all_cost)
    pass
