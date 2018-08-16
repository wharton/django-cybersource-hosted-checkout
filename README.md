# Django CyberSource Hosted Checkout

This package provides utilities for using CyberSource Secure Acceptance Hosted Checkout.

## Settings

* CYBERSOURCE_URL
    * For testing / development: 'https://testsecureacceptance.cybersource.com/pay'
    * For production: 'https://secureacceptance.cybersource.com/pay'
CYBERSOURCE_PROFILE_ID = '[Your CyberSource Profile ID]'
CYBERSOURCE_ACCESS_KEY = '[Your CyberSource Access Key]'
CYBERSOURCE_SECRET_KEY = '[Your CyberSource Secret Key'

## Configuration

### models.py

```python
from cybersource_hosted_checkout.models import AstractCyberSourceTransaction

class CyberSourceTransaction(AstractCyberSourceTransaction):
    """
    Stores credit card transaction receipts made with CyberSource.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
```

## Release Notes

### 0.1.0

* Initial release

## Contributors

* Timothy Allen (https://github.com/FlipperPA)
