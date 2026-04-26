/*
 * Routines for configuring and using an ADS1256 8-channel analog/digital
 * converter, connected to the Raspberry Pi via an SPI bus.
 *
 * Author: Jon McClintock
 * $Id: $
 */

#ifndef _ADS1256_H_
#define _ADS1256_H_
 
#include <stdint.h>
#include <unistd.h>

/*
 * ADS1256 configuration values.
 */

// The number of channels supported in the different modes.
#define ADS1256_SINGLE_CHANNEL_COUNT		(8)
#define ADS1256_DIFFERENTIAL_CHANNEL_COUNT	(4)

// Input modes.
typedef enum
{
  ADS1256_INPUT_SINGLE_ENDED = 0,
  ADS1256_INPUT_DIFFERENTIAL = 1,
} ADS1256_INPUT_MODE_E;

// Channel gain settings.
typedef enum
{
  ADS1256_GAIN_1  = (0), /* Gain  1x */
  ADS1256_GAIN_2  = (1), /* Gain  2x */
  ADS1256_GAIN_4  = (2), /* Gain  4x */
  ADS1256_GAIN_8  = (3), /* Gain  8x */
  ADS1256_GAIN_16 = (4), /* Gain 16x */
  ADS1256_GAIN_32 = (5), /* Gain 32x */
  ADS1256_GAIN_64 = (6), /* Gain 64x */
  ADS1256_GAIN_MAX
} ADS1256_GAIN_E;

// Sampling rate settings.
typedef enum {
	ADS1256_30000SPS = 0,
	ADS1256_15000SPS,
	ADS1256_7500SPS,
	ADS1256_3750SPS,
	ADS1256_2000SPS,
	ADS1256_1000SPS,
	ADS1256_500SPS,
	ADS1256_100SPS,
	ADS1256_60SPS,
	ADS1256_50SPS,
	ADS1256_30SPS,
	ADS1256_25SPS,
	ADS1256_15SPS,
	ADS1256_10SPS,
	ADS1256_5SPS,
	ADS1256_2d5SPS,
	ADS1256_DATA_RATE_MAX
} ADS1256_DATA_RATE_E;

/*
 * Initialize the SPI bus and set it up to communicate with the ADS1256.
 *
 * Returns: 0 on success, nonzero on error.
 */
uint8_t ads1256_initialize(void);

/*
 * Set the configuration parameters of the ADC: gain and data rate.
 */
void ads1256_configure_adc(ADS1256_GAIN_E gain, ADS1256_DATA_RATE_E data_rate);

/*
 * Read the ID of the chip on the SPI bus.
 */
uint8_t ads1256_read_chip_id(void);

/*
 * Perform a single conversion on the specified channel and return the 
 * result.
 */
double ads1256_read_channel(uint8_t channel, ADS1256_INPUT_MODE_E input_mode);

/*
 * Perform conversions on the specified channel range (inclusive) and store the 
 * results in the array provided (which must have enough memory allocated).
 *
 * Returns 0 on success, non-zero on error.
 */
uint8_t ads1256_read_channels(uint8_t start_channel, 
                              uint8_t end_channel,
			      ADS1256_INPUT_MODE_E input_mode, 
			      double results[]);

/*
 * Shut down the SPI bus.
 */
void ads1256_shutdown(void);

#endif /* _ADS1256_H_ */
