#include "server.h"

#include "log.h"

void Server::add_vm(const shared_ptr<VirtualMachine> &vm, int node) {
    int vm_cpu = vm->GetCpu(), vm_ram = vm->GetRam();
    if (vm->DoubleDeploy()) {
        vm_cpu /= 2;
        vm_ram /= 2;
        m_cpu_a -= vm_cpu;
        m_ram_a -= vm_ram;
        m_cpu_b -= vm_cpu;
        m_ram_b -= vm_ram;
    } else {
        if (node == 0) {
            m_cpu_a -= vm_cpu;
            m_ram_a -= vm_ram;
        } else {
            m_cpu_b -= vm_cpu;
            m_ram_b -= vm_ram;
        }
    }
    m_vm_list.insert(vm);
}
void Server::del_vm(const shared_ptr<VirtualMachine> &vm, int node) {
    int vm_cpu = vm->GetCpu(), vm_ram = vm->GetRam();
    if (vm->DoubleDeploy()) {
        vm_cpu /= 2;
        vm_ram /= 2;
        m_cpu_a += vm_cpu;
        m_ram_a += vm_ram;
        m_cpu_b += vm_cpu;
        m_ram_b += vm_ram;
    } else {
        if (node == 0) {
            m_cpu_a += vm_cpu;
            m_ram_a += vm_ram;
        } else {
            m_cpu_b += vm_cpu;
            m_ram_b += vm_ram;
        }
    }
    m_vm_list.erase(vm);
}

void Server::debug() {
    log_debug("(Svr: %s, id: %d, hv: %d, ev: %d, proto:[%d, %d], a:[%d, %d], b:[%d, %d]", m_name.c_str(), m_id,
              m_hardware_cost, m_energy_cost, m_proto_cpu, m_proto_ram, m_cpu_a, m_ram_a, m_cpu_b, m_ram_b);
    // for (auto &it : m_vm_list) it->debug();
}

int Server::get_update_deltime() {
    int ans = 0;
    for (auto &it : m_vm_list) {
        ans = max(ans, it->GetDestoryTime());
    }
    return ans;
}