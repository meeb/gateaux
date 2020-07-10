import os
import glob
import subprocess
import unittest
from typing import ClassVar, List


class TypingTestCase(unittest.TestCase):

    MYPY_CMD: ClassVar[str] = 'mypy'

    def _run_mypy(self, filename: str) -> None:
        '''
            Runs mypy on an file as a subprocess
        '''
        args: List[str] = [self.MYPY_CMD] + self.global_args + [filename]
        exitcode: int = subprocess.call(args, env=os.environ, cwd=self.python_path)
        self.assertEqual(exitcode, 0, f'mypy on: {filename}')

    def _run_mypy_tests(self) -> None:
        '''
            Iterates over all Python files in the tests/ directory and calls _run_mypy
            on them.
        '''
        for test_file in glob.iglob(f'{os.getcwd()}/tests/**/*.py', recursive=True):
            print(f'type checking: {os.path.basename(test_file)} ... ', end='')
            self._run_mypy(test_file)
            print('ok')

    def test_typing(self) -> None:
        '''
            Called by unittest to start the type checking.
        '''
        print()
        self._run_mypy_tests()

    def __init__(self, *args, **kwargs) -> None:
        self.global_args: List[str] = ['--ignore-missing-imports']
        test_env = os.environ.copy()
        self.python_path: str = test_env.get('PYTHONPATH', os.getcwd())
        super().__init__(*args, **kwargs)
