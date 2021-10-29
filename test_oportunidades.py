import unittest
from tasas import Rates_arbitrage

class TestOportunities(unittest.TestCase):  
  
  #testeo la habilidad de encontrar oportunidades de arbitraje dados los precios
    def test_oportunidad_arb(self):
        print('Test Oportunidad de Arbitraje')
        
        runArb = Rates_arbitrage()
        runArb.init_instruments_test()
        colocadora, tomadora = runArb.update_rates() 

        runArb.compare_rates(colocadora, tomadora, esTest=1)
        ops = runArb.testOP

        #mirando los rates calculados es facil hacer la cuenta de que tendria que devolver
        #devuelve un diccionario que tiene a cada tasa colocadora como key, y en sus correspondientes
        #values encontramos las tasas tomadoras con las que tenemos oportunidades
        expected_dict = dict()
        expected_dict[44.558] = [6.614, 7.172, 9.301]
        expected_dict[5.575] = []
        expected_dict[4.577] = []
        expected_dict[7.795] = [6.614, 7.172]

        self.assertEqual(ops, expected_dict)

if __name__ == '__main__':
    unittest.main()
