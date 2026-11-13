#include "DXWidgets/src/window/sdl3/ios_touch_state.h"
#include "DXWidgets/src/window/sdl3/ios_touch_glyphs.h"
#include <cassert>
int main(){for(bool menu:{false,true})for(auto b:IOSTouch::Layout(menu)){auto glyph=IOSTouch::Glyph(b.id,menu);assert(!glyph.empty());for(auto s:glyph)for(float x:{s.x1,s.y1,s.x2,s.y2})assert(std::isfinite(x)&&std::abs(x)<=1.f);}return 0;}
