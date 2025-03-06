"""
Class defining the general OpenMSIStream science_kit for running from the command line
(or as a Service/daemon)
"""

# imports
from abc import ABC, abstractmethod
from openmsimodel.utilities.has_arguments import HasArguments
from openmsimodel.utilities.has_argument_parser import HasArgumentParser


class Runnable(HasArguments, HasArgumentParser, ABC):
    """
    Abstract base class for any child classes that want to define some behavior
    for running from the command line (i.e. as a module)
    """

    ARGUMENT_PARSER_TYPE = None

    @classmethod
    def get_argument_parser(cls, *args, **kwargs):
        """
        Get the argument parser used to run the code

        :param args: Any arguments to this method are names of arguments recognized
            by Argument parsers of the :attr:`~Runnable.ARGUMENT_PARSER_TYPE` type
        :type args: list
        :param kwargs: Any keyword arguments to this method define custom default values
            for their given arguments, whose names must be recognized by Argument parsers
            of the :attr:`~Runnable.ARGUMENT_PARSER_TYPE` type
        :type kwargs: dict

        :return: An argument parser of the :attr:`~Runnable.ARGUMENT_PARSER_TYPE` type to use
            for the object
        """
        parser = cls.ARGUMENT_PARSER_TYPE(*args, **kwargs)
        cl_args, cl_kwargs = cls.get_command_line_arguments()
        parser.add_arguments(*cl_args, **cl_kwargs)
        return parser

    @classmethod
    @abstractmethod
    def run_from_command_line(cls, args=None):
        """
        Child classes should implement this function to do whatever it is they do
        when they run from the command line

        :param args: the list of arguments to send to the parser instead of
            getting them from sys.argv
        :type args: list
        """
        raise NotImplementedError
