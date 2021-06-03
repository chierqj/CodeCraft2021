#pragma once

#include <algorithm>
#include <cstring>
#include <iostream>
#include <memory>
#include <unordered_set>
#include <vector>

#include "virtual_machine.h"
using namespace std;

class VirtualMachine;

class Server {
   public:
    Server() {}
    Server(string name, int type_id, int cpu, int ram, int hv, int ev) {
        m_name = name;
        m_type_id = type_id;
        m_cpu_a = m_cpu_b = cpu >> 1;
        m_ram_a = m_ram_b = ram >> 1;
        m_proto_cpu = cpu;
        m_proto_ram = ram;
        m_hardware_cost = hv;
        m_energy_cost = ev;
        m_inv_cpu = 1.0 / (double)m_proto_cpu;
        m_inv_ram = 1.0 / (double)m_proto_ram;
    }
    Server(const shared_ptr<Server> &svr) {
        m_id = svr->m_id;
        m_name = svr->m_name;
        m_cpu_a = svr->m_cpu_a;
        m_ram_a = svr->m_ram_a;
        m_cpu_b = svr->m_cpu_b;
        m_ram_b = svr->m_ram_b;
        m_proto_cpu = svr->m_proto_cpu;
        m_proto_ram = svr->m_proto_ram;
        m_hardware_cost = svr->m_hardware_cost;
        m_energy_cost = svr->m_energy_cost;
        m_type_id = svr->m_type_id;
        m_inv_cpu = svr->m_inv_cpu;
        m_inv_ram = svr->m_inv_ram;
        m_vm_list = svr->m_vm_list;
    }

   public:
    inline const string &GetName() const { return m_name; }
    inline const int &GetCpuA() const { return m_cpu_a; }
    inline const int &GetCpuB() const { return m_cpu_b; }
    inline const int &GetRamA() const { return m_ram_a; }
    inline const int &GetRamB() const { return m_ram_b; }
    inline const int &GetProtoCpu() const { return m_proto_cpu; }
    inline const int &GetProtoRam() const { return m_proto_ram; }
    inline const int &GetHardwareCost() const { return m_hardware_cost; }
    inline const int &GetEnergyCost() const { return m_energy_cost; }
    inline const int &GetID() const { return m_id; }
    inline const unordered_set<shared_ptr<VirtualMachine>> &GetVirList() const { return m_vm_list; }
    inline const int GetRest() const { return m_cpu_a + m_cpu_b + m_ram_a + m_ram_b; }
    inline const int GetRestA() const { return m_cpu_a + m_ram_a; }
    inline const int GetRestB() const { return m_cpu_b + m_ram_b; }
    inline const int GetWeightedRest() const {
        int cpu = m_cpu_a + m_cpu_b;
        int ram = m_ram_a + m_ram_b;
        return cpu * 2 + ram;
    }
    inline const int GetWeightedRestA() const {
        int cpu = m_cpu_a, ram = m_ram_a;
        return cpu * 2 + ram;
    }
    inline const int GetWeightedRestB() const {
        int cpu = m_cpu_b, ram = m_ram_b;
        return cpu * 2 + ram;
    }
    inline const int GetTypeID() const { return m_type_id; }
    inline const double &GetInvCPU() const { return m_inv_cpu; }
    inline const double &GetInvMem() const { return m_inv_ram; }
    inline const int &GetBuyTime() const { return m_buy_time; }
    inline const int &GetDestoreTime() const { return m_destore_time; }

    inline void SetID(int id) { m_id = id; }
    inline void SetBuyTime(int t) { m_buy_time = t; }
    inline void SetDestoreTime(int t) { m_destore_time = t; }

   public:
    void debug();
    void add_vm(const shared_ptr<VirtualMachine> &vm, int node);
    void del_vm(const shared_ptr<VirtualMachine> &vm, int node);
    int get_update_deltime();
    void save_state() {
        m_memento_cpu_a = m_cpu_a;
        m_memento_cpu_b = m_cpu_b;
        m_memento_ram_a = m_ram_a;
        m_memento_ram_b = m_ram_b;
        m_memento_vm_list = m_vm_list;
    }
    void recover_state() {
        m_cpu_a = m_memento_cpu_a;
        m_cpu_b = m_memento_cpu_b;
        m_ram_a = m_memento_ram_a;
        m_ram_b = m_memento_ram_b;
        m_vm_list = m_memento_vm_list;
    }

   private:
    string m_name;                                        // 类型名
    int m_id = -1;                                        // id
    int m_type_id;                                        // 类型id
    int m_hardware_cost;                                  // 硬件成本
    int m_energy_cost;                                    // 能耗成本
    int m_cpu_a, m_ram_a;                                 // A 实时
    int m_cpu_b, m_ram_b;                                 // B 实时
    int m_proto_cpu, m_proto_ram;                         // 读入
    double m_inv_cpu, m_inv_ram;                          // cpu, ram倒数
    int m_buy_time;                                       // 购买日期
    unordered_set<shared_ptr<VirtualMachine>> m_vm_list;  // 当前server部署的虚拟机数量
    int m_destore_time = 0;                               // 销毁时间

    // memento
    int m_memento_cpu_a, m_memento_cpu_b;
    int m_memento_ram_a, m_memento_ram_b;
    unordered_set<shared_ptr<VirtualMachine>> m_memento_vm_list;
};
