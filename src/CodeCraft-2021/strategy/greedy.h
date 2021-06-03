#pragma once

#include <cmath>
#include <memory>
#include <vector>

#include "linear_regression.h"
#include "scenario/log.h"
#include "scenario/request.h"
#include "scenario/server.h"
#include "scenario/tools.h"
#include "scenario/virtual_machine.h"

class Greedy {
   public:
    Greedy(const vector<shared_ptr<Server>> &svrs, const vector<shared_ptr<ProtoVm>> &proto_vms, const int &tol_day)
        : m_servers(svrs), m_proto_vms(proto_vms), m_tol_day(tol_day) {
        m_pre_actual_price = vector<double>(m_tol_day + 1, 0);
        m_pre_total_price = vector<double>(m_tol_day + 1, 0);
    }

    void Initalize();  // 初始化
    void HandleDailyRequests(const vector<shared_ptr<Request>> &daily_requests, int day, int future_k_vm_cpu,
                             int future_k_vm_mem);  // 处理每日请求
    void debug();                                   // 统计数据

   private:
    void pretreat();                                                  // 预处理
    void bidding(const vector<shared_ptr<Request>> &daily_requests);  // 竞价
    void migration();                                                 // 迁移
    void purchase();                                                  // 部署
    void output();                                                    // 输出每日结果

    bool match_double_node(const shared_ptr<Server> &svr, const shared_ptr<ProtoVm> &vm);         // 满足部署
    bool match_node_a(const shared_ptr<Server> &svr, const shared_ptr<ProtoVm> &vm);              // 满足部署
    bool match_node_b(const shared_ptr<Server> &svr, const shared_ptr<ProtoVm> &vm);              // 满足部署
    bool match_double_node(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm);  // 满足部署
    bool match_node_a(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm);       // 满足部署
    bool match_node_b(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm);       // 满足部署
    void reorder_request_list(vector<vector<shared_ptr<Request>>> &new_req_list);
    bool purchase_old_server(const shared_ptr<VirtualMachine> &vm);  // 在已有部署
    bool purchase_new_server(const shared_ptr<VirtualMachine> &vm);  // 在新购部署
    inline void handle_add_svr(shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm, int node);
    inline void handle_del_svr(const shared_ptr<VirtualMachine> &vm);
    inline void handle_move_svr(shared_ptr<Server> &svr_to, const shared_ptr<VirtualMachine> &vm, int node);
    inline double get_used_rate(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm, int node);
    inline int cal_offer_price(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm);
    void set_discount();

    void save_state() {
        for (auto &svr : m_buyed_svr_pool) {
            svr->save_state();
        }
        m_memento_VirtualPoolSize = m_VirtualPoolSize;
        m_memento_global_svr_id = m_global_svr_id;
        m_memento_buyed_svr_pool = m_buyed_svr_pool;
    }
    void recover_state() {
        for (auto &svr : m_buyed_svr_pool) {
            svr->recover_state();
        }
        m_VirtualPoolSize = m_memento_VirtualPoolSize;
        m_global_svr_id = m_memento_global_svr_id;
        m_buyed_svr_pool = m_memento_buyed_svr_pool;
        m_requests.clear();
    }

   private:
    const vector<shared_ptr<Server>> &m_servers;     // 读入服务器
    const vector<shared_ptr<ProtoVm>> &m_proto_vms;  // 读入虚拟机
    int m_tol_day = 0;                               // 总天数
    shared_ptr<LinearRegression> m_model;            // 线性回归

    vector<vector<shared_ptr<Server>>> m_reset_svr_pool;                    // 预处理
    vector<shared_ptr<Request>> m_requests;                                 // 当天拿到的请求
    int m_future_k_vm_cpu = 0;                                              // 未来k天vm_cpu
    int m_future_k_vm_mem = 0;                                              // 未来k天vm_ram
    int m_today_idx = 0;                                                    // 今天是第几天
    int m_VirtualPoolSize = 0;                                              // 当前已经虚拟机的总数
    int m_migra_count = 0;                                                  // 迁移次数
    int m_global_svr_id = 0;                                                // 服务器全局id
    unordered_map<string, vector<shared_ptr<Server>>> m_dayily_buyed_svrs;  // 当天购买服务器
    vector<tuple<int, shared_ptr<Server>, int>> m_migration_result;         // vir->svr_to->localnode
    vector<shared_ptr<Server>> m_buyed_svr_pool;                            // 已经购买的svr
    unordered_set<int> m_global_obtain_vm_pool;                             // 获取到的所有虚拟机的id集合
    double m_enemy_delta_discount;                                          // 对手的昨日折扣
    double m_totol_offer_price = 0.1;                                       // 历史自己报价和[!-1]
    double m_totol_actual_price = 0.1;                                      // 历史实际报价和[!-1]
    double m_enemy_totol_offer_price = 0.1;                                 // 历史自己报价和[!-1]
    double m_enemy_totol_actual_price = 0.1;                                // 历史实际报价和[!-1]
    double m_discount;
    int m_totol_req_nums = 0;
    int m_normal_days = 0;
    vector<double> m_pre_actual_price;
    vector<double> m_pre_total_price;
    vector<int> m_pre_total_req_nums;
    // memento
    int m_memento_VirtualPoolSize = 0;
    int m_memento_global_svr_id = 0;
    vector<shared_ptr<Server>> m_memento_buyed_svr_pool;
};

inline void Greedy::handle_add_svr(shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm, int node) {
    svr->add_vm(vm, node);
    vm->SetBindServer(svr);
    vm->SetNode(node);
}
inline void Greedy::handle_del_svr(const shared_ptr<VirtualMachine> &vm) {
    auto &bind_svr = vm->GetBindServer();
    if (bind_svr == nullptr) return;
    bind_svr->del_vm(vm, vm->GetNode());
}
inline void Greedy::handle_move_svr(shared_ptr<Server> &svr_to, const shared_ptr<VirtualMachine> &vm, int node) {
    this->handle_del_svr(vm);
    this->handle_add_svr(svr_to, vm, node);
}

inline int Greedy::cal_offer_price(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm) {
    int cpu = vm->GetCpu(), ram = vm->GetRam();
    int buyday = svr->GetBuyTime();
    int days = vm->GetDurationTime();
    auto predict = m_model->Predict(cpu, ram, m_tol_day, buyday);
    double hv = predict.first, ev = predict.second;
    double total_ev = ev * days * (1 - 0.1 * m_today_idx / m_tol_day);
    int offer_price = hv * days + total_ev;
    return offer_price;
}

inline bool Greedy::match_double_node(const shared_ptr<Server> &svr, const shared_ptr<ProtoVm> &vm) {
    int vm_cpu = vm->cpu >> 1, vm_mem = vm->ram >> 1;
    int cpu_a = svr->GetCpuA(), mem_a = svr->GetRamA();
    int cpu_b = svr->GetCpuB(), mem_b = svr->GetRamB();
    if (cpu_a >= vm_cpu && mem_a >= vm_mem && cpu_b >= vm_cpu && mem_b >= vm_mem) return true;
    return false;
}
inline bool Greedy::match_node_a(const shared_ptr<Server> &svr, const shared_ptr<ProtoVm> &vm) {
    int vm_cpu = vm->cpu, vm_mem = vm->ram;
    int cpu_a = svr->GetCpuA(), mem_a = svr->GetRamA();
    if (cpu_a >= vm_cpu && mem_a >= vm_mem) return true;
    return false;
}
inline bool Greedy::match_node_b(const shared_ptr<Server> &svr, const shared_ptr<ProtoVm> &vm) {
    int vm_cpu = vm->cpu, vm_mem = vm->ram;
    int cpu_b = svr->GetCpuB(), mem_b = svr->GetRamB();
    if (cpu_b >= vm_cpu && mem_b >= vm_mem) return true;
    return false;
}
inline bool Greedy::match_double_node(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm) {
    int vm_cpu = vm->GetCpu() >> 1, vm_mem = vm->GetRam() >> 1;
    int cpu_a = svr->GetCpuA(), mem_a = svr->GetRamA();
    int cpu_b = svr->GetCpuB(), mem_b = svr->GetRamB();
    if (cpu_a >= vm_cpu && mem_a >= vm_mem && cpu_b >= vm_cpu && mem_b >= vm_mem) return true;
    return false;
}
inline bool Greedy::match_node_a(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm) {
    int vm_cpu = vm->GetCpu(), vm_mem = vm->GetRam();
    int cpu_a = svr->GetCpuA(), mem_a = svr->GetRamA();
    if (cpu_a >= vm_cpu && mem_a >= vm_mem) return true;
    return false;
}
inline bool Greedy::match_node_b(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm) {
    int vm_cpu = vm->GetCpu(), vm_mem = vm->GetRam();
    int cpu_b = svr->GetCpuB(), mem_b = svr->GetRamB();
    if (cpu_b >= vm_cpu && mem_b >= vm_mem) return true;
    return false;
}

inline double Greedy::get_used_rate(const shared_ptr<Server> &svr, const shared_ptr<VirtualMachine> &vm, int node) {
    int vir_cpu = vm->GetCpu(), vir_mem = vm->GetRam();

    double inv_cpu = svr->GetInvCPU(), inv_mem = svr->GetInvMem();
    int cpu_a = svr->GetCpuA(), mem_a = svr->GetRamA();
    int cpu_b = svr->GetCpuB(), mem_b = svr->GetRamB();

    double cpu = (node == -1 ? (cpu_a + cpu_b) : node == 0 ? cpu_a : cpu_b) - vir_cpu;
    double mem = (node == -1 ? (mem_a + mem_b) : node == 0 ? mem_a : mem_b) - vir_mem;
    double x = cpu * inv_cpu, y = mem * inv_mem;
    return (x * x + y * y) * sqrt(svr->GetEnergyCost());
}
