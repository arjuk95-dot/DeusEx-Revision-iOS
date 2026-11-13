#pragma once
#include <algorithm>
#include <cmath>
#include <cstdlib>
namespace MobilePresentation {
inline float Number(const char* text, float fallback, float lo, float hi) {
 if (!text || !*text) return fallback;
 char* end=nullptr; float v=std::strtof(text,&end);
 return end && !*end && std::isfinite(v) ? std::clamp(v,lo,hi) : fallback;
}
// Fit a complete 640x480 UI even below 480 render pixels. Both painting
// and pointer conversion use this same scale; do not truncate to integers.
inline float UIScale(int width,int height) {
 return std::max(0.01f,std::min(width/640.f,height/480.f));
}
inline float CoronaExtent(float logicalSize,float textureScale) {
 return logicalSize*textureScale;
}
}
