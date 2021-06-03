#pragma once

#include <cstdio>
#include <iostream>

template <class... T>
void m_getline(const char *fromat, T... t) {
    static std::string line;
    std::getline(cin, line);
    sscanf(line.c_str(), fromat, t...);
}