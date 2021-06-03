#pragma once

#include <cassert>
#include <memory>
#include <vector>

#include "scenario/log.h"
#include "scenario/server.h"
using namespace std;

class LinearRegression {
   public:
    void Train(const vector<shared_ptr<Server>> &m_servers, int tol_day) {
        vector<vector<double>> X_train;
        vector<double> hv_train, ev_train;
        for (auto &svr : m_servers) {
            double cpu = svr->GetProtoCpu(), ram = svr->GetProtoRam();
            double hv = svr->GetHardwareCost(), ev = svr->GetEnergyCost();

            X_train.push_back({cpu / 100.0, ram / 100.0});
            hv_train.push_back(hv / (double)tol_day);
            ev_train.push_back(ev);
        }
        auto hv_res = this->fit(X_train, hv_train);
        auto ev_res = this->fit(X_train, ev_train);

        m_hvW1 = hv_res.first;
        m_hvW2 = hv_res.second;
        m_evW1 = ev_res.first;
        m_evW2 = ev_res.second;

        log_debug("hvW1: %.6f, hvW2: %.6f", m_hvW1, m_hvW2);
        log_debug("evW1: %.6f, evW2: %.6f", m_evW1, m_evW2);
    }
    pair<double, double> Predict(int cpu, int ram, int tol_day, int buyday) {
        double hv_a = m_hvW1 * (double)tol_day / (double)(tol_day - buyday);
        double hv_b = m_hvW2 * (double)tol_day / (double)(tol_day - buyday);
        double hv = hv_a * (double)cpu + hv_b * (double)ram;
        double ev = m_evW1 * (double)cpu + m_evW2 * (double)ram;
        return {hv, ev};
    }
    double PredictTolHv(int cpu, int ram, int tol_day) {
        double ans = m_hvW1 * tol_day * cpu + m_hvW2 * tol_day * ram;
        return ans;
    }
    double GetHVCpuW() { return m_hvW1; }
    double GetHVRamW() { return m_hvW2; }
    double GetEVCpuW() { return m_evW1; }
    double GetEVRamW() { return m_evW2; }

   private:
    pair<double, double> fit(const vector<vector<double>> &X_train, vector<double> y_train) {
        int n = X_train.size(), m = X_train[0].size();

        vector<double> W(m, 0);
        auto self_predict = [&](const vector<double> &x) {
            double ans = 0;
            for (int i = 0; i < (int)x.size(); ++i) {
                ans += W[i] * x[i];
            }
            return ans;
        };

        for (int epoch = 0; epoch < EPOCH; ++epoch) {
            vector<double> y_predict;
            for (int i = 0; i < n; ++i) {
                y_predict.push_back(self_predict(X_train[i]));
            }
            vector<double> gradient_w;
            for (int j = 0; j < m; ++j) {
                double tmp = 0;
                for (int i = 0; i < n; ++i) tmp += (y_train[i] - y_predict[i]) * X_train[i][j];
                gradient_w.push_back(tmp / (double)n);
            }
            for (int i = 0; i < m; ++i) {
                W[i] += m_lr * gradient_w[i];
            }
        }
        return {W[0] / 100.0, W[1] / 100.0};
    }

   private:
    static const int EPOCH = 1000;
    static constexpr double m_lr = 0.01;

    double m_hvW1 = 0;
    double m_hvW2 = 0;
    double m_evW1 = 0;
    double m_evW2 = 0;
};