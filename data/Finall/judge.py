# -*- coding: utf-8 -*-
# Author: wolfkin
# File  : final_judge_v2
# 增加判-1放弃（除放弃外全部竞价成功）

import os
import sys
from copy import deepcopy
from matplotlib import pyplot as plt
import numpy as np


class SvrNode:
    def __init__(self, cpu, memory, read_cpu, read_memory):
        self.cpu = cpu
        self.memory = memory
        self.read_cpu = read_cpu
        self.read_memory = read_memory

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
        if self.cpu > self.read_cpu:
            print('cpu 释放后超出最大容量!')
            return False
        if self.memory > self.read_memory:
            print('memory 释放后超出最大容量!')
            return False
        return True

    def check_self(self):
        self.cpu_rate_per_day.append(1 - self.cpu / self.read_cpu)
        self.memory_rate_per_day.append(1 - self.memory / self.read_memory)


class Server:
    def __init__(self, name, cpu, memory, hardware_cost, energy_cost):
        self.name = name
        self.m_nodes = [SvrNode(cpu/2, memory/2, cpu/2, memory/2), SvrNode(cpu/2, memory/2, cpu/2, memory/2)]
        self.m_hardware_cost = hardware_cost
        self.m_energy_cost = energy_cost
        self.max_cpu = cpu
        self.max_memory = memory

        self.id = -1

        self.working = 0
        self.num_virs = 0
        self.m_virs = []

        self.cpu_rate_per_day = []
        self.memory_rate_per_day = []

    def set_id(self, _id):
        self.id = _id

    def add_2nodes(self, vir, day):
        for node in self.m_nodes:
            flag = node.deploy(vir.cpu/2, vir.memory/2)
            if not flag:
                print("部署超出容量: day: {}  vir_id: {}  svr_id: {}  "
                      "server_nodes: A[{}, {}] B[{}, {}]".format(day,
                      vir.id, self.id, self.m_nodes[0].cpu, self.m_nodes[0].memory,
                      self.m_nodes[1].cpu, self.m_nodes[1].memory))
                exit()
        self.working = 1
        self.num_virs += 1
        self.m_virs.append(vir.id)
        vir.m_svr = self
        vir.local_node = -1

    def add_1node(self, vir, node, day):
        flag = self.m_nodes[node].deploy(vir.cpu, vir.memory)
        if not flag:
            print("部署超出容量: day: {}  vir_id: {}  svr_id: {}  "
                  "server_nodes: A[{}, {}] B[{}, {}]".format(day,
                    vir.id, self.id,self.m_nodes[0].cpu,self.m_nodes[0].memory,
                    self.m_nodes[1].cpu,self.m_nodes[1].memory))
            exit()
        self.working = 1
        self.num_virs += 1
        self.m_virs.append(vir.id)
        vir.m_svr = self
        vir.local_node = node

    def release_2nodes(self, vir):
        for node in self.m_nodes:
            node.release(vir.cpu/2, vir.memory/2)
        self.num_virs -= 1
        self.m_virs.remove(vir.id)
        vir.m_svr = None
        vir.local_node = 0
        for node in self.m_nodes:
            if node.cpu < node.read_cpu or node.memory < node.read_memory:
                return
        self.working = 0

    def release_1node(self, vir, node):
        self.m_nodes[node].release(vir.cpu, vir.memory)
        self.num_virs -= 1
        self.m_virs.remove(vir.id)
        vir.m_svr = None
        vir.local_node = 0
        for node in self.m_nodes:
            if node.cpu < node.read_cpu or node.memory < node.read_memory:
                return
        self.working = 0

    def check_self(self):
        for node in self.m_nodes:
            node.check_self()

        cpu = self.m_nodes[0].cpu + self.m_nodes[1].cpu
        memory = self.m_nodes[0].memory + self.m_nodes[1].memory
        self.cpu_rate_per_day.append(1 - cpu / self.max_cpu)
        self.memory_rate_per_day.append(1 - memory / self.max_memory)


class Virtual:
    def __init__(self, name, cpu, memory, node):
        self.name = name
        self.cpu = cpu
        self.memory = memory
        self.m_node_count = node   # 几个结点部署(0:单; 1：双)

        self.m_svr = None
        self.local_node = 0  # 在服务器的哪个结点(0: A, 1: B, -1:双)
        self.id = -1

    def set_id(self, _id):
        self.id = _id


class Request:
    def __init__(self, req_type, vir_id, vir_name=None, live_time=None, user_quota=None):
        self.req_type = req_type
        self.vir_id = vir_id
        self.vir_name = vir_name
        self.live_time = live_time
        self.user_quota = user_quota

        self.suc = 0


class Judge:
    def __init__(self, input_data, answer_data, log_path='./log', view=False):
        self.input_data = input_data
        self.answer_data = answer_data
        self.log_path = log_path
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)
        self.view = view

        self.m_tol_day = -1
        self.k = -1

        self.hardware_cost = 0
        self.energy_cost = 0
        self.total_cost = 0
        self.total_mig_times = 0
        self.total_pur_nums = 0

        self.income = 0
        self.profit = 0

        self.m_servers = {}  # svr_name: svr
        self.m_virtuals = {}
        self.m_requests = []
        self.m_add_reqs = []
        self.m_add_num = []
        self.m_del_num = []

        self.svr_pool = []
        self.vir_pool = {}  # vir_id: vir
        self.mig_more_flag = False
        self.mig_more_num = -1
        self.global_svr_id = 0

        if self.view:  # 数据分析
            self.hardware_cost_per_day = []
            self.energy_cost_per_day = []
            self.all_cost_per_day = []
            self.profit_per_day = []
            self.income_per_day = []
            self.pur_num_per_day = []
            self.mig_times_per_day = []
            self.servers_working_rate_per_day = []  # 服务器总体工作率
            self.servers_cpu_rate_per_day = []  # 服务器总体cpu占用率
            self.servers_memory_rate_per_day = []  # 服务器总体内存占用率

            self.svr_num_per_day = []
            self.req_num_per_day = []
            self.add_num_pur_day = []
            self.del_num_pur_day = []

        self.read_data()
        self.run_judge()
        self.show_scores()

        if self.view:
            # plotting
            self.pic_cost_status_path = self.log_path + '/pic_cost_status/' + self.input_data.split('/')[-1][:-4]
            if not os.path.exists(self.pic_cost_status_path):
                os.makedirs(self.pic_cost_status_path)
            self.plot_cost()
            self.plot_profit()
            self.plot_working_status()
            self.plot_nums_pur_day()

    def read_data(self):
        with open(self.input_data, 'r') as f:
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

            line = f.readline().strip().split()
            self.m_tol_day, self.k = int(line[0]), int(line[1])
            for i in range(self.m_tol_day):
                r = int(f.readline())
                add_num, del_num = 0, 0
                reqs = []
                add_reqs = []
                for j in range(r):
                    line = f.readline().strip()[1:-1].split(sep=', ')
                    if len(line) == 5:
                        req = Request("add", int(line[2]), line[1], int(line[3]), int(line[4]))
                        add_num += 1
                        add_reqs.append(req)
                    else:
                        req = Request("del", int(line[1]))
                        del_num += 1
                    reqs.append(req)
                self.m_requests.append(reqs)
                self.m_add_reqs.append(add_reqs)
                self.m_add_num.append(add_num)
                self.m_del_num.append(del_num)

    def run_judge(self):
        f = open(self.answer_data, 'r')
        if self.view:
            servers_info_per_day_statistics_path = self.log_path + '/' + self.input_data.split('/')[-1][:-4] + '_servers_statistics_info.txt'
            with open(servers_info_per_day_statistics_path, 'w') as sf:
                sf.write('{}---servers statistics info per day \n'.format(self.input_data.split('/')[-1][:-4]))
                sf.write('---------------------------------------\n')
                sf.write('\n')
        for day in range(self.m_tol_day):
            # 竞价
            tmp_income = 0
            for j in range(self.m_add_num[day]):
                our_quota = int(f.readline())
                req = self.m_add_reqs[day][j]
                if our_quota == -1:  # 放弃
                    continue
                if our_quota > req.user_quota:
                    print('第{}天 请求{} 定价({}) 高于用户报价({})'.format(day, req.vir_id, our_quota, req.user_quota))
                    exit()
                req.suc = 1
                self.income += our_quota  # 默认不放弃就竞价成功
                tmp_income += our_quota
            if self.view:
                self.income_per_day.append(tmp_income)
            # 购买
            opt, kind_num = f.readline().strip()[1:-1].split(sep=', ')
            if opt == "purchase":
                tmp_hardware_cost = 0
                tmp_pur_num = 0
                for _ in range(int(kind_num)):
                    svr_name, buy_num = f.readline().strip()[1:-1].split(sep=', ')
                    self.total_pur_nums += int(buy_num)
                    if self.view:
                        tmp_pur_num += int(buy_num)
                    for _ in range(int(buy_num)):
                        self.svr_pool.append(deepcopy(self.m_servers[svr_name]))
                        self.svr_pool[-1].set_id(self.global_svr_id)
                        self.global_svr_id += 1
                        self.hardware_cost += self.svr_pool[-1].m_hardware_cost
                        if self.view:
                            tmp_hardware_cost += self.svr_pool[-1].m_hardware_cost
                if self.view:
                    self.hardware_cost_per_day.append(tmp_hardware_cost)
                    self.pur_num_per_day.append(tmp_pur_num)
            else:
                print("购买解析错误")
            # 迁移
            opt, mig_num = f.readline().strip()[1:-1].split(sep=', ')
            if opt == "migration":
                mig_num = int(mig_num)
                if mig_num > (3 * len(self.vir_pool) // 100):
                    if not self.mig_more_flag:
                        self.mig_more_num = mig_num
                        self.mig_more_flag = True
                    else:
                        print("第{}天 迁移数量{} 超出限制".format(day, mig_num))
                        exit()
                self.total_mig_times += mig_num
                if self.view:
                    self.mig_times_per_day.append(mig_num)
                for _ in range(mig_num):
                    line = f.readline().strip()[1:-1].split(sep=', ')
                    vir_id = int(line[0])
                    svr_to_id = int(line[1])
                    vir = self.vir_pool[vir_id]
                    # 迁移
                    if vir.m_node_count == 1:  # 双节点
                        svr_from_id = self.vir_pool[vir_id].m_svr.id
                        if svr_from_id == svr_to_id:
                            print("error: 迁移到同一台虚拟机")
                            exit()
                        self.svr_pool[svr_from_id].release_2nodes(vir)
                        self.svr_pool[svr_to_id].add_2nodes(vir, day)
                    else:
                        node_to = 0 if line[2] == 'A' else 1
                        svr_from_id, node_from = self.vir_pool[vir_id].m_svr.id, self.vir_pool[vir_id].local_node
                        if svr_from_id == svr_to_id and node_from == node_to:
                            print("error: 迁移到同一台虚拟机")
                            exit()
                        self.svr_pool[svr_from_id].release_1node(vir, node_from)
                        self.svr_pool[svr_to_id].add_1node(vir, node_to, day)
            else:
                print("迁移解析错误")
            # 部署
            for req in self.m_requests[day]:
                if req.req_type == "add":
                    if req.suc == 0:
                        continue
                    self.vir_pool[req.vir_id] = deepcopy(self.m_virtuals[req.vir_name])
                    vir = self.vir_pool[req.vir_id]
                    vir.set_id(req.vir_id)
                    if vir.m_node_count == 1:
                        svr_id = int(f.readline().strip()[1:-1])
                        self.svr_pool[svr_id].add_2nodes(vir, day)
                    else:
                        svr_id, local_node = f.readline().strip()[1:-1].split(sep=', ')
                        svr_id = int(svr_id)
                        local_node = 0 if local_node == 'A' else 1
                        self.svr_pool[svr_id].add_1node(vir, local_node, day)
                elif req.req_type == "del":
                    if req.vir_id not in self.vir_pool.keys():
                        continue
                    vir = self.vir_pool[req.vir_id]
                    svr, local_node = vir.m_svr, vir.local_node
                    if vir.m_node_count == 1:
                        svr.release_2nodes(vir)
                    else:
                        svr.release_1node(vir, local_node)
                    self.vir_pool.pop(req.vir_id)
                else:
                    print("决策解析错误")
            # 核算电费
            tmp_energy_cost = 0
            working_num = 0
            tmp_cpu_occupy = 0
            tmp_cpu_resource = 0
            tmp_memory_occupy = 0
            tmp_memory_resource = 0
            tmp_svr_count_vir_nums = []
            for svr in self.svr_pool:
                if svr.working == 1:
                    self.energy_cost += svr.m_energy_cost
                    if self.view:
                        tmp_energy_cost += svr.m_energy_cost
                        working_num += 1

            if self.view:
                self.energy_cost_per_day.append(tmp_energy_cost)
                self.all_cost_per_day.append(tmp_energy_cost + tmp_hardware_cost)
                self.profit_per_day.append(tmp_income - tmp_hardware_cost - tmp_energy_cost)
                self.servers_working_rate_per_day.append(working_num / len(self.svr_pool))
                for svr in self.svr_pool:
                    svr.check_self()
                    if svr.working == 1:
                        tmp_cpu_occupy += (svr.m_nodes[0].cpu + svr.m_nodes[1].cpu)
                        tmp_cpu_resource += svr.max_cpu
                        tmp_memory_occupy += (svr.m_nodes[0].memory + svr.m_nodes[1].memory)
                        tmp_memory_resource += svr.max_memory
                        tmp_svr_count_vir_nums.append(svr.num_virs)
                self.servers_cpu_rate_per_day.append(1 - tmp_cpu_occupy / tmp_cpu_resource)
                self.servers_memory_rate_per_day.append(1 - tmp_memory_occupy / tmp_memory_resource)

                self.svr_num_per_day.append(len(self.svr_pool))
                self.req_num_per_day.append(len(self.m_requests[day]))
                self.add_num_pur_day.append(self.m_add_num[day])
                self.del_num_pur_day.append(len(self.m_requests[day]) - self.m_add_num[day])

                nv_mean, nv_sum, nv_var, nv_median, nv_min, nv_max = self.get_statistics_info(tmp_svr_count_vir_nums)

                with open(servers_info_per_day_statistics_path, 'a') as sf:
                    sf.write('day[{}] 服务器总数量:   {}'.format(day, len(self.svr_pool)) + '\n')
                    sf.write('day[{}] 服务器开机数量:   {}'.format(day, working_num) + '\n')
                    sf.write('day[{}] 服务器关机数量:   {}'.format(day, len(self.svr_pool)-working_num) + '\n')
                    sf.write('day[{}] 针对所有开机服务器统计:   '.format(day) + '\n')
                    sf.write('day[{}] 平均部署虚拟机数量:   {}'.format(day, nv_mean) + '\n')
                    sf.write('day[{}] 部署虚拟机数量总数:   {}'.format(day, nv_sum) + '\n')
                    sf.write('day[{}] 部署虚拟机数量方差:   {}'.format(day, nv_var) + '\n')
                    sf.write('day[{}] 部署虚拟机数量中位数:  {}'.format(day, nv_median) + '\n')
                    sf.write('day[{}] 部署虚拟机数量最大值:  {}'.format(day, nv_max) + '\n')
                    sf.write('day[{}] 部署虚拟机数量最小值:  {}'.format(day, nv_min) + '\n')
                    sf.write('day[{}] 购买数量:  {}'.format(day, tmp_pur_num) + '\n')
                    sf.write('day[{}] 硬件成本:  {}'.format(day, tmp_hardware_cost) + '\n')
                    sf.write('day[{}] 电费:  {}'.format(day, tmp_energy_cost) + '\n')
                    sf.write('day[{}] cpu利用率:  {}'.format(day, 1 - tmp_cpu_occupy / tmp_cpu_resource) + '\n')
                    sf.write('day[{}] mem利用率:  {}'.format(day, 1 - tmp_memory_occupy / tmp_memory_resource) + '\n')

                    sf.write('day[{}] 当日成本:  {}'.format(day, tmp_energy_cost + tmp_hardware_cost) + '\n')
                    sf.write('day[{}] 当日收入:  {}'.format(day, tmp_income) + '\n')
                    sf.write('day[{}] 当日盈利:  {}'.format(day, tmp_income - tmp_hardware_cost - tmp_energy_cost) + '\n')
                    sf.write('--------------------------------------------\n')
        f.close()

    @staticmethod
    def get_statistics_info(lis):
        arr = np.array(lis)
        return np.mean(arr), np.sum(arr), np.var(arr), np.median(arr), np.min(arr), np.max(arr)

    def show_scores(self):
        self.total_cost = self.hardware_cost + self.energy_cost
        self.profit = self.income - self.total_cost

        svr_poor_kind = [svr.name for svr in self.svr_pool]
        svr_kind_num = {}
        for svr in svr_poor_kind:
            svr_kind_num[svr] = svr_kind_num.get(svr, 0) + 1

        print('total hardware_cost: ', self.hardware_cost)
        print('total energy_cost: ', self.energy_cost)
        print('total migration times: ', self.total_mig_times)
        print('total purchase kind_nums: ', len(set(svr_poor_kind)))
        print('total purchase nums: ', self.total_pur_nums)
        print('total cost: ', self.total_cost)
        print('total income: ', self.income)
        print('total profit: ', self.profit)

        with open(self.log_path+'/'+self.input_data.split('/')[1][:-4]+'_scores.txt', 'w') as f:
            f.write('total hardware_cost: ' + str(self.hardware_cost) + '\n')
            f.write('total energy_cost: ' + str(self.energy_cost) + '\n')
            f.write('total migration times: ' + str(self.total_mig_times) + '\n')
            f.write('total purchase kind_nums: ' + str(len(set(svr_poor_kind))) + '\n')
            f.write('total purchase nums: ' + str(self.total_pur_nums) + '\n')
            f.write('total cost: ' + str(self.total_cost) + '\n')
            f.write('total income: ' + str(self.income) + '\n')
            f.write('total profit: ' + str(self.profit) + '\n')
            f.write('server kind nums: \n')
            for svr, num in svr_kind_num.items():
                f.write('\t' + svr + ' :   ' + str(num) + '\n')

    def plot_cost(self):
        xx = [i+1 for i in range(self.m_tol_day)]
        plt.plot(xx, self.hardware_cost_per_day, color='red', label='hardware_cost')
        plt.plot(xx, self.energy_cost_per_day, color='green', label='energy_cost')
        plt.plot(xx, self.all_cost_per_day, color='blue', label='total_cost')
        plt.legend()
        plt.title("all server cost")
        plt.xlabel("day")
        plt.savefig(self.pic_cost_status_path + '/' + self.input_data.split('/')[-1][:-4] + "_cost.png")
        # plt.show()
        plt.clf()

    def plot_profit(self):
        xx = [i+1 for i in range(self.m_tol_day)]
        plt.plot(xx, self.profit_per_day, color='red', label='profit_per_day')
        plt.plot(xx, self.income_per_day, color='green', label='income_per_day')
        plt.plot(xx, self.all_cost_per_day, color='blue', label='all_cost_per_day')
        plt.legend()
        plt.title("profit_income_cost_per_day")
        plt.xlabel("day")
        plt.savefig(self.pic_cost_status_path + '/' + self.input_data.split('/')[-1][:-4] + "_profit.png")
        # plt.show()
        plt.clf()

    def plot_working_status(self):
        xx = [i + 1 for i in range(self.m_tol_day)]
        plt.plot(xx, self.servers_working_rate_per_day, color='red', label='total_servers_working_rate')
        plt.plot(xx, self.servers_cpu_rate_per_day, color='green', label='total_servers_cpu_rate')
        plt.plot(xx, self.servers_memory_rate_per_day, color='blue', label='total_servers_memory_rate')
        plt.legend()
        plt.title("all server working status")
        plt.xlabel("day")
        # plt.show()
        plt.savefig(self.pic_cost_status_path + '/' + self.input_data.split('/')[-1][:-4] + "_working_status.png")
        plt.clf()

    def plot_nums_pur_day(self):
        xx = [i + 1 for i in range(self.m_tol_day)]
        plt.plot(xx, self.pur_num_per_day, color='red', label='servers_pur_num')
        plt.legend()
        plt.title("servers_pur_num")
        plt.xlabel("day")
        # plt.show()
        plt.savefig(self.pic_cost_status_path + '/' + self.input_data.split('/')[-1][:-4] + "_servers_pur_num.png")
        plt.clf()

        plt.plot(xx, self.svr_num_per_day, color='green', label='servers_total_num')
        plt.legend()
        plt.title("servers_total_num")
        plt.xlabel("day")
        # plt.show()
        plt.savefig(self.pic_cost_status_path + '/' + self.input_data.split('/')[-1][:-4] + "_servers_total_num.png")
        plt.clf()

        plt.plot(xx, self.mig_times_per_day, color='blue', label='migration_nums')
        plt.legend()
        plt.title("migration_nums")
        plt.xlabel("day")
        # plt.show()
        plt.savefig(self.pic_cost_status_path + '/' + self.input_data.split('/')[-1][:-4] + "_migration_nums.png")
        plt.clf()

        plt.plot(xx, self.req_num_per_day, color='blue', label='requests_total_pur_num')
        plt.plot(xx, self.add_num_pur_day, color='red', label='requests_add_pur_num')
        plt.plot(xx, self.del_num_pur_day, color='green', label='requests_del_pur_num')
        plt.legend()
        plt.title("requests_pur_num")
        plt.xlabel("day")
        # plt.show()
        plt.savefig(self.pic_cost_status_path + '/' + self.input_data.split('/')[-1][:-4] + "_requests_pur_num.png")
        plt.clf()


if __name__ == '__main__':
    VIEW = False
    if len(sys.argv) != 1 and sys.argv[1] == 'view':
        VIEW = True

    DATA_PATH = ['./training-1.txt', './training-2.txt']
    ANSWER_PATH = ['./answer1.txt',
                   './answer2.txt']
    # DATA_PATH = ['./training-test.txt']
    # ANSWER_PATH = ['./answer-test.txt']
    all_cost = 0
    all_income = 0
    all_profit = 0
    for ii, (dp, ap) in enumerate(zip(DATA_PATH, ANSWER_PATH)):
        print("training-data", ii + 1)
        j = Judge(input_data=dp, answer_data=ap, view=VIEW)
        all_cost += j.total_cost
        all_income += j.income
        all_profit += j.profit
        print('-' * 30)
        print()
    print("training data 1+2: ")
    print("\t all_cost: ", all_cost)
    print("\t all_income: ", all_income)
    print("\t all_profit: ", all_profit)
