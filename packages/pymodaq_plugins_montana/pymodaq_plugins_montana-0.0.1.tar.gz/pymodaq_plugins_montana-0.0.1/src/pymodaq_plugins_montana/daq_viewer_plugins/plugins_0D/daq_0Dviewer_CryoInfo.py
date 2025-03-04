import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport
from pymodaq_data import Q_
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins


from pymodaq_plugins_montana.hardware.scryostation import SCryostation
from pymodaq_plugins_montana.utils import Config as PluginConfig


plugin_config = PluginConfig()


class DAQ_0DViewer_CryoInfo(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    Attributes:
    -----------
    controller: SCryostation
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    """
    params = comon_parameters+[
        {'title': 'Server IP:', 'name': 'ipaddress', 'type': 'str', 'value': plugin_config('ip_address')},
        {'title': 'Cryo. Port:', 'name': 'cryo_port', 'type': 'int', 'value': plugin_config('cryo_port')},
        {'title': 'Temperatures:', 'name': 'temperatures', 'type': 'group', 'children':[
            {'title': 'Stage 1:', 'name': 'stage1', 'type': 'float', 'value': 290., 'suffix': 'K'},
            {'title': 'Stage 2:', 'name': 'stage2', 'type': 'float', 'value': 290., 'suffix': 'K'},
            {'title': 'Platform:', 'name': 'platform', 'type': 'float', 'value': 290., 'suffix': 'K'},
            {'title': 'User 1:', 'name': 'user1', 'type': 'float', 'value': 290., 'suffix': 'K'},
        ]},
        {'title': 'Pressure:', 'name': 'pressure', 'type': 'float', 'value': 1000., 'suffix': 'mbar'},
        ]

    def ini_attributes(self):
        self.controller: SCryostation = None

        self.temperatures = DataFromPlugins('Temperatures', data=[np.array([290]),
                                                                  np.array([290]),
                                                                  np.array([290]),
                                                                  np.array([290])],
                                            units='K',
                                            labels=['Stage 1', 'Stage 2', 'Platform', 'User 1'])

        self.pressure = DataFromPlugins('Pressure', data=[np.array([1000, ])],
                                        units='mbar',
                                        labels=['pressure'])

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        pass

    def update_temperatures(self):

        temps = [self.controller.get_stage1_temperature()[1],
                 self.controller.get_stage2_temperature()[1],
                 self.controller.get_platform_temperature()[1],
                 self.controller.get_user1_temperature()[1]]

        self.temperatures.data = [np.array([temp]) for temp in temps]

        self.settings.child('temperatures', 'stage1').setValue(temps[0])
        self.settings.child('temperatures', 'stage2').setValue(temps[1])
        self.settings.child('temperatures', 'platform').setValue(temps[2])
        self.settings.child('temperatures', 'user1').setValue(temps[3])

    def update_pressure(self):
        pressure = Q_(self.controller.get_sample_chamber_pressure(), 'Pa').to('mbar').magnitude
        self.settings.child('pressure').setValue(pressure)
        self.pressure.data[0] = np.array([pressure])


    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        if self.is_master:
            self.controller = SCryostation(self.settings['ipaddress'], port=self.settings['cryo_port'])  #instantiate you driver with whatever arguments are needed
        else:
            self.controller = controller

        self.update_temperatures()
        self.update_pressure()
        self.dte_signal_temp.emit(DataToExport('Cryo', data=[self.temperatures, self.pressure]))

        info = "Cryo connected"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.close()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        self.update_temperatures()
        self.update_pressure()
        self.dte_signal.emit(DataToExport('Cryo', data=[self.temperatures, self.pressure]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        return ''


if __name__ == '__main__':
    main(__file__)
