from flask import Flask, request, redirect
import time, netifaces

app = Flask(__name__)

# Constants for configuration
master_controller_address = '192.168.8.111'
network_adapter = 'wlan0'  # Probably need to eventually use eth0

# Will keep track of whether we're in the middle of an active victory sequence.
active_victory = False
victory_start_time = 0
victory_length = 10  # Number of seconds for the victory sequence - set this to the sound file's length


#############################################################################
#
# Helper functions
#
#############################################################################

##
# Gets the IP(v4) address of the station controller
def get_host_address():
    addrs = netifaces.ifaddresses(network_adapter)
    print('Getting host address for ' + network_adapter +' from ' + str(addrs) )
    return addrs[netifaces.AF_INET][0]['addr']

##
# Determine if the victory sequence has finished. Currently decides based on whether victory_length seconds have passed
#
# @return Boolean - True if the victory sequence needs to end. False if it should continue
def is_victory_finished():
    if (time.time() > victory_start_time + victory_length):
        return True
    if (victory_start_time < 1):
        print('Error: checking for victory end without a victory start time')
    return False

##
# Start the victory sequence and run the sound instructions. Send the lighting a signal when to stop
def victory_sequence():
    global active_victory, victory_start_time
    print('Station Victory achieved!')
    active_victory = True
    victory_start_time = time.time()

    ##
    # TODO: Implement running the sound file for the victory sequence
    ##

    # This block is for debugging purposes, counting out seconds of a victory sequence on the console
    time_table = []
    while (is_victory_finished() == False):
        if (int(time.time()) not in time_table):
            print('Victory: ' + str(int(time.time())))
            time_table.append(int(time.time()))

    # After victory has finished, clean up
    active_victory = False
    victory_start_time = 0
    print('Station Victory finished')

##
# This function triggers the sounds that will play from this station
#
# @param <analog_values> - List of the analog input values from this station
def play_sound(analog_values):
    print('* Playing sounds for: ' + str(analog_values) + '*')

    ##
    # TODO: Implement playing sound associated with analog inputs
    ##

    return True

############################################################################
#
# Main dispatcher routine
#
############################################################################

##
# This function will process the analog values from this station to calculate sound effects
#
# @param <analog_values> - a list of the analog values to process
# @param <victory> - a boolean of whether a victory sequence needs to be started
# @return Response/output to render to a browser
#
# Restful API call example: http://192.168.8.111:8000/sound?analog_values=1,.5,.3,.4&victory=True
@app.route('/sound')
def sound():
    global active_victory, victory_start_time, victory_dictionary

    # Get the list of analog input parameters
    input = request.args.get('analog_values');
    input = input.replace('[', '').replace(']', '')
    analog_values = [float(f) for f in input.split(',')]
    assert isinstance(analog_values, list)
    assert len(analog_values) == 4

    # If we need to end an active victory sequence display based on the ending of the sound sequence
    victory = request.args.get('victory') == 'True'

    this_station = get_host_address()

    # If we're already in a victory sequence, do nothing. Let the thread playing the victory sequence finish and proceed
    # Otherwise see if we meet the victory condition or play the sound associated with the inputs
    if (active_victory == False):
        if victory:
            # Begin Active victory sequence for lighting
            victory_sequence()

            # Call the master controller's API to end the victory sequence
            return redirect('http://{}:8000/light?station={}&analog_values={}&victory={}'.format(master_controller_address, this_station, analog_values, active_victory))
        else:
            # Play the sound
            play_sound(analog_values)

    # Debugging line
    output = "Input accepted for {} : {} : victory({})".format(this_station, analog_values, victory)
    return output

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int("9000"))

