import unittest

class TestCase(unittest.TestCase):
    def test_1(self):
       
        # Begin Test Case Contents

        from Project5.project import generate_LMAOcode_from_LOLcode
        from Project5.interpreter import interpret        

        def strip_leading_whitespace(text):
            lines = [line.lstrip() for line in text.splitlines()]
            return '\n'.join(lines)

        def expect_exception(lolcode_str):
            print(f"LOLcode str:\n{lolcode_str}")
            with self.assertRaises(Exception) as e:
                generate_LMAOcode_from_LOLcode(lolcode_str)
            print("Correctly raised exception")

        def check_output(lolcode_str, expected_output):
            print(f"LOLcode str:\n{lolcode_str}")
            lmaocode = generate_LMAOcode_from_LOLcode(lolcode_str)
            print("Generated LMAOcode:")
            print(lmaocode)
            standard_input = "afdsafdjsaanjkankajaaakjnakaajknaaakjnkaaaakjnaakjnaaaaakjnakjnaaaakjnaaabkkahbakhbaaakhabahkbakbadsjnksajndfa"
            executed_output = interpret(lmaocode, 'LMAOcode', seed=0, standard_input=standard_input)
            
            self.assertEqual(expected_output, executed_output)


        # Create an array of a random size (use the RANDOM command)
        # Populate the array with letters from standard input (use the IN_CHAR)
        # Print out the number of 'a's in the array (and a newline).
        # Print out every third letter of the array (starting with the third letter) and a newline.
        lolcode_str = r"""
        HAI 1.450
        VISIBLE GIMMEH
        I HAS A WINNER ITZ A NUMBR AN ITZ 4
        VISIBLE WINNER
        KTHXBYE
        """
        check_output(lolcode_str, 'a\n4\n')

        



        # End Test Case Contents


if __name__ == '__main__':
    unittest.main()