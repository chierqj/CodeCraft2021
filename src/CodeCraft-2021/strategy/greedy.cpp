#include "greedy.h"

#include <map>
#include <unordered_set>

void Greedy::output() {
    printf("(purchase, %d)\n", (int)m_dayily_buyed_svrs.size());
    for (auto& it : m_dayily_buyed_svrs) {
        for (auto& svr : it.second) {
            svr->SetID(m_global_svr_id++);
        }
        printf("(%s, %d)\n", it.first.c_str(), (int)it.second.size());
    }
    printf("(migration, %d)\n", (int)m_migration_result.size());
    for (auto& it : m_migration_result) {
        int vir_id = std::get<0>(it);
        const auto& svr_to = std::get<1>(it);
        int node = std::get<2>(it);
        if (node == -1) {
            printf("(%d, %d)\n", vir_id, svr_to->GetID());
        } else {
            char c = 'A' + node;
            printf("(%d, %d, %c)\n", vir_id, svr_to->GetID(), c);
        }
    }

    for (auto& req : m_requests) {
        if (req->GetType() == REQ_TYPE::DEL) continue;
        const auto& vir = req->GetBindVm();
        if (vir->DoubleDeploy()) {
            printf("(%d)\n", vir->GetBindServer()->GetID());
        } else {
            char c = vir->GetNode() + 'A';
            printf("(%d, %c)\n", vir->GetBindServer()->GetID(), c);
        }
    }
    fflush(stdout);
}

void Greedy::HandleDailyRequests(const vector<shared_ptr<Request>>& daily_requests, int day, int future_k_vm_cpu,
                                 int future_k_vm_mem) {
    m_requests.clear();
    m_future_k_vm_cpu = future_k_vm_cpu;
    m_future_k_vm_mem = future_k_vm_mem;
    m_today_idx = day;
    m_migra_count = m_VirtualPoolSize * 3 / 100;
    if (day == m_tol_day - 3) m_migra_count = m_VirtualPoolSize;
    log_debug("day: %d", day);
    this->migration();
    log_debug("start bidding");
    this->bidding(daily_requests);
    log_debug("start purchase");
    this->purchase();
    log_debug("start output");
    this->output();
}

void Greedy::Initalize() {
    log_debug("Initalize start.");

    m_model = make_shared<LinearRegression>();
    m_model->Train(m_servers, m_tol_day);

    this->pretreat();

    for (auto& proto_vm : m_proto_vms) {
        auto predict = m_model->Predict(proto_vm->cpu, proto_vm->ram, m_tol_day, 0);
        proto_vm->predict_hv = predict.first;
        proto_vm->predict_ev = predict.second;
    }

    log_debug("Initalize end.");
}

void Greedy::debug() {}

void Greedy::set_discount() {
    auto sigmod = [&](double x) { return 1.0 / (1 + exp(-x)); };

    int decay_day = m_tol_day * 0.5;
    double x = (m_today_idx - decay_day) * 10 / m_tol_day;
    double ideal_rate = 1.0 - sigmod(x) * 0.9;

    double up = m_pre_actual_price[m_today_idx - 1];
    double down = m_pre_total_price[m_today_idx - 1];
    int K = 10;
    if (m_today_idx > K) {
        up -= m_pre_actual_price[m_today_idx - K];
        down -= m_pre_total_price[m_today_idx - K];
    }
    double his_rate = up / down;

    m_discount = 1.0 + (his_rate - ideal_rate) * 0.2 / ideal_rate;
}

void Greedy::bidding(const vector<shared_ptr<Request>>& daily_requests) {
    this->save_state();
    m_requests = daily_requests;
    this->purchase();

    this->set_discount();

    int add_req_nums = 0;
    for (auto req : daily_requests) {
        if (req->GetType() == REQ_TYPE::DEL) continue;
        add_req_nums++;
    }
    bool breakout_day = false;
    int avg_add_nums = m_totol_req_nums / m_normal_days;
    if (m_today_idx > 0 && add_req_nums > 3 * avg_add_nums) {
        breakout_day = true;
        m_discount = m_discount * (1 - 0.1 * (m_tol_day - m_today_idx) / m_tol_day);
    }

    auto cal_offer_price = [&](const shared_ptr<VirtualMachine>& vm) {
        int buyday = vm->GetBindServer()->GetBuyTime();
        int user_price = vm->GetUserPrice();
        int days = vm->GetDurationTime();

        double day_rate = (double)m_tol_day / (double)(m_tol_day - buyday);
        double hv = vm->GetProtoVm()->predict_hv * day_rate;
        double ev = vm->GetProtoVm()->predict_ev;

        bool big = vm->GetProtoVm()->predict_hv <= vm->GetUserPrice();
        int offer_price = 0;

        if (big) {
            offer_price = (hv * days + ev * days * (1 - 0.1 * m_today_idx / m_tol_day)) * m_discount;
        } else {
            offer_price = (hv * days * (1 - 0.1 * m_today_idx / m_tol_day) + ev * days) * m_discount;
        }

        if (offer_price <= 0 || offer_price > user_price) {
            offer_price = buyday == m_today_idx ? -1 : user_price;
        }
        return offer_price;
    };

    vector<shared_ptr<Request>> add_req;

    for (auto& req : daily_requests) {
        if (req->GetType() == REQ_TYPE::DEL) continue;
        add_req.push_back(req);
        auto vm = req->GetBindVm();
        int offer_price = cal_offer_price(vm);
        vm->SetOfferPrice(offer_price);
        printf("%d\n", offer_price);
        if (offer_price != -1) {
            m_totol_offer_price += offer_price;
        }
    }

    this->recover_state();

    log_debug("-------------------------------------- day: %d ---------------------------", m_today_idx);
    log_debug("days   cpu    ram    price   enemy_p  m_price   hv    ev    m_dis  enemy_dis suc");

    m_enemy_delta_discount = 0;
    double fail_count = 0;
    for (auto& req : add_req) {
        int suc, enemy_price;
        m_getline("(%d, %d)", &suc, &enemy_price);
        auto vm = req->GetBindVm();
        if (suc == 1) {
            m_global_obtain_vm_pool.insert(vm->GetID());
            m_totol_actual_price += vm->GetOfferPrice();
        } else {
            double rate = double(vm->GetUserPrice() - enemy_price) / (double)vm->GetUserPrice();
            m_enemy_delta_discount += rate;
            fail_count++;
        }
        if (enemy_price != -1) {
            if (suc == 0) m_enemy_totol_actual_price += enemy_price;
            m_enemy_totol_offer_price += enemy_price;
        }

        // debug
        double m_discount = (double)vm->GetOfferPrice() / (double)vm->GetUserPrice();
        double enemy_discount = (double)enemy_price / (double)vm->GetUserPrice();
        log_debug("%-6d %-6d %-6d %-8d %-8d %-8d %.3f %.3f %.3f   %.3f  %d", vm->GetDurationTime(), vm->GetCpu(),
                  vm->GetRam(), vm->GetUserPrice(), enemy_price, vm->GetOfferPrice(), vm->GetProtoVm()->predict_hv,
                  vm->GetProtoVm()->predict_ev, m_discount, enemy_discount, suc);
    }

    m_enemy_delta_discount /= fail_count;
    m_pre_total_price[m_today_idx] = m_totol_offer_price;
    m_pre_actual_price[m_today_idx] = m_totol_actual_price;

    if (!breakout_day) {
        m_normal_days++;
        m_totol_req_nums += add_req_nums;
    }

    for (auto& req : daily_requests) {
        auto vm = req->GetBindVm();
        if (m_global_obtain_vm_pool.find(vm->GetID()) == m_global_obtain_vm_pool.end()) {
            vm->SetBindServer(nullptr);
            vm->SetNode(-1);
            continue;
        }
        m_requests.push_back(req);
    }
}