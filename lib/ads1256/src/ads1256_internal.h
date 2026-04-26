/*
 * Internal definitions and function declarations.
 *
 * Author: Jon McClintock
 * $Id: $
 */

#ifndef _ADS1256_INTERNAL_
#define _ADS1256_INTERNAL_

/*
 * Enumerations and config values.
 */

// Sampling data rate configuration values. Indices match with the
// ADS1256_DATA_RATE_E enum defined in the header file.
static const uint8_t s_tabDataRate[ADS1256_DATA_RATE_MAX] = {
        0xF0,           /*reset the default values  */
        0xE0,
        0xD0,
        0xC0,
        0xB0,
        0xA1,
        0x92,
        0x82,
        0x72,
        0x63,
        0x53,
        0x43,
        0x33,
        0x20,
        0x13,
        0x03
};

// Register addresses, followed by their default values..
enum {
  REG_STATUS = 0,  // x1H
  REG_MUX    = 1,  // 01H
  REG_ADCON  = 2,  // 20H
  REG_DRATE  = 3,  // F0H
  REG_IO     = 4,  // E0H
  REG_OFC0   = 5,  // xxH
  REG_OFC1   = 6,  // xxH
  REG_OFC2   = 7,  // xxH
  REG_FSC0   = 8,  // xxH
  REG_FSC1   = 9,  // xxH
  REG_FSC2   = 10, // xxH
};

// Chip command numbers.
enum {
  CMD_WAKEUP  = 0x00, // Completes SYNC and exits Standby Mode
  CMD_RDATA   = 0x01, // Read Data
  CMD_RDATAC  = 0x03, // Read Data Continuously
  CMD_SDATAC  = 0x0F, // Stop Read Data Continuously
  CMD_RREG    = 0x10, // Read from REG rrr              0001 rrrr (1xh)
  CMD_WREG    = 0x50, // Write to REG rrr               0101 rrrr (5xh)
  CMD_SELFCAL = 0xF0, // Offset and Gain Self-Calibration
  CMD_SELFOCAL= 0xF1, // Offset Self-Calibration
  CMD_SELFGCAL= 0xF2, // Gain Self-Calibration
  CMD_SYSOCAL = 0xF3, // System Offset Calibration
  CMD_SYSGCAL = 0xF4, // System Gain Calibration
  CMD_SYNC    = 0xFC, // Synchronize the A/D Conversion
  CMD_STANDBY = 0xFD, // Begin Standby Mode
  CMD_RESET   = 0xFE, // Reset to Power-Up Values
};


/*
 * Definitions and macros for modifying I/O pins.
 */

// Control line pin mappings.
#define  DRDY   RPI_GPIO_P1_11  //P0
#define  RST    RPI_GPIO_P1_12  //P1
#define  SPICS  RPI_GPIO_P1_15  //P3

// Macros for setting the chip-select line.
#define CS_1() (bcm2835_gpio_write(SPICS, HIGH))
#define CS_0() (bcm2835_gpio_write(SPICS, LOW))

// Macro to test if the data ready line is low.
#define DRDY_IS_LOW()   ((bcm2835_gpio_lev(DRDY) == 0))

// Macros for setting the RST line.
#define RST_1()         (bcm2835_gpio_write(RST,HIGH))
#define RST_0()         (bcm2835_gpio_write(RST,LOW))

/*
 * Function declarations.
 */

static void ads1256_delay_us(uint64_t micros);

static void ads1256_delay_data(void);
static int8_t ads1256_wait_drdy(void); 

static void ads1256_send_byte(uint8_t byte);
static uint8_t ads1256_receive_byte(void);

static void ads1256_write_register(uint8_t register_id, uint8_t value);
static uint8_t ads1256_read_register(uint8_t register_id);
static void ads1256_write_command(uint8_t command);

static void ads1256_set_channel(uint8_t channel, 
				ADS1256_INPUT_MODE_E input_mode);
static double ads1256_read_conversion_result(void);
static double ads1256_result_to_voltage(int32_t result);

#endif /* _ADS1256_INTERNAL */
