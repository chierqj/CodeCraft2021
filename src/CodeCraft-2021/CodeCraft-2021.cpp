#include <algorithm>
#include <cstring>
#include <ctime>
#include <iostream>
#include <unordered_map>
#include <vector>

#include "scenario/log.h"
#include "scenario/request.h"
#include "scenario/server.h"
#include "scenario/tools.h"
#include "scenario/virtual_machine.h"
#include "strategy/greedy.h"

using namespace std;

void RunFramework() {
    vector<shared_ptr<Server>> m_servers;            // 读入服务器
    vector<shared_ptr<ProtoVm>> m_proto_vms;         // 读入虚拟机
    vector<vector<shared_ptr<Request>>> m_requests;  // 读入请求

    int svr_n = 0;
    m_getline("%d", &svr_n);

    for (int i = 0; i < svr_n; ++i) {
        char c_name[32];
        int cpu, ram, hardware_cost, energy_cost;
        m_getline("(%[^,], %d, %d, %d, %d)", c_name, &cpu, &ram, &hardware_cost, &energy_cost);
        shared_ptr<Server> svr = make_shared<Server>(string(c_name), i, cpu, ram, hardware_cost, energy_cost);
        m_servers.push_back(svr);
    }

    int vm_n = 0;
    unordered_map<string, shared_ptr<ProtoVm>> hash_proto_vm;
    m_getline("%d\n", &vm_n);

    for (int i = 0; i < vm_n; ++i) {
        char c_name[32];
        int cpu, ram, double_deploy;
        m_getline("(%[^,], %d, %d, %d)", c_name, &cpu, &ram, &double_deploy);
        shared_ptr<ProtoVm> proto_vm = make_shared<ProtoVm>(string(c_name), i, cpu, ram, double_deploy);
        m_proto_vms.push_back(proto_vm);
        hash_proto_vm[proto_vm->name] = proto_vm;
    }

    int t, k;
    unordered_map<int, shared_ptr<VirtualMachine>> vm_pool;
    m_getline("%d %d\n", &t, &k);

    auto input_daily_req = [&](int day) {
        int req_n = 0;
        m_getline("%d", &req_n);
        vector<shared_ptr<Request>> vct_req;
        for (int i = 0; i < req_n; ++i) {
            string line;
            getline(cin, line);
            int id;
            if (sscanf(line.c_str(), "(del, %d)", &id)) {
                shared_ptr<VirtualMachine> vm = vm_pool[id];
                shared_ptr<Request> req = make_shared<Request>(REQ_TYPE::DEL, vm);
                vct_req.push_back(req);
            } else {
                char c_name[32];
                int duration_t, user_price;
                sscanf(line.c_str(), "(add, %[^,], %d, %d, %d)", c_name, &id, &duration_t, &user_price);

                shared_ptr<ProtoVm> proto_vm = hash_proto_vm[string(c_name)];
                shared_ptr<VirtualMachine> vm = make_shared<VirtualMachine>(proto_vm, id, day, duration_t, user_price);
                vm_pool[id] = vm;
                shared_ptr<Request> req = make_shared<Request>(REQ_TYPE::ADD, vm);
                vct_req.push_back(req);
            }
        }
        m_requests.push_back(vct_req);
    };

    for (int i = 0; i < k; ++i) input_daily_req(i);

    unique_ptr<Greedy> greedy(new Greedy(m_servers, m_proto_vms, t));
    greedy->Initalize();

    for (int i = 0; i < t; ++i) {
        log_debug("day: %d start...", i);
        vector<shared_ptr<Request>> requests;
        for (auto &req : m_requests[i]) {
            if (req->GetType() == REQ_TYPE::DEL && req->GetBindVm()->GetDestoryTime() != i &&
                req->GetBindVm()->GetBindServer() == nullptr) {
                continue;
            }
            requests.push_back(req);
        }
        // greedy->HandleDailyRequests(m_requests[i], i, 1, 1);
        greedy->HandleDailyRequests(requests, i, 1, 1);
        if (i < t - k) input_daily_req(i + k);
    }

    greedy->debug();
}

int main(int argc, char **argv) {
#ifdef LOCAL_DEBUG
    FILE *fp = fopen("./battle.log", "w");
    log_set_fp(fp);
#endif

    RunFramework();

    return 0;
}