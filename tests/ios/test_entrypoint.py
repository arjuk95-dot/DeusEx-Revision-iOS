import pathlib
import unittest

class EntryPointTests(unittest.TestCase):
    def test_sdl_main_macro_is_isolated_after_engine_code(self):
        source = (pathlib.Path(__file__).resolve().parents[2] / "ports/ios/MainIOS.mm").read_text()
        include = source.index("#include <SDL3/SDL_main.h>")
        self.assertLess(source.index('#include "GameApp.h"'), include)
        self.assertLess(source.index("app.main("), include)
        self.assertGreater(source.index("int main(int argc"), include)
        self.assertIn("return RunIOSGame();", source[include:])
