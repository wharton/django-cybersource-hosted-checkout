from django.test import TestCase

from cybersource_hosted_checkout.utils import create_sha256_signature


class UtilTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sha256_signature(self):
        key = 'testkeytestkeytestkeytestkey'
        message = 'key1=value1,key2=value2,key3=value3'

        response = create_sha256_signature(key, message)

        self.assertEqual(response, 'A8ew8SEYdgbyeiiQBWFYHsW1pcAAZFroS331gMDzBaI=')
