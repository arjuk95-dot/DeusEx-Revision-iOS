# Revision touch design evidence (proposal, no layout implemented)

Read-only audit of the owner's installed Revision User.ini and scripts on Legion.
These are behavior findings, not redistributed game scripts or UI assets.

## World controls

- WASD/arrows: move/strafe. Mouse X/Y: aMouseX/aMouseY, speed 6; always mouselook.
- Left click / Enter: ParseLeftClick | Fire. Fires a weapon or activates the held
  item (including lockpick/multitool); context includes drone detonation.
- Right click: ParseRightClick. Use/pick up/talk/open; without a target, put away
  held item. **Not alternate fire.**
- Space jump; X toggle crouch; Shift walk; CapsLock toggles walk.
- Q/E lean. **R looks up, not reload.** Semicolon reloads.
- Quote switches ammo; left/right bracket toggle scope/laser.
- I/F1 inventory; G/F2 goals; B skills.
- Belt: 1..9,0; minus/equal additional slots; wheel previous/next item.
- Tab/middle click drop; Backspace put in hand; Escape main menu.
- F3..F12 augmentation slots 0..9, L augmentation 9.

Do not synthesize familiar generic shooter bindings. Use explicit semantic
commands or a generated private binding profile without replacing the owner's
keyboard mappings.

## UI context is separate

Inventory requires absolute pointer/tap and dragging, not a relative look area.
Enter uses the selected item; Backspace drops it; Delete clears belt assignment;
number keys assign the selected object to a belt slot.

Conversations: no-choice lines can advance with Enter/Space/Escape or mouse
release (subject to script guards); choices need navigation/tap and confirm.
Menu Enter confirms, Escape goes back with the menu's own conditional save rules.
World fire/use must not leak through modal UI. All held actions must release on
finger cancellation, focus loss, backgrounding, menu transitions and rotation.

## Mockup to review before implementation

Landscape phone, safe-area insets. Left movement thumbstick and broad right look
area. Separate prominent Use/Talk and Fire/Item buttons; smaller jump, crouch,
reload; belt radial (12 slots: 1–9, 0, minus, equal); unobtrusive inventory/goals/pause. Expandable secondary panel
for lean, walk, ammo, scope, laser, drop and augmentations. Preserve readable
world/HUD rather than covering the screen with every keyboard command.

Layout remains pending user review of an image mockup. SDL3 currently routes
mouse/keyboard/gamepad events, not finger events; this proposal is not working
multitouch. Host proof covers menu flow and weapon equip, not mobile controls.

Owner feedback: simplify to direct move/look/use/fire/jump/crouch, with number
keys in a radial. Revised mockup required before layout implementation.
