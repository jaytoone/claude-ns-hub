---
name: Keyboard Control App PoC Findings
description: BT HID keyboard → Android app PoC hardware test results (2026-05-07)
type: project
originSessionId: b1da7c17-e239-486f-a3f9-c3a9221ecf5a
---
PoC hardware validation completed 2026-05-07 with Huawei WAS-LX2J + GK104 BT1 keyboard.

**Why:** Verifying PoC acceptance criteria T1-T2 before full MVP build.

**How to apply:** Use these findings to inform MVP build decisions — numpad keycodes are confirmed K1/K2/K3 candidates.

## Devices tested
- OPPO CPH1909 (Android 8.1, SDK 27): BT paired but HidService.mInputDevices empty — HID profile never connected. Unusable for PoC.
- Huawei WAS-LX2J (Android 7.0, SDK 24, EMUI 5.1): HID connected, keyboard registered as event5 (GK104 BT1). Working.

## Keyboard
- Model: GK104 BT1 (MAC E4:07:67:0E:0B:17)
- Registered as: mouse1 + event5 (SOURCE_MOUSE | SOURCE_KEYBOARD)
- Has relative axes (REL=1c3) → classified as mouse+keyboard combo

## Key findings
- Regular alpha keys (A/S/D/F): arrive at OS level (getevent confirmed) but EMUI FullInputEventModel aborts them before app dispatchKeyEvent
- Numpad keys: bypass IME, arrive cleanly at app dispatchKeyEvent

## Confirmed K1/K2/K3 candidates
- K1 = KEYCODE_NUMPAD_1 (keyCode=145, scanCode=79, device=6)
- K2 = KEYCODE_NUMPAD_2 (keyCode=146, scanCode=80, device=6)
- K3 = KEYCODE_NUMPAD_3 (keyCode=147, scanCode=81, device=6)
- All unique, no IME interference, no text input conflict

## Remote test setup
- WSL → SSH → LT-1 (100.125.152.31) → ADB → Huawei (serial: 9TSDU18329001416)
- ADB platform-tools: C:\Users\be2ja\AppData\Local\platform-tools\adb.exe
- KeyInspector APK installed: com.poc.keyinspector
- ADB simulation: `adb shell input keyevent 145/146/147`
- ADB vs real keyboard distinguishable: device=-1/scanCode=0 vs device=6/scanCode=79+

## Dev plan note
- minSdk lowered to 24 for PoC (Huawei is SDK 24); restore to 26 for MVP
- KeyInspector project: /home/desk-1/Project/VIDraft/KeyInspector/
