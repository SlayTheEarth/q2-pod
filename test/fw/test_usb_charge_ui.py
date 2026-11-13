"""Display policy; the Power row's full UI test is in test_nav_painters.py."""
import ctypes as C

import pytest

from test_usb_charge import Charging


@pytest.mark.parametrize('pref,mode,cable,status,gpio,held,level,image', [
    (1, 1, 1, 1, 0, 0, 80, b'bar_charge'),
    (0, 1, 1, 1, 0, 0, 80, b'bar_battery'),
    (1, 1, 1, 0, 0, 0, 80, b'bar_battery'),
    (1, 1, 1, 2, 0, 0, 100, b'bar_battery'),
    (1, 1, 1, -1, 0, 0, 80, b'bar_battery'),
    (1, 1, 1, 1, 1, 0, 80, b'bar_battery'),
    (1, 1, 1, 1, -1, 0, 80, b'bar_battery'),
    (1, 1, 1, 1, 0, 1, 80, b'bar_battery'),
    (1, 1, 0, 1, 0, 0, 80, b'bar_battery'),
    (0, 0, 1, 1, 0, 0, 80, b'bar_charge'),
    (0, 1, 1, 0, 1, 0, 10, b'bar_lowcharge'),
])
def test_final_image_selection_cannot_be_overridden_by_stocks_choice(fw, st, pref, mode, cable, status, gpio, held, level, image):
    q = Charging(fw, pref=pref, mode=mode, cable=cable)
    q.config()
    q.gpio = gpio
    fw.var('g_usbdet_value', C.c_ubyte).value = cable
    fw.var('fw_ctx_g_power_chargestate', C.c_int).value = status
    fw.var('fw_ctx_g_power_capacity', C.c_int).value = level
    st('charge_held').value = held
    shown = []
    fw.mock('image_base_set_image', lambda widget, name, *_: shown.append((widget, C.string_at(name))) or 17)
    render = fw.fn('usb_charge_image', C.c_int, C.c_void_p, C.c_char_p)
    before = list(q.writes)
    for stock in (b'bar_charge', b'bar_battery', b'bar_lowcharge'):
        assert render(1234, stock) == 17 and shown[-1] == (1234, image)
    assert q.writes == before and q.flag.value == pref and q.usbmode.value == mode
    assert fw.var('fw_ctx_g_power_chargestate', C.c_int).value == status
