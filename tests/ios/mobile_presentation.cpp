#include "../../DXEngine/Utils/MobilePresentation.h"
#include "../../DXWidgets/src/window/sdl3/ios_presentation.h"
#include "../../DXWidgets/src/window/sdl3/ios_touch_state.h"
#include <cassert>
#include <limits>
int main(){
 using namespace MobilePresentation;
 for(int logical:{32,64,128}) for(float scale:{.5f,1.f,2.f}) {
   // Both stock and 8x replacement mips must cover one logical UV period.
   for(int mip:{logical,logical*8,logical*4}) { (void)mip;
     assert(std::abs(CoronaExtent(logical,scale)/(logical*scale)-1.f)<1e-6f);
   }
 }
 for(auto size:{std::pair<int,int>{956,440},{1434,660},{2868,1320},{640,480},{400,300}}){
   float s=UIScale(size.first,size.second);
   assert(size.first/s>=639.99f && size.second/s>=479.99f);
   float pointer=123.4f; assert(std::abs((pointer*s)/s-pointer)<.001f);
 }
 auto b=IOSPresentation::Fit(956,440,2868,1320);
 assert(b.x==0&&b.y==0&&b.w==2868&&b.h==1320);
 b=IOSPresentation::Fit(640,480,1920,1080);
 assert(b.x==240&&b.y==0&&b.w==1440&&b.h==1080);
 float countsA=.1f*956*IOSPresentation::LookScale(3,956);
 float countsB=.1f*1280*IOSPresentation::LookScale(3,1280);
 assert(std::abs(countsA-countsB)<.001f);
 IOSTouch::State touch;touch.Down(1,.7f,.43f,2);touch.Down(2,.85f,.8f,2);
 touch.Move(2,.9f,.81f,2,956,440);assert(touch.buttons[0]&&touch.dx>0);
 assert(Number("nan",.33f,.25f,1)==.33f);assert(Number(".5",.33f,.25f,1)==.5f);
 assert(Number("garbage",.33f,.25f,1)==.33f);assert(Number("0",.33f,.25f,1)==.25f);
}
