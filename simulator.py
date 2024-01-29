from pydantic import BaseModel


class Simulator(BaseModel):
    tassel_dimension: float
    cutting_time: int
    repetitions: int


def begin_simulation(simulator):
    with open('../SetUp/robot_file', 'r') as robot_file:
        robot_data = robot_file.read()

    with open('../SetUp/environment_file', 'r') as environment_file:
        environment_data = environment_file.read()

        # TODO: COME FACCIO A RIPETERE QUESTA COSA PER OGNI MAPPA? forse lo dovrei fare esternamente
        # todo: per ogni mappa possibile
        # todo: devi fare il controllo di dov'e' la stazione base
