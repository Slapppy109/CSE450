import unittest

class TestCase(unittest.TestCase):
    def test_1(self):
       
        # Begin Test Case Contents

        from Project6.project import generate_LMAOcode_from_LOLcode, generate_ROFLcode_from_LOLcode
        from Project6.interpreter import interpret        
    
        SEED = 0
        STANDARD_INPUT = "aabzbdaeaabbccaaa"
        
        def strip_leading_whitespace(text):
            lines = [line.lstrip() for line in text.splitlines()]
            return '\n'.join(lines)
        
        def expect_exception(lolcode_str):
            print(f"LOLcode str:\n{lolcode_str}")
            with self.assertRaises(Exception) as e:
                generate_LMAOcode_from_LOLcode(lolcode_str)
            with self.assertRaises(Exception) as e:
                generate_ROFLcode_from_LOLcode(lolcode_str)
            print("Correctly raised exception")
        
        def check_output(lolcode_str, expected_output):
            print(f"LOLcode str:\n{lolcode_str}")
            lmaocode = generate_LMAOcode_from_LOLcode(lolcode_str)
            print("Generated LMAOcode:")
            print(lmaocode)
            executed_lmao_output = interpret(lmaocode, 'LMAOcode', seed=SEED, standard_input=STANDARD_INPUT)
            
            self.assertEqual(expected_output, executed_lmao_output)
        
            roflcode = generate_ROFLcode_from_LOLcode(lolcode_str)
            print("Generated ROFLcode:")
            print(roflcode)
            executed_rofl_output = interpret(roflcode, 'ROFLcode', seed=SEED, standard_input=STANDARD_INPUT)
            
            self.assertEqual(expected_output, executed_rofl_output)
        
        
        
        lolcode_str = r"""
        HAI 1.450
        VISIBLE GIMMEH WHATEVR
        
        I HAS A char ITZ A LETTR AN ITZ 'c'
        
        WTF? char
          OMG 'a'
            VISIBLE "Handle 'a'"
          OMG 'b'
            VISIBLE "Handle 'b'"
          OMG 'c'
            VISIBLE "Handle 'c'"
          OMG 'd'
            VISIBLE "Handle 'd'"
          OMGWTF
            VISIBLE "Couldn't Find It" 
        OIC
        KTHXBYE
        """
        check_output(lolcode_str, "a49\nHandle 'c'\nHandle 'd'\nCouldn't Find It\n")
        
        lolcode_str = r"""
        HAI 1.450
        VISIBLE GIMMEH WHATEVR
        
        I HAS A char ITZ A LETTR AN ITZ 'a'
        
        WTF? char
          OMG 'a'
            VISIBLE "Handle 'a'"
          OMG 'b'
            VISIBLE "Handle 'b'"
            GTFO
          OMG 'c'
            VISIBLE "Handle 'c'"
          OMG 'd'
            VISIBLE "Handle 'd'"
          OMGWTF
            VISIBLE "Couldn't Find It" 
        OIC
        KTHXBYE
        """
        check_output(lolcode_str, "a49\nHandle 'a'\nHandle 'b'\n")
        
        lolcode_str = r"""
        HAI 1.450
        VISIBLE GIMMEH WHATEVR
        
        I HAS A char ITZ A LETTR AN ITZ '!'
        
        WTF? char
          OMG 'a'
            VISIBLE "Handle 'a'"
          OMG 'b'
            VISIBLE "Handle 'b'"
            GTFO
          OMG 'c'
            VISIBLE "Handle 'c'"
          OMG 'd'
            VISIBLE "Handle 'd'"
          OMGWTF
            VISIBLE "Couldn't Find It" 
        OIC
        KTHXBYE
        """
        check_output(lolcode_str, "a49\nCouldn't Find It\n")



        # End Test Case Contents


if __name__ == '__main__':
    unittest.main()