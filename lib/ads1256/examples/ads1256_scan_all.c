/*
 * Test program to read in values from the analog lines on an ADS1256 connected
 * to the SPI bus on a Raspberry Pi.
 *
 * Author: Jon McClintock
 * $Id: $
 */
 
#include "ads1256.h"

#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <math.h>
#include <errno.h>

int
main()
{
    uint8_t id;
    double adc[8];
    uint8_t i;
    int32_t iTemp;

    if (ads1256_initialize()) {
        return -1;
    }

    id = ads1256_read_chip_id();
    if (id != 3) {
	printf("Error, ASD1256 Chip ID = 0x%d\r\n", (int)id);
    } else {
	printf("Ok, ASD1256 Chip ID = 0x%d\r\n", (int)id);
    }

    ads1256_configure_adc(ADS1256_GAIN_1, ADS1256_100SPS);

    while(1) {
	if (ads1256_read_channels(0, ADS1256_SINGLE_CHANNEL_COUNT - 1,
	                          ADS1256_INPUT_SINGLE_ENDED, adc)) {
	    printf("Error reading input.\n");
	    break;	    
        }

	for (i = 0; i < ADS1256_SINGLE_CHANNEL_COUNT; i++) {
	    printf("%d=%2.4f\n", (int)i, adc[i]);
	}

	printf("\33[%dA", (int)ADS1256_SINGLE_CHANNEL_COUNT);  
	usleep(10000);	
    }	

    ads1256_shutdown();

    return 0;
}
