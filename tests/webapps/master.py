from flask import Flask, request, redirect
import time

app = Flask(__name__)

# Python dictionary (aka Hashtable) of [station address] : [analog value list]
station_dictionary = {}

# Python dictionary of the victory condition values for each station input
# TODO: Need to update this with all station addresses and their respective victory values
victory_dictionary = {'192.168.8.116':[1,1,1,1]}

# Will keep track of whether we're in the middle of an active victory sequence.
active_victory = False

# Python dictionary (aka Hashtable) of [pixel] : [rgbw values]
pixel_cache = {}

# Channel indices for pixels
r_idx = 0
g_idx = 1
b_idx = 2
w_idx = 3
max_idx = 3

# Maximum value of a DMX channel value
max_channel = 255

# Maximum number of pixels in the structure
max_pixel = 48  # TODO: Set to the correct actual value

# Maximum value that the analog knobs can return
max_analog_value = 1  # TODO: Set to the correct actual value


#############################################################################
#
# Helper functions
#
#############################################################################

##
# This function will ensure that the pixel value is within bounds
def is_pixel_value_sane(pixel_value):
    p = int(pixel_value)
    if (p >= 0 and p <= max_pixel):
        return True
    else:
        return False


##
# This function will ensure that the value for a channel is within bounds
def sanitize_channel_value(channel_value):
    if (channel_value > max_channel):
        return max_channel
    elif (channel_value < 0):
        return 0
    else:
        return channel_value


##
# Takes a list of analog values and convertis it to a list of channels for the
# proportional values relating 0-[max_analog_value] to 0-[max_channel]
#
# @param <analog_values> - a list of long analog values ranging from 0 to [max_analog_value]
# @return A list of integer channels ranging from 0 to [max_channel]
def convert_to_channels(analog_values):
    channels = []
    factor = max_channel / max_analog_value
    for value in analog_values:
        channels.append(int(float(value) * factor))
        if (len(channels) >= 4):
            break
    return channels


##
# This function will determine which pixels need to be updated to the channels derrived
# from the analog values provided
#
# @param <analog_values> - a list of long analog values ranging from 0 to [max_analog_value]
# @return A list of integer pixel addresses to modify. Each range from 0 to [max_pixel]
def get_pixels_to_update(analog_values):
    ##
    # TODO: Implement logic for choosing the pixel/s to update based on the analog values
    ##
    return [1]

##
# This function will determine if the victory condition has been met
#
# Check values of all stations stored in the station_dictionary
#
# @return Boolean - True if victory condition has been met. False otherwise
def check_for_victory():
    for station in victory_dictionary.keys():
        if (victory_dictionary[station] != station_dictionary[station]):
            return False
    return True

##
# Start the victory sequence and run the lighting instructions in a loop until we get the signal to end
def start_victory():
    global active_victory
    print('Master Victory achieved!')
    active_victory = True
    ##
    # TODO: Implement logic of displaying victory sequence
    ##

##
# End the victory sequence
def finish_victory():
    global active_victory, victory_start_time
    print('Finishing Victory...')
    active_victory = False
    victory_start_time = 0

    ##
    # TODO: Figure out how to kill the victory sequence initiated from another request call
    ##

    # Reset the lights to current knob analog values
    print('pixel_cache size: ' + str(len(pixel_cache)))
    for pixel in pixel_cache.keys():
        print(set_pixel(pixel, pixel_cache[pixel]))

##
# This function will receive the instructins to set a particular pixel
# to a set of given R,G,B,W values and translate that into DMX instructions
#
# @param <pixel> - the address of the pixel to modify
# @param <analog_values> - an integer list of 4 R,G,B,W channels ranging 0 to [max_channels]
# @return Debugging text
def set_pixel(pixel, channels):
    # Only accept inputs for valid 'pixel' values
    if (is_pixel_value_sane(pixel) == False):
        output = "Your input pixel value is insane"
        return output
    if (len(channels) != 4):
        return 'Invald number of channel values: {}. Expected: 4'.format(len(channels))

    # Get the list of analog input parameters
    rgbw = []
    rgbw.insert(r_idx, sanitize_channel_value(channels[0]))
    rgbw.insert(g_idx, sanitize_channel_value(channels[1]))
    rgbw.insert(b_idx, sanitize_channel_value(channels[2]))
    rgbw.insert(w_idx, sanitize_channel_value(channels[3]))

    # Store our station & analog value list in the pixel_dictionary for future use
    pixel_cache[pixel] = rgbw

    ##
    # TODO: Invoke the light controller functions on the computed channels here
    ##

    cv = pixel_cache[pixel]
    output = "Input for pixel {} : r={},b={},g={},w={}".format(pixel, cv[r_idx], cv[g_idx], cv[b_idx], cv[w_idx])
    return output


############################################################################
#
# Main dispatcher routine
#
############################################################################

##
# This function will process the analog values from each station to calculate lighting effects,
# then it will send the analog values back to each station for computation of sound
#
# @param <station> - the address of the station for which data is being processed
# @param <analog_values> - a list of the analog values to process
# @param <stop_victory> - a boolean of whether an active victory sequence needs to be ended and reset
# @return Response/output to render to a browser
#
# Restful API call example: http://192.168.8.111:8000/light?station=192.168.8.116&analog_values=1,2,3,4&stop_victory=False
@app.route('/light', methods=['GET','POST'])
def light():
    global station_dictionary, pixel_cache, active_victory, victory_start_time, victory_dictionary

    # Get the list of analog input parameters
    input = request.args.get('analog_values');
    input = input.replace('[', '').replace(']', '')
    analog_values = [float(f) for f in input.split(',')]
    assert isinstance(analog_values, list)
    assert len(analog_values) == 4

    # If we need to end an active victory sequence display based on the ending of the sound sequence
    stop_victory = request.args.get('stop_victory') == 'True'

    # Store our station & analog value list in the analog_dictionary for global access
    station = request.args.get('station')
    station_dictionary[station] = analog_values

    # If we're already in a victory sequence, check if we need to end it otherwise don't affect the active sequence
    if (active_victory & stop_victory):
        print('Terminate signal found: Stopping victory sequence...')
        finish_victory()

        output = "Input accepted for {} : {} : victory({})".format(station, station_dictionary[station], active_victory)
        return output
    else:
        if check_for_victory():
            # Begin Active victory sequence for lighting
            start_victory()
        else:
            # Update the lights controller functions accordingly here
            pixels = get_pixels_to_update(analog_values)
            channels = convert_to_channels(analog_values)
            assert isinstance(pixels, list)
            for pixel in pixels:
                print(set_pixel(pixel, channels))

        # Call the station controller's API for sound processing here
        return redirect('http://{}:9000/sound?analog_values={}&victory={}'.format(station, analog_values, active_victory))

    # Debugging code - COMMENT OUT IN WORKING VERSION
    output = "Input accepted for {} : {} : victory({})".format(station, station_dictionary[station], active_victory)
    return output

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int("8000"))

