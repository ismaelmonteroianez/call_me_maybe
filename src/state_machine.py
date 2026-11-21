from enum import Enum
from src.models import FunctionDefinition, TypeDefinition
from src import constraints


class State(Enum):
    START = 1
    NAME = 2
    PARAMETERS_START = 3
    PARAMETER_NAME = 4
    PARAMETER_VALUE = 5
    PARAMETERS_END = 6
    END = 7


class StateMachine:

    def __init__(self, functions: list[FunctionDefinition]):
        self.functions = functions
        self.state = State.START
        self.generated_name = ""
        self.generated_parameters = ""
        self.current_fragment = ""
        self.selected_function: FunctionDefinition | None = None
        self.parameters: list[tuple[str, TypeDefinition]] = []
        self.parameter_index = 0

    def change_state(self, new_state: State) -> None:
        self.state = new_state
        self.current_fragment = ""

    def get_current_parameter(self) -> tuple[str, TypeDefinition]:
        return self.parameters[self.parameter_index]

    def select_function(self, function_name: str) -> None:
        for function in self.functions:
            if function.name == function_name:
                self.selected_function = function
                self.parameters = list(function.parameters.items())
                self.parameter_index = 0
                self.change_state(State.PARAMETERS_START)
                return

    def next_parameter(self) -> None:
        self.parameter_index += 1
        self.change_state(State.PARAMETERS_END)

    def validate(self) -> bool:
        if self.state == State.START:
            return constraints.validate_start(self.current_fragment)
        if self.state == State.NAME:
            return constraints.validate_function_name_prefix(
                self.functions, self.current_fragment)
        elif self.state == State.PARAMETERS_START:
            return constraints.validate_parameters_start(
                self.current_fragment)
        elif self.state == State.PARAMETER_NAME:
            parameter_name, _ = self.get_current_parameter()
            return constraints.validate_parameter_name_prefix(
                parameter_name, self.current_fragment)
        elif self.state == State.PARAMETER_VALUE:
            _, definition = self.get_current_parameter()
            if definition.type == "string":
                return constraints.validate_string_prefix(
                    self.current_fragment)
            if definition.type == "number":
                return constraints.validate_number_prefix(
                    self.current_fragment)
            if definition.type == "boolean":
                return constraints.validate_boolean_prefix(
                    self.current_fragment)
        elif self.state == State.PARAMETERS_END:
            has_more_parameters = self.parameter_index < len(self.parameters)
            return constraints.validate_parameters_end(
                            self.current_fragment, has_more_parameters)
        elif self.state == State.END:
            return constraints.validate_end(self.current_fragment)
        return True

    def add_generated_text(self, text: str) -> bool:
        for char in text:
            if self.state == State.PARAMETER_VALUE:
                _, definition = self.get_current_parameter()
                if definition.type == "number" and char in ",}":
                    if constraints.is_number_complete(self.current_fragment):
                        self.next_parameter()
            self.current_fragment += char
            if self.state == State.NAME:
                self.generated_name += char

            elif self.state in (
                               State.PARAMETERS_START,
                               State.PARAMETER_NAME,
                               State.PARAMETER_VALUE,
                               State.PARAMETERS_END
                               ):
                self.generated_parameters += char

            if not self.validate():
                return False
            if self.state == State.START:
                if constraints.is_start_complete(self.current_fragment):
                    self.change_state(State.NAME)
            elif self.state == State.NAME:
                if constraints.is_function_name_complete(
                                                        self.functions,
                                                        self.current_fragment
                                                        ):
                    self.select_function(self.current_fragment)

            elif self.state == State.PARAMETERS_START:
                if constraints.is_parameters_start_complete(
                        self.current_fragment):
                    self.change_state(State.PARAMETER_NAME)

            elif self.state == State.PARAMETER_NAME:
                parameter_name, _ = self.get_current_parameter()

                if constraints.is_parameter_name_complete(
                                                         parameter_name,
                                                         self.current_fragment
                                                         ):
                    self.change_state(State.PARAMETER_VALUE)
            elif self.state == State.PARAMETER_VALUE:
                _, definition = self.get_current_parameter()
                if definition.type == "boolean":
                    if constraints.is_boolean_complete(self.current_fragment):
                        self.next_parameter()
                elif definition.type == "string":
                    if constraints.is_string_complete(self.current_fragment):
                        self.next_parameter()
            elif self.state == State.PARAMETERS_END:
                has_more_parameters = (
                    self.parameter_index < len(self.parameters)
                )

                if constraints.is_parameters_end_complete(
                                self.current_fragment,
                                has_more_parameters):
                    if has_more_parameters:
                        self.change_state(State.PARAMETER_NAME)
                    else:
                        self.change_state(State.END)
        return True
