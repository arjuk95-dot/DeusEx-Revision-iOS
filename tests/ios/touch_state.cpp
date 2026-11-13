#include "../../DXWidgets/src/window/sdl3/ios_touch_state.h"
#include <cassert>
int main(){
 IOSTouch::State s;s.Down(1,.70f,.43f,2);assert(s.buttons[0]);
 s.Down(2,.85f,.8f,2);s.Move(2,.90f,.81f,2,1000,500);assert(s.buttons[0]&&s.dx>49&&s.dy>4);
 s.Up(2);assert(s.buttons[0]);s.Up(1);assert(!s.buttons[0]);
 s.Down(3,.2f,.7f,2);s.Move(3,.3f,.6f,2,1000,500);assert(s.lx>0&&s.ly<0);s.Up(3);assert(s.lx==0&&s.ly==0);
 s.Down(4,.7f,.43f,2);s.Down(5,.7f,.43f,2);s.Up(4);assert(s.buttons[0]);
 s.Down(99,.94f,.25f,2);s.Up(99);assert(s.pressed[3]&&!s.buttons[3]);
 s.SetMenu(true);assert(!s.buttons[0]&&s.fingers.empty());s.Down(6,.7f,.44f,2);assert(s.buttons[0]);s.Reset();assert(!s.buttons[0]);
}
