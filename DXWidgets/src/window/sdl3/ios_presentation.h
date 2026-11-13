#pragma once
#include <algorithm>
#include <cmath>
namespace IOSPresentation {
struct Box {float x,y,w,h;};
inline Box Fit(int sw,int sh,int dw,int dh) {
 float scale=std::min(dw/(float)std::max(sw,1),dh/(float)std::max(sh,1));
 float w=std::max(1.f,std::round(sw*scale)),h=std::max(1.f,std::round(sh*scale));
 return {std::floor((dw-w)/2),std::floor((dh-h)/2),w,h};
}
inline float LookScale(float gain,int logicalWidth) { return gain*956.f/std::max(logicalWidth,1); }
}
