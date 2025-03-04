
from typing import Union, List, Dict
from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun,
                                                          main, DataActuatorType, DataActuator)

from pymodaq_utils.utils import ThreadCommand
from pymodaq_utils.logger import set_logger, get_module_name

from pymodaq_data import Q_
from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_montana.hardware.scryostation import SCryostation
from pymodaq_plugins_montana.utils import Config as PluginConfig


plugin_config = PluginConfig()
logger = set_logger(get_module_name(__file__))


class DAQ_Move_CryoTemperature(DAQ_Move_base):
    """ Instrument plugin class for an actuator.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.


    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
             """
    is_multiaxes = True
    _axis_names: Union[List[str], Dict[str, int]] = ['ATSM',]
    _controller_units: Union[str, List[str]] = 'K'
    _epsilon: Union[float, List[float]] = 0.01
    data_actuator_type = DataActuatorType.DataActuator

    params = [
         {'title': 'Server IP:', 'name': 'ipaddress', 'type': 'str', 'value': plugin_config('ip_address')},
         {'title': 'Cryo. Port:', 'name': 'cryo_port', 'type': 'int', 'value': plugin_config('cryo_port')},
         {'title': 'Temp. Stability', 'name': 'stability', 'type': 'float',
          'value': plugin_config('temp_stability'), 'suffix': 'K',
          'siPrefix': True}
             ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: SCryostation = None

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = DataActuator(data=self.controller.get_user1_temperature()[1])  # when writing your own plugin replace this line
        pos = self.get_position_with_scaling(pos)
        return pos

    def user_condition_to_reach_target(self) -> bool:
        """ Implement a user defined condition for exiting the polling mechanism and specifying
        that the target value has been reached (on top of the existing epsilon mechanism)

        Should be reimplemented in plugins to implement other conditions

        Returns
        -------
        bool: if True, PyMoDAQ considers the target value has been reached
        """
        logger.debug(f'Temp stab is {self.controller.get_user1_temperature_stability()[1]}')
        return self.controller.get_user1_temperature_stability()[1] < self.settings['stability']


    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.set_user1_temperature_controller_enabled(False)
            self.controller.close()

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        pass

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        if self.is_master:  # is needed when controller is master
            self.controller = SCryostation(self.settings['ipaddress'], port=self.settings['cryo_port'])
        else:
            self.controller = controller

        self.controller.set_user1_temperature_controller_enabled(True)
        self.settings.child('timeout').setValue(1000) # allows for temperature stabilisation

        self.emit_status(ThreadCommand('update_ui', attribute='set_abs_value_red',
                                       args=[Q_(plugin_config('target_temp_1'),
                                                self.axis_unit)]))

        self.emit_status(ThreadCommand('update_ui', attribute='set_abs_value_green',
                                       args=[Q_(plugin_config('target_temp_2'),
                                                self.axis_unit)]))

        info = "Cryo connected"
        initialized = True
        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """

        value = self.check_bound(value)  #if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one
        self.controller.set_user1_target_temperature(value.value())  # when writing your own plugin replace this line

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)

        self.controller.set_user1_target_temperature(self.target_value.value())

    def move_home(self):
        """Call the reference method of the controller"""

        self.controller.set_user1_target_temperature(290.)

    def stop_motion(self):
      """Stop the actuator and emits move_done signal"""
      self.controller.set_user1_target_temperature(self.controller.get_user1_temperature()[1])


if __name__ == '__main__':
    main(__file__)
