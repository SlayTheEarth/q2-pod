/* Offline control of stock's saved DAC charging choice, and its status-bar indication.
 * Keep this separate from the policy in usb_charge.c: presentation never writes cable flags.
 */
#include "navigation.h"

static int charge_click(void *view, void *event) {
    (void)event;
    g_usbdac_chargeflag = g_usbdac_chargeflag != 1;
    write_int_config(g_usbdac_chargeflag, "PLAYSET", "USBDAC_CHARGE");
    /* Restore a request that the DAC page may have disabled, without releasing a limit hold.
     * The existing guard still permits Storage charging with the DAC preference Off. */
    ringnav_usb_charge(!st.charge_held);
    void *label = widget_lookup(view, "_usb_dac_charge", 1);
    if (label) list_toggle(label, "USB DAC charging", g_usbdac_chargeflag == 1);
    return 0;
}
void usb_charge_row(void *view) {
    if (!view) return;
    void *label = list_row(view, "usb_chargeswitch", charge_click, view);
    if (label) {
        widget_set_name(label, "_usb_dac_charge");
        list_toggle(label, "USB DAC charging", g_usbdac_chargeflag == 1);
    }
}
/* The two final stock battery-image assignments, after all stock cable/page choices.
 * get_battery_capacity's cached status matched all 393 samples of a Q2 charging test:
 * 1 Charging, 0 Discharging. Full (2) is not active charging. GPIO errors never grant green.
 * Other battery painters consume this image, including full-screen/dark status bars.
 */
int usb_charge_image(void *image, const char *stock_choice) {
    (void)stock_choice;
    int permitted = g_usbdac_chargeflag == 1 || (g_usbmode == 0 && g_usbdet_value == 1);
    int active = I(g_power_chargestate, 0) == 1 && g_usbdet_value == 1 && permitted &&
                 !st.charge_held && toolsGpioGetValue("PE22") == 0;
    const char *choice = active                        ? "bar_charge"
                         : I(g_power_capacity, 0) < 15 ? "bar_lowcharge"
                                                       : "bar_battery";
    return image_base_set_image(image, choice);
}
