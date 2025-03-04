
from typing import Union, List, Dict
from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun,
                                                          main, DataActuatorType, DataActuator)

from pymodaq_utils.logger import set_logger, get_module_name
from pymodaq_utils.utils import ThreadCommand  # object used to send info back to the main thread

from pymodaq_data import Q_

from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_montana.hardware.rook import Rook
from pymodaq_plugins_montana.utils import Config as PluginConfig


plugin_config = PluginConfig()
logger = set_logger(get_module_name(__file__))


class DAQ_Move_Rook(DAQ_Move_base):
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
    _axis_names: Union[List[str], Dict[str, int]] = {'Xaxis': 1, 'Yaxis': 2, 'Zaxis':3}
    _controller_units: Union[str, List[str]] = 'm'
    _epsilon: Union[float, List[float]] = 1e-7
    data_actuator_type = DataActuatorType.DataActuator
    params = [
                 {'title': 'Server IP:', 'name': 'ipaddress', 'type': 'str', 'value': plugin_config('ip_address')},
                 {'title': 'Cryo. Port:', 'name': 'cryo_port', 'type': 'int', 'value': plugin_config('rook_port')},
                ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: Rook = None
        self.stack_num = 1

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """

        pos = DataActuator(data=self.controller.get_axis_encoder_position(self.stack_num, self.axis_value),
                           units=self.axis_unit)
        pos = self.get_position_with_scaling(pos)
        return pos

    def user_condition_to_reach_target(self) -> bool:
        """ Implement a condition for exiting the polling mechanism and specifying that the
        target value has been reached

       Returns
        -------
        bool: if True, PyMoDAQ considers the target value has been reached
        """
        return not self.controller.get_axis_moving(self.stack_num, self.axis_value)

    def close(self):
        """Terminate the communication protocol"""
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
            self.controller = Rook(ip=self.settings['ipaddress'], port=self.settings['cryo_port'])
        else:
            self.controller = controller

        self.emit_status(ThreadCommand('update_ui', attribute='set_abs_value_red',
                                           args=[Q_(0, 'um')]))

        self.emit_status(ThreadCommand('update_ui', attribute='set_abs_value_green',
                                   args=[Q_(100, 'um')]))

        self.emit_status(ThreadCommand('update_ui', attribute='set_abs_value',
                                       args=[Q_(100, 'um')]))

        self.emit_status(ThreadCommand('update_ui', attribute='set_rel_value',
                                       args=[Q_(100, 'um')]))

        info = "Rook is connected"
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
        self.controller.move_axis_absolute_position(self.stack_num, self.axis_value, value.value())

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)

        self.move_abs(self.target_value)

    def move_home(self):
        """Call the reference method of the controller"""

        self.controller.move_axis_to_negative_limit(self.stack_num, self.axis_value, wait=True)

    def stop_motion(self):
      """Stop the actuator and emits move_done signal"""

      self.controller.stop_axis(self.stack_num, self.axis_value)


if __name__ == '__main__':
    main(__file__)
