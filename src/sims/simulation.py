class Simulation:
    def __init__(self, name: str):
        self.name = name
        self._deltaT: float = self.get_deltaT()

    def set_deltaT(self, deltaT: float):
        self._deltaT = deltaT

    def get_deltaT(self) -> float:
        return 1.0

    def advance(self) -> None:
        """
        Args:
            None
        Returns:
            None

        Advances the simulation by one time step.
        """
        pass

    def run(self) -> None:
        """
        Args:
            None
        Returns:
            None

        Runs the simulation until it is complete.
        """
        pass
