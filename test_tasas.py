import unittest
from tasas import Rates_arbitrage

class TestRates(unittest.TestCase):

    #testeo el calculo de las tasas implicitas    
    def test_tasas_implicitas(self):
        print('Test Calculo Tasas Implicitas')
        runArb = Rates_arbitrage()
        runArb.init_instruments_test()
        colocadora, tomadora = runArb.update_rates() 
        
        #     "ARS=X"      "GGAL.BA"     "PAMP.BA"      "YPFD.BA"
        #   "DLR/Dic21"   "GGAL/Dic21"  "PAMP/Dic21"   "YPFD/Dic21"
        expected_c = [44.558, 5.575, 4.577, 7.795]         #calculados a mano
        expected_t = [8.447, 6.614, 7.172, 9.301]

        self.assertEqual(expected_c, colocadora)
        self.assertEqual(expected_t, tomadora)
        print("finished tasas")
 
if __name__ == '__main__':
    unittest.main()
