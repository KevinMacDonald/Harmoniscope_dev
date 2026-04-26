from flask import Flask, request
# from ../hw/dmx_control import DMXControl

# dmx_control = DMXControl()

app = Flask(__name__)

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
max_pixel = 48 # TODO: Set to the correct actual value

#############################################################################
#
# Helper functions
#
#############################################################################

##
# This function will ensure that the pixel value is within bounds
def IsPixelValueSane(pixel_value):
    p = int(pixel_value)
    if (p >= 0 and p <= max_pixel):
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
# Restful API call example: http://192.168.8.116:5000/light/12?r=1&g=2&b=3&w=4
def light(pixel):
    # Only accept inputs for valid 'pixel' values
    if (IsPixelValueSane(pixel) == False):
        output = "Your input pixel value is insane"
        return output

    # Get the list of analog input parameters
    rgbw = []
    rgbw.insert(r_idx,SanitizeChannelValue(request.args.get('r',0,type=int)))
    rgbw.insert(g_idx,SanitizeChannelValue(request.args.get('g',0,type=int)))
    rgbw.insert(b_idx,SanitizeChannelValue(request.args.get('b',0,type=int)))
    rgbw.insert(w_idx,SanitizeChannelValue(request.args.get('w',0,type=int)))

    # Store our station & analog value list in the pixel_dictionary for future use
    pixel_cache[pixel] = rgbw

    ##
    # TODO: Invoke the light controller functions on the computed channels here
    ##

    cv=pixel_cache[pixel]
    output = "Input for pixel {} : r={},b={},g={},w={}".format(pixel, cv[r_idx],cv[g_idx],cv[b_idx],cv[w_idx])
    return output

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=int("8000"))

