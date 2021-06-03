#pragma once

#include <algorithm>
#include <cstring>
#include <iostream>
#include <memory>
#include <unordered_map>
#include <vector>

#include "log.h"
#include "server.h"
using namespace std;

class Server;

struct ProtoVm {
    ProtoVm(string _name, int _type_id, int _cpu, int _ram, int _double_deploy) {
        name = _name;
        type_id = _type_id;
        cpu = _cpu;
        ram = _ram;
        double_deploy = _double_deploy;
        delta_cpu_ratio = (double)(cpu - ram) / (double)cpu;
        delta_ram_ratio = (double)(ram - cpu) / (double)ram;
        weighted_resource = cpu * 2 + ram;
    }
    string name;                            // 类型名称
    int type_id;                            // 类型id
    int cpu;                                // cpu
    int ram;                                // memory
    bool double_deploy;                     // 是否双点部署(false:单; true：双)
    double delta_cpu_ratio = 0;             // cpu-mem/cpu
    double delta_ram_ratio = 0;             // mem-cpu/mem
    int weighted_resource = 0;              // size
    double predict_hv = 0, predict_ev = 0;  // 按照总天数均摊，预测硬件成本和电费
};

class VirtualMachine {
   public:
    VirtualMachine() {}
    VirtualMachine(const shared_ptr<ProtoVm> &proto_vm, int id, int create_t, int duration_t, int user_price) {
        m_proto_vm = proto_vm;
        m_id = id;
        m_create_time = create_t;
        m_duration_time = duration_t;
        m_user_price = user_price;
        m_destory_time = m_create_time + m_duration_time;
    }

    inline const int &GetID() const { return m_id; }
    inline const string &GetName() const { return m_proto_vm->name; }
    inline const shared_ptr<ProtoVm> &GetProtoVm() { return m_proto_vm; }
    inline const int &GetNode() const { return m_node; }
    inline const bool &DoubleDeploy() const { return m_proto_vm->double_deploy; }
    inline const shared_ptr<Server> &GetBindServer() const { return m_bind_svr; }
    inline const int &GetCpu() const { return m_proto_vm->cpu; }
    inline const int &GetRam() const { return m_proto_vm->ram; }
    inline const int GetRest() const { return m_proto_vm->cpu + m_proto_vm->ram; }
    inline const int GetWeightedRest() const { return m_proto_vm->weighted_resource; }
    inline const int &GetDurationTime() const { return m_duration_time; }
    inline const int &GetOfferPrice() const { return m_offer_price; }
    inline const double &GetDeltaCpuRatio() const { return m_proto_vm->delta_cpu_ratio; }
    inline const double &GetDeltaRamRatio() const { return m_proto_vm->delta_ram_ratio; }
    inline const int GetUserPrice() const { return m_user_price; }
    inline void SetOfferPrice(int price) { m_offer_price = price; }
    inline const int GetDestoryTime() const { return m_destory_time; }
    inline void SetNode(int node) { m_node = node; }
    inline void SetBindServer(const shared_ptr<Server> &svr) { m_bind_svr = svr; }

   public:
    void debug() {
        log_debug(
            "* vm: %s, id: %d, cpu: %d, ram: %d, create_t: %d, duration_t: %d, user_price: %d, offer_price: %d, "
            "discount: %.3f",
            m_proto_vm->name.c_str(), m_id, m_proto_vm->cpu, m_proto_vm->ram, m_create_time, m_duration_time,
            m_user_price, m_offer_price, (double)m_offer_price / (double)m_user_price);
    }

   private:
    shared_ptr<ProtoVm> m_proto_vm = nullptr;  // 虚拟机类型
    shared_ptr<Server> m_bind_svr = nullptr;   // 当前在哪台服务器上
    int m_id = -1;                             // 虚拟机id
    int m_node = -1;                           // 在服务器的哪个结点(0: A, 1: B, -1:双)
    int m_create_time;                         // 创建时间
    int m_duration_time;                       // 持续时间
    int m_destory_time;                        // 销毁时间
    int m_user_price;                          // 用户报价
    int m_offer_price = -1;                    // 成交价
};