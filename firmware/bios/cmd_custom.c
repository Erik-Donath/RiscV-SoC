#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <generated/csr.h>
#include <irq.h>

#include "../command.h"
#include "../helpers.h"

#ifdef CSR_LEDS_BASE

static volatile int blink_active = 0;

define_command(blink, blink_handler, "Blink LED 0", SYSTEM_CMDS);

static void blink_handler(int nb_params, char **params) {
    unsigned int count = 10;  // Default: 10 blinks
    unsigned int delay = 5000000;  // Default delay (busy loop iterations)
    unsigned int i, j;
    
    if (nb_params >= 1) {
        count = strtoul(params[0], NULL, 0);
    }
    
    if (nb_params >= 2) {
        delay = strtoul(params[1], NULL, 0);
    }
    
    printf("Blinking LED 0 %d times...\n", count);
    printf("Press Ctrl+C to stop\n");
    
    blink_active = 1;
    
    for (i = 0; i < count && blink_active; i++) {
        // LED 0 on (bit 0 = 1)
        leds_out_write(0x01);
        
        // Busy wait delay
        for (j = 0; j < delay; j++) {
            asm volatile("nop");
        }
        
        // LED 0 off
        leds_out_write(0x00);
        
        // Busy wait delay
        for (j = 0; j < delay; j++) {
            asm volatile("nop");
        }
        
        // Print progress every 10 blinks
        if ((i + 1) % 10 == 0) {
            printf("  %d blinks completed\n", i + 1);
        }
    }
    
    // Ensure LED is off at the end
    leds_out_write(0x00);
    
    if (blink_active) {
        printf("Blink complete!\n");
    } else {
        printf("Blink stopped by user\n");
    }
    
    blink_active = 0;
}

#endif /* CSR_LEDS_BASE */

