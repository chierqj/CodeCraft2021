#pragma once

#include "virtual_machine.h"
using namespace std;

enum REQ_TYPE { ADD, DEL };

class Request {
   public:
    Request(enum REQ_TYPE type, const shared_ptr<VirtualMachine> &vm) : m_type(type), m_bind_vm(vm) {}

   public:
    inline const REQ_TYPE &GetType() const { return m_type; }
    inline shared_ptr<VirtualMachine> GetBindVm() { return m_bind_vm; }

   private:
    REQ_TYPE m_type;                                 // 请求类型
    shared_ptr<VirtualMachine> m_bind_vm = nullptr;  // 请求绑定的虚拟机实例
};