#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <map>
#include <vector>
namespace IOSTouch {
struct Button { float x,y,r; int id; const char* label; };
inline std::vector<Button> Layout(bool menu) {
 if(menu) return {{.70f,.44f,.075f,0,"ACCEPT"},{.88f,.30f,.06f,1,"BACK"},{.94f,.70f,.045f,12,"DOWN"},{.94f,.53f,.045f,11,"UP"}};
 return {{.70f,.43f,.075f,0,"FIRE"},{.84f,.25f,.06f,2,"USE"},{.94f,.44f,.06f,1,"JUMP"},{.94f,.25f,.055f,3,"CROUCH"},{.83f,.44f,.055f,8,"RELOAD"},{.53f,.11f,.045f,4,"INV"},{.62f,.11f,.045f,6,"MENU"},{.78f,.11f,.04f,9,"PREV"},{.90f,.11f,.04f,10,"NEXT"}};
}
class State {
public:
 std::array<bool,15> buttons{},pressed{};
 float lx=0,ly=0,dx=0,dy=0; bool menu=false;
 struct Contact { int owner; float x,y; };
 std::map<int64_t,Contact> fingers;
 void Reset() { fingers.clear();buttons.fill(false);pressed.fill(false);lx=ly=dx=dy=0; }
 void SetMenu(bool next) {if(menu!=next){Reset();menu=next;}}
 void Down(int64_t id,float x,float y,float aspect) {
  if(fingers.count(id))return;int owner=-2;
  for(const auto& b:Layout(menu)){float xx=(x-b.x)*aspect,yy=y-b.y;if(xx*xx+yy*yy<=b.r*b.r){owner=b.id;break;}}
  if(owner==-2 && x<.42f && y>.35f){bool occupied=false;for(auto& f:fingers)if(f.second.owner==-1)occupied=true;if(!occupied)owner=-1;}
  fingers.emplace(id,Contact{owner,x,y});if(owner>=0)pressed[owner]=true;Recompute();
 }
 void Move(int64_t id,float x,float y,float aspect,float width,float height){
  auto it=fingers.find(id);if(it==fingers.end())return;auto& f=it->second;
  if(f.owner==-1){lx=std::clamp((x-f.x)*aspect/.14f,-1.0f,1.0f);ly=std::clamp((y-f.y)/.14f,-1.0f,1.0f);float length=std::sqrt(lx*lx+ly*ly);if(length>1){lx/=length;ly/=length;}}
  else if(f.owner==-2){dx+=(x-f.x)*width;dy+=(y-f.y)*height;f.x=x;f.y=y;}
 }
 void Up(int64_t id){auto it=fingers.find(id);if(it==fingers.end())return;if(it->second.owner==-1)lx=ly=0;fingers.erase(it);Recompute();}
private:
 void Recompute(){buttons.fill(false);for(auto& f:fingers)if(f.second.owner>=0)buttons[f.second.owner]=true;}
};
}
