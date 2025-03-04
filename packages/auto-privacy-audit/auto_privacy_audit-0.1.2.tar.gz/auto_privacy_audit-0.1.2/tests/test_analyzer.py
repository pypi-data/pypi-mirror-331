import unittest
from auto_privacy_audit import PrivacyAuditAnalyzer

class TestPrivacyAuditAnalyzer(unittest.TestCase):
    def test_sensitive_detection(self):
        code = '''
import logging

def test():
    print("User email is test@example.com")
    logging.info("User password: 123456")
'''
        analyzer = PrivacyAuditAnalyzer(code)
        issues = analyzer.analyze()
        # 应该检测到两个问题
        self.assertEqual(len(issues), 2)
        keywords = [issue['keyword'] for issue in issues]
        self.assertIn('email', keywords)
        self.assertIn('password', keywords)

if __name__ == "__main__":
    unittest.main()
