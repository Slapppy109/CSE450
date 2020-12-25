import unittest

class TestCase(unittest.TestCase):
    def test_1(self):
       
        # Begin Test Case Contents

        from Project4.project import generate_LMAOcode_from_LOLcode
        from Project4.interpreter import interpret

        def expect_exception(lolcode_str):
            with self.assertRaises(Exception) as e:
                generate_LMAOcode_from_LOLcode(lolcode_str)
            print("Correctly raised assertion\n")
                
        def check_output(lolcode_str, expected_output):
        	lmaocode = generate_LMAOcode_from_LOLcode(lolcode_str)
        	print("Generated LMAOcode:")
        	print(lmaocode)
        	executed_output = interpret(lmaocode, 'LMAOcode')
        	self.assertEqual(expected_output, executed_output)

        lolcode_str = r"""
        HAI 1.450
        VISIBLE GIMMEH
        I HAS A x ITZ A NUMBR AN ITZ 5
        I HAS A y ITZ A NUMBR AN ITZ 6
        VISIBLE x y
        O RLY? WIN
          YA RLY
            VISIBLE x y   
        OIC
        VISIBLE x y
        KTHXBYE
        """
        check_output(lolcode_str, 'a\n56\n56\n56\n')
        
        lolcode_str = r"""
        HAI 1.450
        VISIBLE GIMMEH
        I HAS A x ITZ A NUMBR AN ITZ 5
        I HAS A y ITZ A NUMBR AN ITZ 6
        VISIBLE x y
        O RLY? WIN
          YA RLY
            VISIBLE x y   
            I HAS A x ITZ A NUMBR AN ITZ 10
            I HAS A z ITZ A NUMBR AN ITZ 11
            VISIBLE x y z
        OIC
        VISIBLE x y
        KTHXBYE
        """
        check_output(lolcode_str, 'a\n56\n56\n10611\n56\n')
        
        lolcode_str = r"""
        HAI 1.450
        VISIBLE GIMMEH
        I HAS A x ITZ A NUMBR AN ITZ 5
        I HAS A y ITZ A NUMBR AN ITZ 6
        VISIBLE x y
        O RLY? WIN
          YA RLY
            VISIBLE x y   
            I HAS A x ITZ A NUMBR AN ITZ 10
            I HAS A z ITZ A NUMBR AN ITZ 11
            VISIBLE x y z
        OIC
        VISIBLE x y z
        KTHXBYE
        """
        expect_exception(lolcode_str)
        
        lolcode_str = r"""
        HAI 1.450
        VISIBLE GIMMEH
        I HAS A x ITZ A NUMBR AN ITZ 5
        I HAS A y ITZ A NUMBR AN ITZ 6
        VISIBLE x y
        O RLY? WIN
          YA RLY
            VISIBLE x y   
            I HAS A x ITZ A NUMBR AN ITZ 10
            I HAS A z ITZ A NUMBR AN ITZ 11
            VISIBLE x y z
        OIC
        I HAS A z ITZ A NUMBR AN ITZ 13
        VISIBLE x y z
        KTHXBYE
        """
        check_output(lolcode_str, 'a\n56\n56\n10611\n5613\n')
                
if __name__ == '__main__':
    unittest.main()