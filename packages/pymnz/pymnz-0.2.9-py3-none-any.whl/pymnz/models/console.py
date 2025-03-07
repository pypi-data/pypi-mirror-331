from pymnz.utils import countdown_timer, retry_on_failure
from pymnz.utils.classes import singleton
import sys
import os


@singleton
class Script:
    def __init__(self, name, code, *args, **kwargs):
        self.name = name
        self.code_start = None
        self.args_start = None
        self.kwargs_start = None
        self.code = code
        self.args = args
        self.kwargs = kwargs
        self.execution_interval = 10
        self.execution_interval_msg = 'Executando novamente em'
        self.width = 80
        self.separator_format = '='
        self.terminator_format = 'x'
        self.terminator_msg = 'Fim do script'

    def _show_header(self):
        """Amostrar cabeçalho"""
        print(self.separator_format * self.width)
        print(str(self.name).upper().center(self.width))
        print(self.separator_format * self.width)

    def _run_code(self, code, *args, **kwargs):
        """Rodar código"""
        if code is not None:
            code(*args, **kwargs)
            print(self.separator_format * self.width)

    @retry_on_failure(1000)
    def _run_code_with_retry_on_failure(self, code, *args, **kwargs):
        """Rodar código com repetição por falha"""
        self._run_code(code, *args, **kwargs)

    def _run(self, code, with_retry_on_failure, *args, **kwargs):
        """ Rodar código de acordo com os parâmetros """
        # Com repetição por falha
        if with_retry_on_failure:
            self._run_code_with_retry_on_failure(code, *args, **kwargs)

        else:  # Sem repetição por falha
            self._run_code(code, *args, **kwargs)

    def run(self, with_retry_on_failure: bool = True):
        # Limpar console
        os.system('cls')

        # Amostrar cabeçalho
        self._show_header()

        try:
            # Rodar código inicial
            if self.code_start is not None:
                self._run(self.code_start, with_retry_on_failure, *self.args_start, **self.kwargs_start)

            # Rodar código
            while True:
                self._run(self.code, with_retry_on_failure, *self.args, **self.kwargs)

                countdown_timer(self.execution_interval, self.execution_interval_msg)

        except KeyboardInterrupt:
            print(self.terminator_format * self.width)
            sys.exit(self.terminator_msg)

    def set_code_start(self, code, *args, **kwargs):
        """ Adicionar código inicial """
        self.code_start = code
        self.args_start = args
        self.kwargs_start = kwargs

        return self
