#include <Python.h>
#include <ads1256.h>

static PyObject* ads1256_py_initialize(   PyObject *self, PyObject *args);
static PyObject* ads1256_py_configure_adc(PyObject *self, PyObject *args);
static PyObject* ads1256_py_read_chip_id( PyObject *self, PyObject *args);
static PyObject* ads1256_py_read_channel( PyObject *self, PyObject *args);
static PyObject* ads1256_py_read_channels(PyObject *self, PyObject *args);
static PyObject* ads1256_py_shutdown(     PyObject *self, PyObject *args);

static PyObject *ads1256_error;

static PyMethodDef ads1256_methods[] = {
    {"initialize",    ads1256_py_initialize, METH_NOARGS,
     PyDoc_STR("Initialize the SPI interface to the ADS1256.")},
    {"configure",     ads1256_py_configure_adc, METH_VARARGS,
     PyDoc_STR("Set the configuration parameters of the ADS1256.")},
    {"get_chip_id",   ads1256_py_read_chip_id, METH_NOARGS,
     PyDoc_STR("Read the ID of the ADS1256 chip.")},
    {"read_channel",  ads1256_py_read_channel, METH_VARARGS,
     PyDoc_STR("Read in a single channel's value.")},
    {"read_channels", ads1256_py_read_channels, METH_VARARGS,
     PyDoc_STR("Read in a range of channel values.")},
    {"shutdown",    ads1256_py_shutdown, METH_NOARGS,
     PyDoc_STR("Shut down the SPI interface to the ADS1256.")},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef ads1256_module_def = {
    PyModuleDef_HEAD_INIT,
    "ads1256",                                     /* m_name */
    PyDoc_STR("Module for interacting with an ADS1256 ADC"),  /* m_doc */
    -1,                                            /* m_size */
    ads1256_methods,                               /* m_methods */
    NULL,                                          /* m_reload */
    NULL,                                          /* m_traverse */
    NULL,                                          /* m_clear */
    NULL,                                          /* m_free */
};

PyMODINIT_FUNC
PyInit_ads1256(void)
{
    PyObject *m;

    m = PyModule_Create(&ads1256_module_def);
    if (m == NULL) {
        return NULL;
    }

    ads1256_error = PyErr_NewException("ads1256.error", NULL, NULL);
    Py_INCREF(ads1256_error);
    PyModule_AddObject(m, "error", ads1256_error);

    PyModule_AddIntConstant(m, "ADS1256_SINGLE_CHANNEL_COUNT",
                               ADS1256_SINGLE_CHANNEL_COUNT);
    PyModule_AddIntConstant(m, "ADS1256_DIFFERENTIAL_CHANNEL_COUNT",
                               ADS1256_DIFFERENTIAL_CHANNEL_COUNT);

    PyModule_AddIntConstant(m, "ADS1256_INPUT_SINGLE_ENDED", 
                               ADS1256_INPUT_SINGLE_ENDED);
    PyModule_AddIntConstant(m, "ADS1256_INPUT_DIFFERENTIAL", 
                               ADS1256_INPUT_DIFFERENTIAL);

    PyModule_AddIntConstant(m, "ADS1256_GAIN_1",   ADS1256_GAIN_1);
    PyModule_AddIntConstant(m, "ADS1256_GAIN_2",   ADS1256_GAIN_2);
    PyModule_AddIntConstant(m, "ADS1256_GAIN_4",   ADS1256_GAIN_4);
    PyModule_AddIntConstant(m, "ADS1256_GAIN_8",   ADS1256_GAIN_8);
    PyModule_AddIntConstant(m, "ADS1256_GAIN_16",  ADS1256_GAIN_16);
    PyModule_AddIntConstant(m, "ADS1256_GAIN_32",  ADS1256_GAIN_32);
    PyModule_AddIntConstant(m, "ADS1256_GAIN_64",  ADS1256_GAIN_64);
    PyModule_AddIntConstant(m, "ADS1256_GAIN_MAX", ADS1256_GAIN_MAX);

    PyModule_AddIntConstant(m, "ADS1256_30000SPS", ADS1256_30000SPS);
    PyModule_AddIntConstant(m, "ADS1256_15000SPS", ADS1256_15000SPS);
    PyModule_AddIntConstant(m, "ADS1256_7500SPS",  ADS1256_7500SPS);
    PyModule_AddIntConstant(m, "ADS1256_3750SPS",  ADS1256_3750SPS);
    PyModule_AddIntConstant(m, "ADS1256_2000SPS",  ADS1256_2000SPS);
    PyModule_AddIntConstant(m, "ADS1256_1000SPS",  ADS1256_1000SPS);
    PyModule_AddIntConstant(m, "ADS1256_500SPS",   ADS1256_500SPS);
    PyModule_AddIntConstant(m, "ADS1256_100SPS",   ADS1256_100SPS);
    PyModule_AddIntConstant(m, "ADS1256_60SPS",    ADS1256_60SPS);
    PyModule_AddIntConstant(m, "ADS1256_50SPS",    ADS1256_50SPS);
    PyModule_AddIntConstant(m, "ADS1256_30SPS",    ADS1256_30SPS);
    PyModule_AddIntConstant(m, "ADS1256_25SPS",    ADS1256_25SPS);
    PyModule_AddIntConstant(m, "ADS1256_15SPS",    ADS1256_15SPS);
    PyModule_AddIntConstant(m, "ADS1256_10SPS",    ADS1256_10SPS);
    PyModule_AddIntConstant(m, "ADS1256_5SPS",     ADS1256_5SPS);
    PyModule_AddIntConstant(m, "ADS1256_2d5SPS",   ADS1256_2d5SPS);
    PyModule_AddIntConstant(m, "ADS1256_DATA_RATE_MAX", 
                                                   ADS1256_DATA_RATE_MAX);

    return m;
}

static PyObject*
ads1256_py_initialize(PyObject *self, PyObject *args)
{
    ads1256_initialize();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
ads1256_py_configure_adc(PyObject *self, PyObject *args)
{
    ADS1256_GAIN_E gain;
    ADS1256_DATA_RATE_E data_rate;

    if (!PyArg_ParseTuple(args, "ii", &gain, &data_rate)) {
        PyErr_SetString(ads1256_error, "Invalid arguments specified");
        return NULL;
    }

    if ((gain < 0) || (gain >= ADS1256_GAIN_MAX)) {
        PyErr_SetString(ads1256_error, "Invalid gain specified");
        return NULL;
    }	    

    if ((data_rate < 0) || (data_rate >= ADS1256_DATA_RATE_MAX)) {
        PyErr_SetString(ads1256_error, "Invalid data rate specified");
        return NULL;
    }	    

    ads1256_configure_adc(gain, data_rate);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
ads1256_py_read_chip_id(PyObject *self, PyObject *args)
{
    uint8_t chip_id;

    chip_id = ads1256_read_chip_id();

    return Py_BuildValue("B", chip_id);
}

/*
 * Validate that the channel specified is valid for the given input mode.
 *
 * Returns 1 if it is valid, 0 if not.
 */
static uint8_t
ads1256_py_validate_channel(uint8_t channel, ADS1256_INPUT_MODE_E input_mode)
{
    if ((channel < 0) || 
        ((input_mode == ADS1256_INPUT_SINGLE_ENDED) &&
	 (channel >= ADS1256_SINGLE_CHANNEL_COUNT)) || 
        ((input_mode == ADS1256_INPUT_DIFFERENTIAL) &&
	 (channel >= ADS1256_DIFFERENTIAL_CHANNEL_COUNT))) {
        return 0;
    }	    

    return 1;
}

static PyObject*
ads1256_py_read_channel(PyObject *self, PyObject *args)
{
    uint8_t channel;
    ADS1256_INPUT_MODE_E input_mode;
    double result;

    if (!PyArg_ParseTuple(args, "Bi", &channel, &input_mode)) {
        PyErr_SetString(ads1256_error, "Invalid arguments specified");
        return NULL;
    }

    if ((input_mode != ADS1256_INPUT_SINGLE_ENDED) &&
	(input_mode != ADS1256_INPUT_DIFFERENTIAL)) {
        PyErr_SetString(ads1256_error, "Invalid input mode specified");
        return NULL;
    }

    if (ads1256_py_validate_channel(channel, input_mode) == 0) {
        PyErr_SetString(ads1256_error, "Invalid channel specified");
        return NULL;
    }

    result = ads1256_read_channel(channel, input_mode);

    return PyFloat_FromDouble(result);
}

static PyObject*
ads1256_py_read_channels(PyObject *self, PyObject *args)
{
    uint8_t i;
    uint8_t start_channel, end_channel, channel_count;
    ADS1256_INPUT_MODE_E input_mode;
    double *results;
    PyObject *result_list;

    if (!PyArg_ParseTuple(args, "BBi", 
			  &start_channel, &end_channel, 
			  &input_mode)) {
        PyErr_SetString(ads1256_error, "Invalid arguments specified");
        return NULL;
    }

    if ((input_mode != ADS1256_INPUT_SINGLE_ENDED) &&
	(input_mode != ADS1256_INPUT_DIFFERENTIAL)) {
        PyErr_SetString(ads1256_error, "Invalid input mode specified");
        return NULL;
    }

    if ((ads1256_py_validate_channel(start_channel, input_mode) == 0) || 
        (ads1256_py_validate_channel(end_channel, input_mode) == 0) ||
        (start_channel > end_channel)) {
        PyErr_SetString(ads1256_error, "Invalid channel specified");
        return NULL;
    }

    channel_count = end_channel - start_channel + 1;
    results = calloc(channel_count, sizeof(double));
    if (results == NULL) {
        PyErr_SetString(ads1256_error, "Couldn't allocate the result buffer");
        return NULL;
    }

    if(ads1256_read_channels(start_channel, end_channel, input_mode, results)) {
        PyErr_SetString(ads1256_error, "Error reading input channels.");
        return NULL;
    }

    result_list = PyList_New(channel_count);
    for (i = 0; i < channel_count; i++) {
	PyObject* value = PyFloat_FromDouble(results[i]);
	PyList_SetItem(result_list, i, value); 
    }

    free(results);

    return result_list;
}

static PyObject*
ads1256_py_shutdown(PyObject *self, PyObject *args)
{
    ads1256_shutdown();

    Py_INCREF(Py_None);
    return Py_None;
}

