#include <cmath>
#include <map>
#include <unordered_set>

#include "greedy.h"

void Greedy::reorder_request_list(vector<vector<shared_ptr<Request>>>& new_req_list) {
    if (m_requests.empty()) return;

    int add_sum = 0, del_sum = 0;
    for (auto& req : m_requests) {
        const auto& vm = req->GetBindVm();
        if (req->GetType() == REQ_TYPE::ADD) {
            add_sum += vm->GetRest();
        } else {
            if (vm->GetBindServer() != nullptr) del_sum += vm->GetRest();
        }
    }
    vector<shared_ptr<Request>> m_requests_copy(m_requests.begin(), m_requests.end());
    bool sign = (add_sum > del_sum);
    if (sign) {
        stable_sort(m_requests_copy.begin(), m_requests_copy.end(),
                    [&](const shared_ptr<Request>& req1, const shared_ptr<Request>& req2) {
                        if (req1->GetType() == req2->GetType()) {
                            return req1->GetBindVm()->GetRest() > req2->GetBindVm()->GetRest();
                        }
                        return req1->GetType() < req2->GetType();
                    });
    }
    vector<vector<shared_ptr<Request>>> vct_block;
    vector<shared_ptr<Request>> tmp;
    auto type = m_requests_copy.front()->GetType();
    for (auto& req : m_requests_copy) {
        if (req->GetType() == type) {
            tmp.push_back(req);
            continue;
        }
        vct_block.push_back(tmp);
        type = req->GetType();
        tmp.clear();
        tmp.push_back(req);
    }
    vct_block.push_back(tmp);
    for (auto& block : vct_block) {
        if (sign) {
            new_req_list.push_back(block);
            continue;
        }
        if (block.front()->GetType() == REQ_TYPE::ADD) {
            stable_sort(block.begin(), block.end(),
                        [&](const shared_ptr<Request>& req1, const shared_ptr<Request>& req2) {
                            return req1->GetBindVm()->GetRest() > req2->GetBindVm()->GetRest();
                        });
        }
        new_req_list.push_back(block);
    }
}

bool Greedy::purchase_old_server(const shared_ptr<VirtualMachine>& vm) {
    struct Node {
        double val;
        int node;
        shared_ptr<Server> svr;
        bool operator<(const Node& r) const { return val < r.val; }
    };

    vector<Node> vct;
    double vm_cpu_ratio = vm->GetDeltaCpuRatio();
    double vm_mem_ratio = vm->GetDeltaRamRatio();

    for (const auto& svr : m_buyed_svr_pool) {
        double cpu_a = svr->GetCpuA(), mem_a = svr->GetRamA();
        double cpu_b = svr->GetCpuB(), mem_b = svr->GetRamB();
        double svr_ratio_cpu_a = (cpu_a - mem_a) / cpu_a, svr_ratio_mem_a = (mem_a - cpu_a) / mem_a;
        double svr_ratio_cpu_b = (cpu_b - mem_b) / cpu_b, svr_ratio_mem_b = (mem_b - cpu_b) / mem_b;

        double base_val = 0;
        // int del_time = svr->get_update_deltime();
        // if (del_time > vm->GetDestoryTime()) {
        //     base_val = 0.4 * (vm->GetDestoryTime() - del_time) * svr->GetEnergyCost();
        // }
        if (vm->DoubleDeploy()) {
            if (match_double_node(svr, vm)) {
                double val = fabs(svr_ratio_cpu_a - vm_cpu_ratio) + fabs(svr_ratio_mem_a - vm_mem_ratio) +
                             fabs(svr_ratio_cpu_b - vm_cpu_ratio) + fabs(svr_ratio_mem_b - vm_mem_ratio);
                vct.push_back(Node{val + base_val, -1, svr});
            }
            continue;
        }
        if (match_node_a(svr, vm)) {
            double val = fabs(svr_ratio_cpu_a - vm_cpu_ratio) + fabs(svr_ratio_mem_a - vm_mem_ratio);
            vct.push_back(Node{val + base_val, 0, svr});
        }
        if (match_node_b(svr, vm)) {
            double val = fabs(svr_ratio_cpu_b - vm_cpu_ratio) + fabs(svr_ratio_mem_b - vm_mem_ratio);
            vct.push_back(Node{val + base_val, 1, svr});
        }
    }

    stable_sort(vct.begin(), vct.end());

    int r = vct.size() * (vm->DoubleDeploy() ? 0.6 : 0.5);

    shared_ptr<Server> select_svr = nullptr;
    double select_value = 0;
    int select_env = 0;
    int select_node = -1;

    for (int i = 0; i < r; ++i) {
        const auto& svr = vct[i].svr;
        double val = this->get_used_rate(svr, vm, vct[i].node);
        // int val = this->abs_offer_price(svr, vm);
        if (select_svr == nullptr || val < select_value || (val == select_value && svr->GetEnergyCost() < select_env)) {
            select_svr = svr;
            select_value = val;
            select_node = vct[i].node;
            select_env = svr->GetEnergyCost();
        }
    }

    if (select_svr == nullptr) return false;
    this->handle_add_svr(select_svr, vm, select_node);
    return true;
}

void Greedy::pretreat() {
    m_reset_svr_pool = vector<vector<shared_ptr<Server>>>(m_proto_vms.size() + 7);

    for (auto& vm : m_proto_vms) {
        vector<pair<double, shared_ptr<Server>>> vct;
        double vm_cpu_ratio = vm->delta_cpu_ratio;
        double vm_mem_ratio = vm->delta_ram_ratio;

        for (const auto& svr : m_servers) {
            if (vm->double_deploy && !match_double_node(svr, vm)) continue;
            if (!vm->double_deploy && !match_node_a(svr, vm)) continue;

            double cpu_a = svr->GetCpuA(), mem_a = svr->GetRamA();
            double svr_ratio_cpu_a = (cpu_a - mem_a) / cpu_a, svr_ratio_mem_a = (mem_a - cpu_a) / mem_a;
            double ratio = fabs(svr_ratio_cpu_a - vm_cpu_ratio) + fabs(svr_ratio_mem_a - vm_mem_ratio);
            vct.push_back({ratio, svr});
        }

        stable_sort(vct.begin(), vct.end());

        int r = max(min(1, (int)vct.size()), (int)(vct.size() * 0.5));

        for (int i = 0; i < r; ++i) {
            const auto& svr = vct[i].second;
            m_reset_svr_pool[vm->type_id].push_back(svr);
        }
    }
}

bool Greedy::purchase_new_server(const shared_ptr<VirtualMachine>& vm) {
    shared_ptr<Server> select_svr = nullptr;

    double select_value = 0;
    int delta_day = m_tol_day - m_today_idx;
    double cpu_hv_w = m_model->GetHVCpuW(), ram_hv_w = m_model->GetHVRamW();
    double base = cpu_hv_w / ram_hv_w;
    base = 2.0;

    for (auto& svr : m_reset_svr_pool[vm->GetProtoVm()->type_id]) {
        double hv = svr->GetHardwareCost();
        double ev = svr->GetEnergyCost() * delta_day;
        double cpu = svr->GetCpuA() + svr->GetCpuB();
        double ram = svr->GetRamA() + svr->GetRamB();
        double val = (hv + ev * 1.2) / (cpu * base + ram);
        if (select_svr == nullptr || val < select_value) {
            select_svr = svr;
            select_value = val;
        }
    }

    int local_node = vm->DoubleDeploy() ? -1 : 0;

    shared_ptr<Server> new_svr = std::make_shared<Server>(select_svr);
    this->handle_add_svr(new_svr, vm, local_node);
    new_svr->SetBuyTime(m_today_idx);
    m_buyed_svr_pool.push_back(new_svr);
    m_dayily_buyed_svrs[new_svr->GetName()].push_back(new_svr);

    return true;
}

void Greedy::purchase() {
    for (auto& it : m_dayily_buyed_svrs) it.second.clear();
    m_dayily_buyed_svrs.clear();

    vector<vector<shared_ptr<Request>>> new_req_list;
    this->reorder_request_list(new_req_list);

    for (auto& block : new_req_list) {
        if (block.front()->GetType() == REQ_TYPE::DEL) {
            m_VirtualPoolSize -= block.size();
            for (auto& req : block) {
                this->handle_del_svr(req->GetBindVm());
            }
            continue;
        }

        m_VirtualPoolSize += block.size();

        for (auto& req : block) {
            auto vm = req->GetBindVm();
            auto svr = vm->GetBindServer();
            if (this->purchase_old_server(vm)) continue;
            this->purchase_new_server(vm);
        }
    }
}

void Greedy::migration() {
    m_migration_result.clear();
    if (m_migra_count <= 0) return;

    vector<shared_ptr<Server>> svr_pool;
    for (auto& svr : m_buyed_svr_pool) {
        if (svr->GetVirList().empty()) continue;
        svr_pool.push_back(svr);
    }

    auto do_migration = [&]() {
        map<int, unordered_set<shared_ptr<Server>>> hash_svr_list;
        auto action_move = [&](shared_ptr<VirtualMachine>& vm, shared_ptr<Server>& svr_to, int node) {
            hash_svr_list[vm->GetBindServer()->GetWeightedRest()].erase(vm->GetBindServer());
            if (hash_svr_list[vm->GetBindServer()->GetWeightedRest()].empty()) {
                hash_svr_list.erase(vm->GetBindServer()->GetWeightedRest());
            }
            hash_svr_list[svr_to->GetWeightedRest()].erase(svr_to);
            if (hash_svr_list[svr_to->GetWeightedRest()].empty()) {
                hash_svr_list.erase(svr_to->GetWeightedRest());
            }

            this->handle_move_svr(svr_to, vm, node);
            hash_svr_list[svr_to->GetWeightedRest()].insert(svr_to);
        };

        for (auto& svr : svr_pool) {
            if (svr->GetVirList().empty()) continue;
            svr->SetDestoreTime(svr->get_update_deltime());
            hash_svr_list[svr->GetWeightedRest()].insert(svr);
        }

        vector<shared_ptr<VirtualMachine>> vir_list;
        int max_migra_count = 2 * m_migra_count;
        svr_pool.clear();
        for (auto it = hash_svr_list.rbegin(); it != hash_svr_list.rend(); it++) {
            for (auto svr : it->second) {
                svr_pool.push_back(svr);
                vir_list.insert(vir_list.end(), svr->GetVirList().begin(), svr->GetVirList().end());
            }
            if ((int)vir_list.size() >= max_migra_count) break;
        }

        stable_sort(vir_list.begin(), vir_list.end(),
                    [&](const shared_ptr<VirtualMachine>& vm1, const shared_ptr<VirtualMachine>& vm2) {
                        return vm1->GetWeightedRest() > vm2->GetWeightedRest();
                    });

        unordered_set<int> vis_svr_to_set, vis_svr_from_set;  // svr_to别往出迁移

        for (auto& vir : vir_list) {
            if (m_migra_count <= 0) return;
            if (vis_svr_to_set.find(vir->GetBindServer()->GetID()) != vis_svr_to_set.end()) continue;

            shared_ptr<Server> select_svr = nullptr;
            int select_value = this->cal_offer_price(vir->GetBindServer(), vir);
            int select_node = -1;
            int select_env = 0;

            auto iter = hash_svr_list.lower_bound(vir->GetWeightedRest());
            for (; iter != hash_svr_list.end(); ++iter) {
                const auto& svr_to_list = iter->second;
                for (auto svr_to : svr_to_list) {
                    if (svr_to == vir->GetBindServer()) continue;
                    if (svr_to->GetVirList().empty()) continue;
                    // if (vis_svr_from_set.find(svr_to->GetID()) != vis_svr_from_set.end()) continue;

                    vector<int> suc_node;
                    if (vir->DoubleDeploy() && this->match_double_node(svr_to, vir)) suc_node = {-1};
                    if (!vir->DoubleDeploy() && this->match_node_a(svr_to, vir)) suc_node.push_back(0);
                    if (!vir->DoubleDeploy() && this->match_node_b(svr_to, vir)) suc_node.push_back(1);
                    for (auto& node : suc_node) {
                        // double val = this->get_used_rate(svr_to, vir, node);
                        // int val = this->abs_offer_price(svr_to, vir);
                        int val = this->cal_offer_price(svr_to, vir);
                        if (select_svr == nullptr || val < select_value ||
                            (val == select_value && svr_to->GetEnergyCost() < select_env)) {
                            select_svr = svr_to;
                            select_value = val;
                            select_node = node;
                            select_env = svr_to->GetEnergyCost();
                        }
                    }
                }
            }
            if (select_svr != nullptr) {
                // vis_svr_from_set.insert(vir->GetBindServer()->GetID());
                vis_svr_to_set.insert(select_svr->GetID());
                action_move(vir, select_svr, select_node);
                m_migration_result.push_back({vir->GetID(), select_svr, select_node});
                --m_migra_count;
            }
        }
    };

    while (true) {
        int count = m_migra_count;
        do_migration();
        if (count == m_migra_count || m_migra_count <= 0) return;
    }
}
