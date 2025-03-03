from .command import Command
import argparse

class SerialCommand(Command):
    def __init__(self) -> None:
        super().__init__()

        self._parser = argparse.ArgumentParser()
        self._parser.add_argument('-p', '--port', type=str, required=True)
        self._parser.add_argument('-b', '--baudrate', type=int, required=True)

    def run(self, remaining_args):
        #print(f'{remaining_args=}')

        args = self._parser.parse_args(remaining_args)

        print(f'port : {args.port}')
        print(f'baudrate : {args.baudrate}')