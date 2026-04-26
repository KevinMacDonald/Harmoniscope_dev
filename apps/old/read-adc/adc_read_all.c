/* 
  Initiates and reads a single sample from each channel of the ADS1115 
  (without error handling).
*/

#include <stdio.h>
#include <fcntl.h>     // open
#include <inttypes.h>  // uint8_t, etc
#include <linux/i2c-dev.h> // I2C bus definitions

#define I2C_DEVICE  "/dev/i2c-1"	// The device of the I2C bus
#define ADS_ADDRESS 0x48		// Address of the device on the I2C bus

void
usage(char* argv_zero)
{
  printf("Usage: %s [-r]\n", argv_zero);
  printf("Read the analog values at all four input lines, and print them out.\n");
  printf("\n");
  printf("  -r  Print raw values instead of converting them to voltages\n");
  printf("\n");
}

int
open_i2c_bus(const char* dev, int address)
{
  int fd;
  fd = open(dev, O_RDWR);
  if (-1 == fd) {
    perror("Couldn't open the I2C bus device");
    return -1;
  }

  // Specify the address of the I2C Slave to communicate with
  if (ioctl(fd, I2C_SLAVE, address)) {
    perror("Couldn't set the I2C slave address");
    close(fd);
    return -1;
  }

  return fd;
}

int16_t
read_adc_channel(int fd, uint8_t channel) 
{
  ssize_t count;
  uint8_t write_buf[3];
  uint8_t read_buf[2];
  
  // These three bytes are written to the ADS1115 to set the config 
  // register and start a conversion.
  write_buf[0] = 1;			// Pointer register => config register
  write_buf[1] = 0xC1;   	        // Config 8 MSBs to 11000001
  write_buf[2] = 0xC3;  		// Config 8 LSBs to 11000011 (475s/s)
 
  // Set the channel. 
  write_buf[1] |= (channel & 0x03) << 4;

  // Initialize the buffer used to read data from the ADS1115 to 0
  read_buf[0]= 0;
  read_buf[1]= 0;
	  
  // Write the config to the ADS1115. This begins a single conversion.
  count = write(fd, write_buf, 3);	
  if (count != 3) {
    perror("Couldn't write the command to the ADC");
    return INT16_MIN;
  }

  // Wait for the conversion to complete, indicated by bit 15 changing from 0->1
  while ((read_buf[0] & 0x80) == 0) {
    count = read(fd, read_buf, 2);
    if (count != 2) {
      perror("Couldn't read the status register from the ADC");
      return INT16_MIN;
    }
  }

  // Set pointer register to 0 to read from the conversion register. 
  write_buf[0] = 0;
  count = write(fd, write_buf, 1);
  if (count != 1) {
    perror("Couldn't set the pointer register on the ADC");
    return INT16_MIN;
  }

  // Read the contents of the conversion register.
  count = read(fd, read_buf, 2);
  if (count != 2) {
    perror("Couldn't read the conversion register from the ADC");
    return INT16_MIN;
  }

  return (read_buf[0] << 8 | read_buf[1]);
}

int 
main(int argc, char** argv)
{
  int i;
  int i2c_fd;
  int16_t val;
  int print_raw_values = 0; // Default to output voltage

  if (argc > 2) {
    usage(argv[0]);
    return -1;
  }
 
  if (argc == 2) {
    if (strncmp(argv[1], "-r") == 0) {
      print_raw_values = 1;
    } else {
      usage(argv[0]);
      return -1;
    }
  }
 
  i2c_fd = open_i2c_bus(I2C_DEVICE, ADS_ADDRESS);
  if (-1 == i2c_fd) {
    return -1;
  }

  for (i = 0; i < 4; i++) {
    val = read_adc_channel(i2c_fd, i);
    if (INT16_MIN == val) {
      fprintf(stderr, "Error reading from channel %i, aborting.\n", i);
      break;
    }
    
    if (print_raw_values == 1) {
      if (i > 0) {
	printf(",");
      }
      printf("%d", val);
    } else {
      printf("Channel %d Voltage Reading %f (V) \n", 
             i, (float)val*6.144/32767.0);
    }
  }
		
  if (print_raw_values == 1) {
    printf("\n");
  }

  if (close(i2c_fd)) {
    perror("Error closing I2C device");
    return -1;
  }
  
  return 0;
}

