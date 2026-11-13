#pragma once
#include <vector>
#include <cmath>
#include "ios_touch_state.h"
namespace IOSTouch {
struct Stroke {float x1,y1,x2,y2;};
inline std::vector<Stroke> Glyph(int id,bool menu){
 std::vector<Stroke>s;auto line=[&](float a,float b,float c,float d){s.push_back({a,b,c,d});};
 auto arc=[&](float cx,float cy,float r,float start,float end){for(int i=0;i<24;i++){float a=start+(end-start)*i/24,b=start+(end-start)*(i+1)/24;line(cx+r*std::cos(a),cy+r*std::sin(a),cx+r*std::cos(b),cy+r*std::sin(b));}};
 if(menu){if(id==0){line(-.55f,0,-.15f,.4f);line(-.15f,.4f,.6f,-.45f);}else if(id==1){line(-.5f,-.5f,.5f,.5f);line(-.5f,.5f,.5f,-.5f);}else{float d=id==11?-1.f:1.f;line(-.5f,-.2f*d,0,.4f*d);line(0,.4f*d,.5f,-.2f*d);}return s;}
 switch(id){
 case 0:arc(0,0,.45f,0,6.2831853f);line(-.8f,0,-.25f,0);line(.25f,0,.8f,0);line(0,-.8f,0,-.25f);line(0,.25f,0,.8f);break;
 case 1:line(0,.6f,0,-.6f);line(0,-.6f,-.45f,-.15f);line(0,-.6f,.45f,-.15f);line(-.55f,.65f,.55f,.65f);break;
 case 2:line(-.45f,.65f,-.65f,.1f);line(-.65f,.1f,-.25f,.15f);line(-.25f,.15f,-.25f,-.55f);arc(-.1f,-.55f,.15f,3.14159f,6.28318f);line(.05f,-.55f,.05f,-.1f);line(.05f,-.1f,.55f,0);line(.55f,0,.4f,.65f);line(.4f,.65f,-.45f,.65f);break;
 case 3:arc(-.15f,-.5f,.18f,0,6.28318f);line(-.15f,-.3f,-.4f,.1f);line(-.4f,.1f,.25f,.25f);line(.25f,.25f,.45f,.65f);line(-.4f,.1f,-.5f,.65f);line(-.15f,-.15f,.5f,-.05f);break;
 case 4:line(-.5f,-.25f,.5f,-.25f);line(.5f,-.25f,.5f,.55f);line(.5f,.55f,-.5f,.55f);line(-.5f,.55f,-.5f,-.25f);arc(0,-.25f,.25f,3.14159f,6.28318f);line(-.5f,.1f,.5f,.1f);break;
 case 6:for(float y:{-.4f,0.f,.4f})line(-.6f,y,.6f,y);break;
 case 8:arc(0,0,.55f,-2.8f,2.1f);line(-.5f,-.2f,-.6f,-.65f);line(-.5f,-.2f,-.05f,-.25f);break;
 case 9:case 10:{float d=id==9?-1.f:1.f;line(-.3f*d,-.5f,.3f*d,0);line(.3f*d,0,-.3f*d,.5f);break;}
 }return s;
}
}

namespace IOSTouch {
// Pure geometry shared with the Vulkan overlay, independently testable.
template<class Line> inline void OverlayLines(const State& touch,float width,float height,Line line) {
  auto ring = [&](float x,float y,float radius,float light) {
   for(int i=0;i<48;i++) {float a=i*6.2831853f/48,b=(i+1)*6.2831853f/48;
    line(x+radius*std::cos(a),y+radius*std::sin(a),x+radius*std::cos(b),y+radius*std::sin(b),light);}
  };
  for(const auto& b:IOSTouch::Layout(touch.menu)) {
   float x=b.x*width,y=b.y*height,r=b.r*height,s=r*.66f;
   float light=touch.buttons[b.id]?1.f:.82f;
   ring(x,y,r,light);
   for(const auto& g:IOSTouch::Glyph(b.id,touch.menu))
    line(x+g.x1*s,y+g.y1*s,x+g.x2*s,y+g.y2*s,light);
  }
  float x=.19f*width,y=.72f*height;
  for(const auto& finger:touch.fingers) if(finger.second.owner==-1){x=finger.second.x*width;y=finger.second.y*height;}
  ring(x,y,.14f*height,.55f);
  ring(x+touch.lx*.14f*height,y+touch.ly*.14f*height,.035f*height,.8f);
}
}
