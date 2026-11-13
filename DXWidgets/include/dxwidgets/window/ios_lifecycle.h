#pragma once
#include <atomic>
namespace IOSLifecycle
{
inline std::atomic<bool> Suspended{false};
inline bool IsSuspended() { return Suspended.load(std::memory_order_acquire); }
inline void Suspend() { Suspended.store(true, std::memory_order_release); }
inline void Resume() { Suspended.store(false, std::memory_order_release); }
}
