from flask import Flask, request, redirect
import time, netifaces

app = Flask(__name__)

# Constants for configuration
station_address = 'station0' # TODO: Update with Jon's code

# Will keep track of whether we're in the middle of an active victory sequence.
active_victory = False


#############################################################################
#
# Helper functions
#
#############################################################################

##
# Start the victory sequence and run the sound instructions. Send the lighting a signal when to stop
def victory_sequence():
    global active_victory
    print('Station Victory achieved!')
    active_victory = True

    ##
    # TODO: Implement running the sound file for the victory sequence
    ##

    # After victory has finished, clean up
    active_victory = False
    print('Station Victory finished')


##
# This function triggers the sounds that will play from this station
#
# @param <analog_values> - List of the analog input values from this station
def play_sound(analog_values):
    print('* Playing sounds for ' + station_address + ': ' + str(analog_values) + '*')

    ##
    # TODO: Implement playing sound associated with analog inputs
    ##


##
# This function triggers the sounds that will play from this station
#
# @param <analog_values> - List of the analog input values from this station
def play_clue():
    print('* Playing sound clue for station: ' + station_address + '*')

    ##
    # TODO: Implement playing sound associated with analog inputs
    ##


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
# Restful API call example: http://192.168.8.111:8000/sound?analog_values=1,.5,.3,.4&victory=True&clue=True
@app.route('/sound')
def sound():
    global active_victory

    # Get the list of analog input parameters
    input = request.args.get('analog_values')
    input = input.replace('[', '').replace(']', '')
    analog_values = [float(f) for f in input.split(',')]
    assert isinstance(analog_values, list)
    assert len(analog_values) == 4

    # If we should start a victory sequence
    start_victory = request.args.get('victory') == 'True'

    # If we need to play a clue
    trigger_clue = request.args.get('clue') == 'True'

    # If we're already in a victory sequence, do nothing. Let the thread playing the victory sequence finish and proceed
    # Otherwise see if we meet the victory condition or play the sound associated with the inputs
    if not active_victory:
        if start_victory:
            # Begin Active victory sequence for sound
            victory_sequence()
        else:
            # Play a clue if needed
            if trigger_clue:
                play_clue()

            # Play the sound
            play_sound(analog_values)

    # Debugging line
    output = "Input accepted for {} : {} \n -victory : {}\n -clue : {}".format(
        station_address, analog_values, start_victory, trigger_clue)

    return output

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int("9000"))


