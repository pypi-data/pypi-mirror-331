import unittest
from auth_parser.parser import parse_user_agent

class TestUserAgentParser(unittest.TestCase):
    def test_parse_user_agent(self):
        ua_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        result = parse_user_agent(ua_string)
        self.assertEqual(result['browser_family'], 'Chrome')
        self.assertEqual(result['os_family'], 'Windows')
        self.assertEqual(result['device_family'], 'Other')

if __name__ == '__main__':
    unittest.main()
