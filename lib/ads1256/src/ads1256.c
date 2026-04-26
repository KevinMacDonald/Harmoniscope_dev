/*
 * Routines for configuring and using an ADS1256 8-channel analog/digital
 * converter, connected to the Raspberry Pi via an SPI bus.
 *
 * Author: Jon McClintock
 * $Id: $
 */
 
#include "ads1256.h"
#include "ads1256_internal.h"

#include <bcm2835.h>  
#include <stdint.h>
#include <unistd.h>

// Flag to indicate that the chip has been initialized and the bus is open.
static uint8_t _ads1256_initialized = 0;

/*
 * Public methods.
 */

/*
 * Initialize the SPI bus and set it up to communicate with the ADS1256.
 *
 * Returns: 0 on success, nonzero on error.
 */
uint8_t
ads1256_initialize(void)
{
    // We're already initialized, do nothing.
    if (_ads1256_initialized == 1) {
	return 0;
    }

    if (!bcm2835_init()) {
        return -1;
    }

    if (!bcm2835_spi_begin()) {
        perror("Error: Couldn't open the SPI bus. (Are you root?)");
        return -1;
    }

    // Configure the SPI bus.
    bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_LSBFIRST);
    bcm2835_spi_setDataMode(BCM2835_SPI_MODE1);
    bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_1024);

    // Set up the pins used for SPI signaling.
    bcm2835_gpio_fsel(SPICS, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_write(SPICS, HIGH);
    bcm2835_gpio_fsel(DRDY, BCM2835_GPIO_FSEL_INPT);
    bcm2835_gpio_set_pud(DRDY, BCM2835_GPIO_PUD_UP);

    _ads1256_initialized = 1;

    return 0;
}

/*
 * Set the configuration parameters of the ADC: gain and data rate.
 */
void 
ads1256_configure_adc(ADS1256_GAIN_E gain, ADS1256_DATA_RATE_E data_rate)
{
    uint8_t buf[4];  // Storage ads1256 register configuration parameters

    ads1256_wait_drdy();

    /*
     * Status register definitions:
     *
     * Bits 7-4 ID3, ID2, ID1, ID0  Factory Programmed Identification Bits (R/O)
     *
     * Bit 3 ORDER: Data Output Bit Order
     *   0 = Most Significant Bit First (default)
     *   1 = Least Significant Bit First
     *
     *   Input data  is always shifted in most significant byte and bit first. 
     *   Output data is always shifted out most significant byte first. 
     *   The ORDER bit only controls the bit order of the output data within 
     *   the byte.
     *
     * Bit 2 ACAL : Auto-Calibration
     *   0 = Auto-Calibration Disabled (default)
     *   1 = Auto-Calibration Enabled
     *
     *   When Auto-Calibration is enabled, self-calibration begins at the 
     *   completion of the WREG command that changes the PGA (bits 0-2 of
     *   ADCON register), DR (bits 7-0 in the DRATE register) or BUFEN (bit 
     *   1 in the STATUS register) values.
     *
     * Bit 1 BUFEN: Analog Input Buffer Enable
     *   0 = Buffer Disabled (default)
     *   1 = Buffer Enabled
     *
     * Bit 0 DRDY :  Data Ready (Read Only)
     *   This bit duplicates the state of the DRDY pin.
     *
     * Here we select: LSB first, auto-calibration enabled, no buffer.
     */
    buf[0] = (0 << 3) | (1 << 2) | (0 << 1);

    /* 
     * Input channel selection. Select AIN0 for the positive input, and
     * AINCOM (ground) for the negative input.
     */
    buf[1] = 0x08;	

    /*
     * ADCON: A/D Control Register (Address 02h)
     *
     * Bit 7 Reserved, always 0 (Read Only)
     *
     * Bits 6-5 CLK1, CLK0 : D0/CLKOUT Clock Out Rate Setting
     *  00 = Clock Out OFF
     *  01 = Clock Out Frequency = fCLKIN (default)
     *  10 = Clock Out Frequency = fCLKIN/2
     *  11 = Clock Out Frequency = fCLKIN/4
     *
     *  When not using CLKOUT, it is recommended that it be turned off. 
     *  These bits can only be reset using the RESET pin.
     *
     * Bits 4-3 SDCS1, SCDS0: Sensor Detect Current Sources
     *  00 = Sensor Detect OFF (default)
     *  01 = Sensor Detect Current = 0.5 ¦Ì A
     *  10 = Sensor Detect Current = 2 ¦Ì A
     *  11 = Sensor Detect Current = 10¦Ì A
     *
     *  The Sensor Detect Current Sources can be activated to verify 
     *  the integrity of an external sensor supplying a signal to the
     *  ADS1255/6. A shorted sensor produces a very small signal while 
     *  an open-circuit sensor produces a very large signal.
     *
     * Bits 2-0 PGA2, PGA1, PGA0: Programmable Gain Amplifier Setting
     *  000 = 1 (default)
     *  001 = 2
     *  010 = 4
     *  011 = 8
     *  100 = 16
     *  101 = 32
     *  110 = 64
     *  111 = 64
     *
     * Here we set clock out off, sensor detect off, and the requested gain.
     */
    buf[2] = (0 << 5) | (0 << 3) | (gain << 0);

    /* Set the selected data rate. */
    buf[3] = s_tabDataRate[data_rate];

    /* Select the chip. */
    CS_0();

    /* Write command register, send the first register address */
    ads1256_send_byte(CMD_WREG | 0);

    /* Send the number of registers to write (minus one). */
    ads1256_send_byte(0x03);

    ads1256_send_byte(buf[0]);	/* Set the status register */
    ads1256_send_byte(buf[1]);	/* Set the input channel parameters */
    ads1256_send_byte(buf[2]);	/* Set the ADCON control register,gain */
    ads1256_send_byte(buf[3]);	/* Set the output rate */

    /* Deselect the chip. */
    CS_1();

    ads1256_delay_us(50);                       // TODO: Magic delay.
}

/*
 * Read the ID of the chip on the SPI bus.
 */
uint8_t 
ads1256_read_chip_id(void)
{
    uint8_t id;

    ads1256_wait_drdy();
    id = ads1256_read_register(REG_STATUS);
    return (id >> 4);
}

/*
 * Perform a single conversion on the specified channel and return the
 * result.
 *
 * Returns 0 on error.
 */
double 
ads1256_read_channel(uint8_t channel, ADS1256_INPUT_MODE_E input_mode)
{
    uint8_t channel_count;

    if (input_mode == ADS1256_INPUT_SINGLE_ENDED) {
	channel_count = ADS1256_SINGLE_CHANNEL_COUNT;
    } else {
	channel_count = ADS1256_DIFFERENTIAL_CHANNEL_COUNT;
    }

    if (channel >= channel_count) {
	return 0;
    }

    ads1256_set_channel(channel, input_mode);
    ads1256_delay_us(5);                        // TODO: Magic delay.

    ads1256_write_command(CMD_STANDBY);
    ads1256_delay_us(5);                        // TODO: Magic delay.

    ads1256_write_command(CMD_WAKEUP);
    ads1256_delay_us(25);                       // TODO: Magic delay.

    if (ads1256_wait_drdy() != 0) {
	return 0;
    }

    return ads1256_read_conversion_result();
}

/*
 * Perform conversions on the specified channel range (inclusive) and store the
 * results in the array provided (which must have enough memory allocated).
 */
uint8_t ads1256_read_channels(uint8_t start_channel, 
                              uint8_t end_channel,
                              ADS1256_INPUT_MODE_E input_mode, 
                              double results[])
{
    uint8_t i;
    uint8_t channel_count;

    if (input_mode == ADS1256_INPUT_SINGLE_ENDED) {
	channel_count = ADS1256_SINGLE_CHANNEL_COUNT;
    } else {
	channel_count = ADS1256_DIFFERENTIAL_CHANNEL_COUNT;
    }

    // Validate the input arguments.
    if ((start_channel >= channel_count) ||
        (end_channel   >= channel_count) ||
        (start_channel > end_channel) ||
        (results == 0)) {
	return 0;
    }

    // Wait for it to be ready to start a conversion.
    if (ads1256_wait_drdy() != 0) {
	return -1;
    }

    // Start the conversion on the first channel.
    ads1256_set_channel(start_channel, input_mode);

    // The first result will be for whatever channel the MUX was set to
    // previously, so ignore it.
    ads1256_write_command(CMD_SYNC);
    ads1256_delay_us(5);                        // TODO: Magic delay.

    ads1256_write_command(CMD_WAKEUP);
    ads1256_delay_us(25);                       // TODO: Magic delay.

    if (ads1256_wait_drdy() != 0) {
	return -1;
    }

    // Now loop through the rest of the channels and read in the conversion
    // results.
    for (i = start_channel; i <= end_channel; i++) {
	ads1256_set_channel(i, input_mode);
	ads1256_delay_us(5);                    // TODO: Magic delay.

	ads1256_write_command(CMD_SYNC);
	ads1256_delay_us(5);                    // TODO: Magic delay.

	ads1256_write_command(CMD_WAKEUP);
	ads1256_delay_us(25);                   // TODO: Magic delay.

	if (ads1256_wait_drdy() != 0) {
	    return -1;
	}

	results[i - start_channel] = ads1256_read_conversion_result();
    }

    return 0;
}

/*
 * Shut down the SPI bus.
 */
void
ads1256_shutdown(void)
{
    // We're not initialized, do nothing.
    if (_ads1256_initialized == 0) {
	return;
    }

    bcm2835_spi_end();
    bcm2835_close();

    _ads1256_initialized = 0;
}


/*
 * Internal methods.
 */

/*
 * Delay for 'micros' microseconds.
 */
static void 
ads1256_delay_us(uint64_t micros)
{
    bcm2835_delayMicroseconds(micros);
}

/*
 * Write a byte on the SPI bus.
 */
static void 
ads1256_send_byte(uint8_t byte)
{
    ads1256_delay_us(2);                // TODO: Fix magic value.
    bcm2835_spi_transfer(byte);
}

/*
 * Delay for the clock interval between data in (DIN) and data out (DOUT).
 */
static void 
ads1256_delay_data(void)
{
    /*
     * Delay from last SCLK edge for DIN to first SCLK rising edge 
     * for DOUT: RDATA, RDATAC,RREG Commands
     *
     * Minimum is 50 CLK cycles, where each cycle is 0.13uS.
     *
     *  50 * 0.13uS = 6.5uS
     *
     * We delay 10 uS to be conservative.
     */
    ads1256_delay_us(10);
}

/*
 * Read in a byte from the SPI bus and return it.
 */
static uint8_t 
ads1256_receive_byte(void)
{
    return bcm2835_spi_transfer(0xff);
}

/*
 * Write the byte value to the corresponding register.
 */
static void 
ads1256_write_register(uint8_t register_id, uint8_t value)
{
    /* Select the chip. */
    CS_0();

    /* Send the command to write to a register, along with the desired
     * register ID. */ 
    ads1256_send_byte(CMD_WREG | register_id);
 
    /* The number of registers to write, minus 1. */
    ads1256_send_byte(0x00);

    /* Send desired value. */
    ads1256_send_byte(value);

    /* Deselect the chip. */
    CS_1();
}

/*
 * Read the corresponding register from the chip and return its value.
 */
static uint8_t 
ads1256_read_register(uint8_t register_id)
{
    uint8_t read;

    /* Select the chip. */
    CS_0();

    /* Send the command to read the given register. */
    ads1256_send_byte(CMD_RREG | register_id);

    /* The number of registers to read, minus 1. */
    ads1256_send_byte(0x00);

    /* Wait for the data to be ready. */
    ads1256_delay_data();

    /* Read the register values */
    read = ads1256_receive_byte();

    /* Deselect the chip. */
    CS_1();

    return read;
}

/*
 * Send a single byte command to the chip.
 */
static void 
ads1256_write_command(uint8_t command)
{
    /* Select the chip. */
    CS_0();

    /* Send the command. */
    ads1256_send_byte(command);

    /* Deselect the chip. */
    CS_1();
}

/*
 * Set the current channel number to convert.
 */
static void 
ads1256_set_channel(uint8_t channel, ADS1256_INPUT_MODE_E input_mode)
{
    /*
     * Bits 7-4 PSEL3, PSEL2, PSEL1, PSEL0: Positive Input Channel (AINP) Select
     * Bits 3-0 NSEL3, NSEL2, NSEL1, NSEL0: Negative Input Channel (AINN) Select
     *
     * For each:
     *   0000 = AIN0 (default)
     *   0001 = AIN1
     *   0010 = AIN2 (ADS1256 only)
     *   0011 = AIN3 (ADS1256 only)
     *   0100 = AIN4 (ADS1256 only)
     *   0101 = AIN5 (ADS1256 only)
     *   0110 = AIN6 (ADS1256 only)
     *   0111 = AIN7 (ADS1256 only)
     *   1xxx = AINCOM (when PSEL3 = 1, PSEL2, PSEL1, PSEL0 are "don't care")
     */
    uint8_t nsel, psel;

    /* If the channel is out of range, then abort. */ 
    if (((input_mode == ADS1256_INPUT_SINGLE_ENDED) &&
         (channel >= ADS1256_SINGLE_CHANNEL_COUNT)) || 
        ((input_mode == ADS1256_INPUT_DIFFERENTIAL) &&
         (channel >= ADS1256_DIFFERENTIAL_CHANNEL_COUNT))) {
	return;
    }

    if (input_mode == ADS1256_INPUT_SINGLE_ENDED) {
        /* For single-ended input, positive is the requested channel, and 
         *negative is ACOM (ground). */
	psel = channel;
	nsel = (1 << 3);
    } else { 
        /* For differential input, positive and negative are interleaved
         * as pairs: 0/1, 2/3, 4/5, 6/7 */
	psel = channel << 1;
        nsel = psel + 1;
    }

    /* Write the MUX register. */
    ads1256_write_register(REG_MUX, (psel << 4) | nsel);	
}

/*
 * Loop until the chip has data ready for us to read.
 *
 * Returns -1 on timeout, 0 otherwise.
 */
static int8_t
ads1256_wait_drdy(void)
{
    uint32_t i;

    // TODO: Ideally this would be a sleep() that would be woken up by an
    //       interrupt. Not sure if the bcm2835 library supports that.
    // TODO: 400000 seems like an arbitrary number. Figure out what this value
    //       should be based on.
    for (i = 0; i < 400000; i++) {
	if (DRDY_IS_LOW()) {
	    break;
	}
    }

    if (i >= 400000) {
	perror("ads1256_wait_drdy() Time Out ...\r\n");		
	return -1;
    }

    return 0;
}

/*
 * Read the converted ADC value in and return it.
 */
static double 
ads1256_read_conversion_result(void)
{
    uint32_t read_value = 0;
    static uint8_t buf[3];

    /* Select the chip. */
    CS_0();

    /* Send the command to read the ADC data. */
    ads1256_send_byte(CMD_RDATA);

    /* Wait for the chip to be ready. */
    ads1256_delay_data();

    /* Read the 24 bits of sample results as 3 bytes. */
    buf[0] = ads1256_receive_byte();
    buf[1] = ads1256_receive_byte();
    buf[2] = ads1256_receive_byte();

    /* Deselect the chip. */
    CS_1();

    /* The bytes are in least-significant order. Reassemble them into a word. */
    read_value = ((uint32_t)buf[0] << 16) & 0x00FF0000;
    read_value |= ((uint32_t)buf[1] << 8);
    read_value |= buf[2];

    /* Extend a signed number. */
    if (read_value & 0x800000) {
	read_value |= 0xFF000000;
    }

    return ads1256_result_to_voltage((int32_t)read_value);
}

/*
 * Translate a conversion result into a voltage.
 */
static double
ads1256_result_to_voltage(int32_t result)
{
    /* The result is a signed integer in the range of -1<<23 to +1<<23,
     * representing -5VDC to +5VDC. */
    return (5.0 * result) / (1<<23);
}

