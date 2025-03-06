from pymnz.models import Script

def test_models_script():
  def soma(a, b):
    print(f'A soma de {a} + {b} é {a + b}.')
    assert a + b == 3, "Problema no main"
    raise Exception('Teste de execução')

  def subtracao(a, b):
    print(f"A subtração de {a} - {b} é {a - b}.")
    assert a - b == 5, "Problema no main_start"
    return a - b

  try:
    script = Script('Script de teste', soma, a=1, b=2)
    script.set_code_start(subtracao, 10, 5)
    script.run(False)
  except Exception as e:
    assert str(e) == 'Teste de execução'
