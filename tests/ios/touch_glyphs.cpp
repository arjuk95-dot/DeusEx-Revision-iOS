#include "DXWidgets/src/window/sdl3/ios_touch_state.h"
#include "DXWidgets/src/window/sdl3/ios_touch_glyphs.h"
#include <cassert>
int main(){for(bool menu:{false,true})for(auto b:IOSTouch::Layout(menu)){auto glyph=IOSTouch::Glyph(b.id,menu);assert(!glyph.empty());for(auto s:glyph)for(float x:{s.x1,s.y1,s.x2,s.y2})assert(std::isfinite(x)&&std::abs(x)<=1.f);}for(bool menu:{false,true}) {
 IOSTouch::State state; state.SetMenu(menu);int count=0;
 IOSTouch::OverlayLines(state,956.f,440.f,[&](float x1,float y1,float x2,float y2,float light){
  for(float x:{x1,y1,x2,y2,light})assert(std::isfinite(x));
  assert(x1>=0 && x1<=956 && x2>=0 && x2<=956);
  assert(y1>=0 && y1<=440 && y2>=0 && y2<=440);count++;
 });assert(count>100);
}return 0;}
