from flask import Flask, request
from hw.dmx_control import DMXControl
from hw.web_color_selector import ColorSelector

# Channel indices for pixels
min_idx = 0
r_idx = 0
g_idx = 1
b_idx = 2
w_idx = 3
max_idx = 4 # unreachable maximum for loop ranges

# Main app
app = Flask(__name__)

# Python dictionary (aka Hashtable) of [pixel] : [rgbw values]
pixel_cache = {}

# Maximum value of a DMX channel value
max_channel = 255

# Maximum number of individual light sources in the structure
max_pixel = 28

#############################################################################
#
# Helper functions
#
#############################################################################

##
# This function will ensure that the pixel value is within bounds
def IsPixelValueSane(pixel_value):
    p = int(pixel_value)
    if (p >= 1 and p <= max_pixel):
        return True
    else:
        return False 

##
# This function will ensure that the value for a channel is within bounds
def SanitizeChannelValue(channel_value):
    if (channel_value > max_channel):
        return (max_channel)
    elif (channel_value < 0):
        return 0
    else:
        return channel_value

############################################################################
#
# Main dispatcher routine
#
############################################################################

# Module handles light requests only
@app.route('/light/<pixel>')

##
# This function will receive the instructins to set a particular pixel
# to a set of given R,G,B,W values and translate that into DMX instructions 
#
# @param <pixel> - the address of the pixel to modify
# @param <analogValues> - a list of R,G,B,W values e.g. 1,2,3,4
#
# Restful API call example: http://192.168.8.116:8000/light/12?r=1&g=2&b=3&w=4
def light(pixel):
    # Only accept inputs for valid 'pixel' values
    if (IsPixelValueSane(pixel) == False):
        output = "Your input pixel value is insane"
        return output

    # DMXControl class has the limitation that it must be created on the
    # same thread that uses it, so for now creating one for each request

    dmx_control = DMXControl()

    color_selectors = [
        ColorSelector(DMXControl.CHANNEL_RED, dmx_control),
        ColorSelector(DMXControl.CHANNEL_GREEN, dmx_control),
        ColorSelector(DMXControl.CHANNEL_BLUE, dmx_control),
        ColorSelector(DMXControl.CHANNEL_WHITE, dmx_control),
    ]

    # Get the list of analog input parameters
    rgbw = [0,0,0,0]
    rgbw[r_idx] = SanitizeChannelValue(request.args.get('r',0,type=int))
    rgbw[g_idx] = SanitizeChannelValue(request.args.get('g',0,type=int))
    rgbw[b_idx] = SanitizeChannelValue(request.args.get('b',0,type=int))
    rgbw[w_idx] = SanitizeChannelValue(request.args.get('w',0,type=int))

    # Store our station & analog value list in the pixel_dictionary for future use
    pixel_cache[pixel] = rgbw

    ##
    # Invoke the light controller functions on the computed channels here
    ##

    for i in range(min_idx,max_idx):
        color_selectors[i].update_channel_brightness(rgbw[i])

    cv=pixel_cache[pixel]
    output = "Input for pixel {} : r={},g={},b={},w={}".format(pixel, cv[r_idx],cv[g_idx],cv[b_idx],cv[w_idx])
    return output

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=int("8000"))

