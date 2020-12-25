import unittest

class TestCase(unittest.TestCase):
    def test_1(self):
       
        # Begin Test Case Contents

        from Project3.project import generate_LMAOcode_from_LOLcode
        from Project3.interpreter import interpret
        
        def expect_exception(lolcode_str):
        	with self.assertRaises(Exception) as e:
        		generate_LMAOcode_from_LOLcode(lolcode_str)
        	print("Correctly raised assertion")
        
        def check_output(lolcode_str, expected_output):
        	lmaocode = generate_LMAOcode_from_LOLcode(lolcode_str)
        	print("Generated LMAOcode:")
        	print(lmaocode)
        	executed_output = interpret(lmaocode, 'LMAOcode')
        	self.assertEqual(expected_output, executed_output)
                
        lolcode_str = r"""
        HAI 1.450
        VISIBLE WHATEVR
        KTHXBYE
        """
        expected_output = "49\n"
        check_output(lolcode_str, expected_output)
        
        lolcode_str = r"""
        HAI 1.450
        VISIBLE WHATEVR WHATEVR WHATEVR
        KTHXBYE
        """
        expected_output = "499753\n"
        check_output(lolcode_str, expected_output)
        
        lolcode_str = r"""
        HAI 1.450
        I HAS A x ITZ A NUMBR AN ITZ WHATEVR 
        I HAS A y ITZ A NUMBR
        y R WHATEVR
        VISIBLE x y
        KTHXBYE
        """
        expected_output = "4997\n"
        check_output(lolcode_str, expected_output)
        
        lolcode_str = r"""
        HAI 1.450
        I HAS A x ITZ A NUMBR AN ITZ WHATEVR 
        I HAS A y ITZ A NUMBR
        y R WHATEVR
        VISIBLE x y
        KTHXBYE
        """
        expected_output = "9956\n"
        lmaocode = generate_LMAOcode_from_LOLcode(lolcode_str)
        print("Generated LMAOcode:")
        print(lmaocode)
        executed_output = interpret(lmaocode, 'LMAOcode', seed=1234)
        self.assertEqual(expected_output, executed_output)







        # End Test Case Contents


if __name__ == '__main__':
    unittest.main()