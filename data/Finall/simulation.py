#!/usr/bin/python3

# This program is used to simulate the competition between two players
# in Huawei CodeCraft 2021.
#
# Run this as:
# python simulation.py <path_of_test_data> -- <cmd_line_player_0> --
# <cmd_line_player_1>
#
# For example:
# python simulation.py training-1.txt -- ./binary_0 -- ./binary_1
#
# This is a simple tool which is only used to help contestants debug locally.
# It does not provide the timing function either try to catch any exceptions
# or errors. In particular, it is not identical to the implementation on our
# server, which is more complex.
#
# Feel free to use or distribute this program. If you find any issue of this
# program, you can give feedback in the forum or fix it by yourself. :)
#
# @author Weibo Lin
# @date 2021-04-12

import subprocess
import sys
import os
from matplotlib import pyplot as plt
from tqdm import tqdm

VIEW = True

HOST_NUM_LIMIT = 100000

HOST_DOES_NOT_EXIST = "Host with id {} does not exist.".format
HOST_NAME_DOES_NOT_EXIST = "Host with name {} does not exist.".format
VM_DOES_NOT_EXIST = "Vm with id {} does not exist.".format
RESOURCE_LIMIT_EXCEEDED = "Resource limit in host {} is exceeded.".format
HOST_NUMBER_EXCEEDED = "The number of hosts should not exceed %d." % HOST_NUM_LIMIT
MIGRATION_LIMIT_EXCEEDED = "Migration number limit is exceeded."
INVALID_PRICE = "Price for vm with id {} is invalid".format
INVALID_LINE = "Couldn't read a valid line."
INCORRECT_DEPLOYMENT = "The nodes used to deploy vm with id {} is " \
                       "incorrect.".format


class SimulationError(Exception):
    def __init__(self, player_id, message):
        self.player_id = player_id
        self.message = message


class HostInfo:
    def __init__(self, cpu, mem, hardware_cost, energy_cost):
        self.cpu = cpu
        self.mem = mem
        self.hardware_cost = hardware_cost
        self.energy_cost = energy_cost


class VmInfo:
    def __init__(self, cpu, mem, is_two_node):
        self.cpu = cpu
        self.mem = mem
        self.is_two_node = is_two_node


class Node:
    def __init__(self, last_cpu, last_mem):
        self.last_cpu = last_cpu
        self.last_mem = last_mem

    def update(self, cpu, mem, delta):
        self.last_cpu += cpu * delta
        self.last_mem += mem * delta
        return self.last_cpu >= 0 and self.last_mem >= 0


class Host:
    def __init__(self, host_info):
        self.vm_count = 0
        self.nodes = [
            Node(host_info.cpu // 2, host_info.mem // 2) for _ in range(2)
        ]
        self.host_info = host_info

    def update(self, cpu, mem, delta, nodes):
        self.vm_count -= delta
        if len(nodes) == 2:
            cpu = cpu // 2
            mem = mem // 2
        for node_index in nodes:
            if not self.nodes[node_index].update(cpu, mem, delta):
                return False
        return True


class VmPosition:
    def __init__(self, host_id, nodes, vm_info):
        self.host_id = host_id
        self.nodes = nodes
        self.vm_info = vm_info


class DataCenter:
    def __init__(self, player_id):
        self.player_id = player_id
        self.hosts = []
        self.vm_positions = {}
        self.large_migrations = False
        self.vm_count = 0
        self.profit = 0

        self.cost = 0
        self.income = 0

        self.tmp_cost = 0
        self.all_cost_per_day = []
        self.tmp_profit = 0
        self.profit_per_day = []
        self.tmp_income = 0
        self.income_per_day = []

        self.pur_num_per_day = []
        self.mig_times_per_day = []
        self.servers_working_rate_per_day = []  # 服务器总体工作率
        self.servers_cpu_rate_per_day = []  # 服务器总体cpu占用率
        self.servers_memory_rate_per_day = []  # 服务器总体内存占用率

    def add_host(self, host_info):
        self.profit -= host_info.hardware_cost
        self.cost += host_info.hardware_cost
        self.tmp_cost += host_info.hardware_cost
        self.tmp_profit -= host_info.hardware_cost
        self.hosts.append(Host(host_info))
        if len(self.hosts) > HOST_NUM_LIMIT:
            raise SimulationError(self.player_id, HOST_NUMBER_EXCEEDED)

    def add_vm(self, vm_id, vm_info, host_id, nodes):
        self.vm_count += 1
        if host_id >= len(self.hosts):
            raise SimulationError(self.player_id, HOST_DOES_NOT_EXIST(host_id))
        if not self.hosts[host_id].update(vm_info.cpu, vm_info.mem, -1, nodes):
            raise SimulationError(self.player_id,
                                  RESOURCE_LIMIT_EXCEEDED(host_id))
        self.vm_positions[vm_id] = VmPosition(host_id, nodes, vm_info)

    def del_vm(self, vm_id):
        vm_position = self.vm_positions.get(vm_id)
        if vm_position is not None:
            self.vm_count -= 1
            cpu = vm_position.vm_info.cpu
            mem = vm_position.vm_info.mem
            self.hosts[vm_position.host_id].update(cpu, mem, 1,
                                                   vm_position.nodes)
            self.vm_positions.pop(vm_id)

    def pay_energy_cost(self):
        for host in self.hosts:
            if host.vm_count > 0:
                self.profit -= host.host_info.energy_cost
                self.cost += host.host_info.energy_cost
                self.tmp_cost += host.host_info.energy_cost
                self.tmp_profit -= host.host_info.energy_cost

    def reset_tmp(self):
        self.tmp_cost = 0
        self.tmp_profit = 0
        self.tmp_income = 0
        self.working_num = 0

    def update_per_day(self):
        self.all_cost_per_day.append(self.tmp_cost)
        self.income_per_day.append(self.tmp_income)
        self.profit_per_day.append(self.tmp_profit)

    def check_self(self):
        tmp_cpu_occupy = 0
        tmp_cpu_resource = 0
        tmp_memory_occupy = 0
        tmp_memory_resource = 0
        if len(self.hosts) == 0:
            self.servers_working_rate_per_day.append(0)
            self.servers_cpu_rate_per_day.append(0)
            self.servers_memory_rate_per_day.append(0)
            return
        for host in self.hosts:
            if host.vm_count == 0:
                continue
            self.working_num += 1
            tmp_cpu_occupy += (host.nodes[0].last_cpu + host.nodes[1].last_cpu)
            tmp_memory_occupy += (host.nodes[0].last_mem +
                                  host.nodes[1].last_mem)
            tmp_cpu_resource += host.host_info.cpu
            tmp_memory_resource += host.host_info.mem
        tmp_working_rate = 0 if len(
            self.hosts) == 0 else self.working_num / len(self.hosts)
        self.servers_working_rate_per_day.append(tmp_working_rate)
        tmp_cpu_rate = 0 if tmp_cpu_resource == 0 else (
            1 - tmp_cpu_occupy / tmp_cpu_resource)
        self.servers_cpu_rate_per_day.append(tmp_cpu_rate)
        tmp_memory_rate = 0 if tmp_memory_resource == 0 else (
            1 - tmp_memory_occupy / tmp_memory_resource)
        self.servers_memory_rate_per_day.append(tmp_memory_rate)


def write_lines(lines, player):
    for line in lines:
        player.stdin.write(line.encode())


def write_day_requests(day_requests, player):
    player.stdin.write((str(len(day_requests)) + '\n').encode())
    write_lines(day_requests, player)


host_infos = {}
vm_infos = {}
center_0 = DataCenter(0)
center_1 = DataCenter(1)


def process_host_vm_info(input_lines, player_0, player_1):
    num_hosts = int(input_lines[0])
    for i in range(num_hosts):
        values = input_lines[i + 1].strip()[1:-1].split(',')
        host_infos[values[0]] = HostInfo(int(values[1]), int(values[2]),
                                         int(values[3]), int(values[4]))
    num_vms = int(input_lines[num_hosts + 1])
    for i in range(num_vms):
        values = input_lines[num_hosts + 2 + i].strip()[1:-1].split(',')
        vm_infos[values[0]] = VmInfo(int(values[1]), int(values[2]),
                                     int(values[3]))
    write_lines(input_lines[:num_hosts + num_vms + 2], player_0)
    write_lines(input_lines[:num_hosts + num_vms + 2], player_1)
    return input_lines[num_hosts + num_vms + 2:]


def get_requests(input_lines):
    values = input_lines[0].strip().split()
    num_days = int(values[0])
    requests = []
    index = 1
    for i in range(num_days):
        requests.append([])
        num_requests = int(input_lines[index])
        index += 1
        for j in range(num_requests):
            requests[-1].append(input_lines[index])
            index += 1
    return requests


def read_player_prices(player_id, player, day_requests):
    prices = []
    for request in day_requests:
        values = request.strip()[1:-1].split(',')
        if values[0] == 'add':
            vm_id = int(values[2])
            customer_price = int(values[4])
            price = int(player.stdout.readline().decode().strip())
            prices.append(price)
            if price > customer_price or price < -1:
                raise SimulationError(player_id, INVALID_PRICE(vm_id))
    return prices


def compare_price(player, my_price, opp_price):
    if my_price != -1 and (my_price <= opp_price or opp_price == -1):
        player.stdin.write(('(1, ' + str(opp_price) + ')\n').encode())
        return True
    else:
        player.stdin.write(('(0, ' + str(opp_price) + ')\n').encode())
        return False


def compare_prices(player, center, my_prices, opp_prices):
    access = []
    for index in range(len(my_prices)):
        access.append(
            compare_price(player, my_prices[index], opp_prices[index]))
        if access[-1]:
            center.profit += my_prices[index]
            center.income += my_prices[index]
            center.tmp_income += my_prices[index]
            center.tmp_profit += my_prices[index]
    return access


def process_purchase(player_id, player, center):
    line = player.stdout.readline().decode().strip()
    if not line.startswith('(purchase,') or not line.endswith(')'):
        raise SimulationError(player_id, INVALID_LINE)
    values = line[1:-1].split(',')
    if len(values) != 2:
        raise SimulationError(player_id, INVALID_LINE)
    num_purchases = int(values[1])
    tmp_pur_num = 0
    for i in range(num_purchases):
        line = player.stdout.readline().decode().strip()
        if not line.startswith('(') or not line.endswith(')'):
            raise SimulationError(player_id, INVALID_LINE)
        values = line[1:-1].split(',')
        if len(values) != 2:
            raise SimulationError(player_id, INVALID_LINE)
        if values[0] not in host_infos:
            raise SimulationError(player_id,
                                  HOST_NAME_DOES_NOT_EXIST(values[0]))
        tmp_pur_num += int(values[1])
        for j in range(int(values[1])):
            center.add_host(host_infos[values[0]])
    if VIEW:
        center.pur_num_per_day.append(tmp_pur_num)


def process_migration(player_id, player, center):
    line = player.stdout.readline().decode().strip()
    if not line.startswith('(migration,') or not line.endswith(')'):
        raise SimulationError(player_id, INVALID_LINE)
    values = line[1:-1].split(',')
    if len(values) != 2:
        raise SimulationError(player_id, INVALID_LINE)
    num_migrations = int(values[1])
    if num_migrations > center.vm_count:
        raise SimulationError(player_id, MIGRATION_LIMIT_EXCEEDED)
    if num_migrations > center.vm_count * 3 // 100:
        if center.large_migrations:
            raise SimulationError(player_id, MIGRATION_LIMIT_EXCEEDED)
        center.large_migrations = True
    if VIEW:
        center.mig_times_per_day.append(num_migrations)
    for i in range(num_migrations):
        line = player.stdout.readline().decode().strip()
        if not line.startswith('(') or not line.endswith(')'):
            raise SimulationError(player_id, INVALID_LINE)
        values = line[1:-1].split(',')
        vm_id, host_id = int(values[0]), int(values[1])
        vm_position = center.vm_positions.get(vm_id)
        if vm_position is None:
            raise SimulationError(player_id, VM_DOES_NOT_EXIST(vm_id))
        vm_info = vm_position.vm_info
        nodes = []
        if vm_info.is_two_node == 1:
            if len(values) != 2:
                raise SimulationError(player_id, INCORRECT_DEPLOYMENT(vm_id))
            nodes.extend([0, 1])
        else:
            if len(values) != 3:
                raise SimulationError(player_id, INCORRECT_DEPLOYMENT(vm_id))
            values[2] = values[2].replace(' ', '')
            if values[2] != 'A' and values[2] != 'B':
                raise SimulationError(player_id, INCORRECT_DEPLOYMENT(vm_id))
            nodes.append(0 if values[2] == 'A' else 1)
        center.del_vm(vm_id)
        center.add_vm(vm_id, vm_info, host_id, nodes)


def pre_process_player_outputs(player_id, player, center, num_access):
    process_purchase(player_id, player, center)
    process_migration(player_id, player, center)
    answer = []
    for i in range(num_access):
        answer.append(player.stdout.readline().decode().strip())
    return answer


def deploy_vm(player_id, center, answer, vm_info, vm_id):
    if not answer.startswith('(') or not answer.endswith(')'):
        raise SimulationError(player_id, INVALID_LINE)
    values = answer[1:-1].split(',')
    if len(values) != (1 if vm_info.is_two_node else 2):
        raise SimulationError(player_id, INCORRECT_DEPLOYMENT(vm_id))
    host_id = int(values[0])
    nodes = []
    if vm_info.is_two_node:
        nodes.extend([0, 1])
    else:
        values[1] = values[1].replace(' ', '')
        if values[1] != 'A' and values[1] != 'B':
            raise SimulationError(player_id, INCORRECT_DEPLOYMENT(vm_id))
        nodes.append(0 if values[1] == 'A' else 1)
    center.add_vm(vm_id, vm_info, host_id, nodes)


def process_day_requests(access_0, access_1, answer_0, answer_1, day_requests):
    index = 0
    answer_index_0, answer_index_1 = 0, 0
    for request in day_requests:
        values = request.strip()[1:-1].split(',')
        if values[0] == 'add':
            vm_name = values[1].replace(' ', '')
            vm_id = int(values[2])
            vm_info = vm_infos[vm_name]
            if access_0[index]:
                deploy_vm(0, center_0, answer_0[answer_index_0], vm_info,
                          vm_id)
                answer_index_0 += 1
            if access_1[index]:
                deploy_vm(1, center_1, answer_1[answer_index_1], vm_info,
                          vm_id)
                answer_index_1 += 1
            index += 1
        else:
            vm_id = int(values[1])
            center_0.del_vm(vm_id)
            center_1.del_vm(vm_id)


def simulate_on_day(player_0, player_1, day_requests, day):
    if VIEW:
        center_0.reset_tmp()
        center_1.reset_tmp()
    prices_0 = read_player_prices(0, player_0, day_requests)
    prices_1 = read_player_prices(1, player_1, day_requests)

    expect_0 = [0 if x == -1 else 1 for x in prices_0]
    expect_1 = [0 if x == -1 else 1 for x in prices_1]

    access_0 = compare_prices(player_0, center_0, prices_0, prices_1)
    access_1 = compare_prices(player_1, center_1, prices_1, prices_0)
    player_0.stdin.flush()
    player_1.stdin.flush()
    answer_0 = pre_process_player_outputs(0, player_0, center_0, sum(access_0))
    answer_1 = pre_process_player_outputs(1, player_1, center_1, sum(access_1))
    process_day_requests(access_0, access_1, answer_0, answer_1, day_requests)
    center_0.pay_energy_cost()
    center_1.pay_energy_cost()
    if VIEW:
        center_0.update_per_day()
        center_1.update_per_day()

        center_0.check_self()
        center_1.check_self()

        name0 = sys.argv[3].split('/')[-1]
        name1 = sys.argv[5].split('/')[-1]
        with open(battle_info_per_day_path, 'a', encoding="utf-8") as sf:
            sf.write('day[{}] 服务器开机/总数量:  {}:{}/{} | {}:{}/{}'.format(
                day, name0, center_0.working_num, len(center_0.hosts), name1,
                center_1.working_num, len(center_1.hosts)) + '\n')
            sf.write('day[{}] 当日抢到/期望/总请求数:  {}:{}/{}/{} | {}:{}/{}/{}'.format(
                day, name0, sum(access_0), sum(expect_0), len(expect_0), name1,
                sum(access_1), sum(expect_1), len(expect_1)) + '\n')
            # sf.write('day[{}] 当日抢到请求数:  {}:{} | {}:{}'.format(day, name0, sum(access_0), name1,
            #                                                   sum(access_1)) + '\n')
            sf.write('day[{}] 当日成本:  {}:{} | {}:{}'.format(
                day, name0, center_0.tmp_cost, name1, center_1.tmp_cost) +
                     '\n')
            sf.write('day[{}] 当日收入:  {}:{} | {}:{}'.format(
                day, name0, center_0.tmp_income, name1, center_1.tmp_income) +
                     '\n')
            sf.write('day[{}] 当日盈利:  {}:{} | {}:{}'.format(
                day, name0, center_0.tmp_profit, name1, center_1.tmp_profit) +
                     '\n')
            sf.write('day[{}] 累计盈利:  {}:{} | {}:{}'.format(
                day, name0, center_0.profit, name1, center_1.profit) + '\n')
            sf.write('--------------------------------------------\n')

    return center_0.profit, center_1.profit, sum(access_0), sum(access_1), len(prices_0), \
            sum(expect_0), sum(expect_1)


def plot_center(center, player_name):
    save_path_player = save_path + '/' + player_name
    if not os.path.exists(save_path_player):
        os.mkdir(save_path_player)

    xx = [i + 1 for i in range(len(center.profit_per_day))]
    plt.plot(xx,
             center.servers_working_rate_per_day,
             color='red',
             label='total_servers_working_rate')
    plt.plot(xx,
             center.servers_cpu_rate_per_day,
             color='green',
             label='total_servers_cpu_rate')
    plt.plot(xx,
             center.servers_memory_rate_per_day,
             color='blue',
             label='total_servers_memory_rate')
    plt.legend()
    plt.title("all server working status_" + player_name)
    plt.xlabel("day")
    # plt.show()
    plt.savefig(save_path_player + "/all server working status_" +
                player_name + ".png")
    plt.clf()

    plt.plot(xx, center.profit_per_day, color='red', label='profit_per_day')
    plt.plot(xx, center.income_per_day, color='green', label='income_per_day')
    plt.plot(xx,
             center.all_cost_per_day,
             color='blue',
             label='all_cost_per_day')
    plt.legend()
    plt.title("profit income cost per day_" + player_name)
    plt.xlabel("day")
    plt.savefig(save_path_player + "/profit income cost per day_" +
                player_name + ".png")
    # plt.show()
    plt.clf()

    plt.plot(xx, center.pur_num_per_day, color='red', label='servers_pur_num')
    plt.legend()
    plt.title("servers pur num_" + player_name)
    plt.xlabel("day")
    # plt.show()
    plt.savefig(save_path_player + "/servers pur num_" + player_name + ".png")
    plt.clf()

    plt.plot(xx,
             center.mig_times_per_day,
             color='blue',
             label='migration_nums')
    plt.legend()
    plt.title("migration num_" + player_name)
    plt.xlabel("day")
    # plt.show()
    plt.savefig(save_path_player + "/migration num_" + player_name + ".png")
    plt.clf()


def simulate(input_lines, player_0, player_1, file_name):
    input_lines = process_host_vm_info(input_lines, player_0, player_1)
    player_0.stdin.write(input_lines[0].encode())
    player_1.stdin.write(input_lines[0].encode())
    requests = get_requests(input_lines)
    num_days, num_knows = map(int, input_lines[0].strip().split())
    for i in range(num_knows):
        write_day_requests(requests[i], player_0)
        write_day_requests(requests[i], player_1)
    player_0.stdin.flush()
    player_1.stdin.flush()
    player_0_profit = []
    player_1_profit = []
    player_0_num = []
    player_1_num = []
    player_0_num_all = []
    player_1_num_all = []
    total_add_num = []
    expect_0_num = []
    expect_1_num = []
    for i in tqdm(range(len(requests))):
        profit0, profit1, num_0, num_1, add_all, expect_0, expect_1 = simulate_on_day(
            player_0, player_1, requests[i], i)
        player_0_profit.append(profit0)
        player_1_profit.append(profit1)
        player_0_num.append(num_0)
        player_1_num.append(num_1)
        if len(player_0_num_all) != 0:
            player_0_num_all.append(player_0_num[-1] + player_0_num_all[-1])
        else:
            player_0_num_all.append(player_0_num[-1])
        if len(player_1_num_all) != 0:
            player_1_num_all.append(player_1_num[-1] + player_1_num_all[-1])
        else:
            player_1_num_all.append(player_1_num[-1])
        expect_0_num.append(expect_0)
        expect_1_num.append(expect_1)
        total_add_num.append(add_all)
        if i + num_knows < num_days:
            write_day_requests(requests[i + num_knows], player_0)
            write_day_requests(requests[i + num_knows], player_1)
        if player_0.poll() is None:
            player_0.stdin.flush()
        if player_1.poll() is None:
            player_1.stdin.flush()

    print('-' * 50)
    ply0, ply1 = sys.argv[3].split('/')[-1], sys.argv[5].split('/')[-1]
    winner = ply0 if profit0 > profit1 else ply1
    if profit0 > profit1:
        print("[\033[36m{}\033[0m -> \033[32m{}\033[0m VS \033[31m{}\033[0m]\n".format(
            file_name, ply0, ply1))
    else:
        print("[\033[36m{}\033[0m -> \033[31m{}\033[0m VS \033[32m{}\033[0m]\n".format(
            file_name, ply0, ply1))

    print(
        "* player 0: profit: {}  total_add_req_num: {}  total_expect_num: {}".
        format(profit0, sum(player_0_num), sum(expect_0_num)),
        end=', ')
    print("total_cost: {}  total_income: {}".format(center_0.cost,
                                                    center_0.income))
    print(
        "* player 1: profit: {}  total_add_req_num: {}  total_expect_num: {}".
        format(profit1, sum(player_1_num), sum(expect_1_num)),
        end=', ')
    print("total_cost: {}  total_income: {}".format(center_1.cost,
                                                    center_1.income))

    print('*' * 50)

    if VIEW:
        with open(battle_info_per_day_path, 'a', encoding="utf-8") as sf:
            sf.write('*' * 50 + '\n')
            sf.write('*' * 50 + '\n')
            sf.write("winner: player {}".format(winner) + '\n')
            sf.write(
                "player 0 {} : profit: {}  total_add_req_num: {}  total_expect_num: {}"
                .format(sys.argv[3].split('/')[-1], profit0, sum(player_0_num),
                        sum(expect_0_num)) + '\n')
            sf.write("\t\t total_cost: {}  total_income: {}".format(
                center_0.cost, center_0.income) + '\n')
            sf.write(
                "player 1 {} : profit: {}  total_add_req_num: {}  total_expect_num: {}"
                .format(sys.argv[5].split('/')[-1], profit1, sum(player_1_num),
                        sum(expect_1_num)) + '\n')
            sf.write("\t\t total_cost: {}  total_income: {}".format(
                center_1.cost, center_1.income) + '\n')

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        xx = [i + 1 for i in range(len(requests))]
        ax1.plot(xx, player_0_profit, color='red', label='player_0')
        ax1.plot(xx, player_1_profit, color='green', label='player_1')
        ax1.legend(loc=2)
        plt.title("profit_num_" + sys.argv[3].split('/')[-1] + "_VS_" +
                  sys.argv[5].split('/')[-1] + "_" + sys.argv[1].split('.')[0])

        ax2 = ax1.twinx()
        ax2.plot(xx, player_0_num_all, color='blue', label='player_0_num')
        ax2.plot(xx, player_1_num_all, color='brown', label='player_1_num')
        ax2.legend(loc=1)

        plt.savefig(save_path + "/profit_num_" + sys.argv[3].split('/')[-1] +
                    "_VS_" + sys.argv[5].split('/')[-1] + "_" +
                    sys.argv[1].split('.')[0] + ".png")
        # plt.show()
        plt.clf()

        plt.plot(xx, player_0_num, color='red', label='player_0')
        plt.plot(xx, player_1_num, color='green', label='player_1')
        plt.plot(xx, total_add_num, color='blue', label='total_num')
        plt.legend()
        plt.title("num_" + sys.argv[3].split('/')[-1] + "_VS_" +
                  sys.argv[5].split('/')[-1] + "_" + sys.argv[1].split('.')[0])
        plt.xlabel("day")
        plt.savefig(save_path + "/num_" + sys.argv[3].split('/')[-1] + "_VS_" +
                    sys.argv[5].split('/')[-1] + "_" +
                    sys.argv[1].split('.')[0] + ".png")
        # plt.show()
        plt.clf()

        plot_center(center_0, sys.argv[3].split('/')[-1])
        plot_center(center_1, sys.argv[5].split('/')[-1])


def create_players(argv):
    sep_indices = [i for i, x in enumerate(argv) if x == '--']
    assert len(sep_indices) == 2, \
        "There should be exactly two separator '--' in the command line."
    player_0 = subprocess.Popen(argv[sep_indices[0] + 1:sep_indices[1]],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
    player_1 = subprocess.Popen(argv[sep_indices[1] + 1:],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
    return player_0, player_1


def main(argv):
    file_name = sys.argv[1].split('.')[0]
    player_0, player_1 = create_players(argv)
    test_data_path = argv[1]
    with open(test_data_path, 'r') as f:
        input_lines = f.readlines()
    try:
        simulate(input_lines, player_0, player_1, file_name)
    except SimulationError as error:
        print('player ' + str(error.player_id) + ' error: ' + error.message)
    # return_code_0 = player_0.wait()
    # return_code_1 = player_1.wait()
    # print('player 0 return code: ' + str(return_code_0))
    # print('player 1 return code: ' + str(return_code_1))


if __name__ == "__main__":
    if VIEW:
        battle_log_path = "./battle_log"
        if not os.path.exists(battle_log_path):
            os.mkdir(battle_log_path)
        save_path = battle_log_path + '/' + sys.argv[3].split('/')[-1] + "_VS_" +\
                    sys.argv[5].split('/')[-1] + '_on_' + sys.argv[1].split('.')[0]
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        battle_info_per_day_path = save_path + '/' + 'battle_info.txt'
        with open(battle_info_per_day_path, 'w', encoding="utf-8") as sf:
            sf.write(sys.argv[3].split('/')[-1] + "   VS   " +
                     sys.argv[5].split('/')[-1] + " on " +
                     sys.argv[1].split('.')[0] + '\n')
            sf.write('---------------------------------------\n')
            sf.write('\n')
    main(sys.argv)
