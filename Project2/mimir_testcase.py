import unittest

class TestCase(unittest.TestCase):
    def test(self):
        from Project2.project import parse_LOLcode

        def parse_LOLcode_exception(lolcode_str):
            with self.assertRaises(Exception) as e:
                parse_LOLcode(lolcode_str)
        
        parse_LOLcode(r"""HAI 1.450
        I HAS A x ITZ A NUMBR AN ITZ 12
        x R WHATEVR
        VISIBLE x
        KTHXBYE""")
        print("Can assign random NUMBR")
        
        parse_LOLcode(r"""HAI 1.450
        I HAS A x ITZ A NUMBR AN ITZ 12
        x R DIFF OF 5 AN WHATEVR
        VISIBLE x
        KTHXBYE""")
        print("Random is an expression")


if __name__ == '__main__':
    unittest.main()