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

Create a model in an app in your Django project which inherited from `AstractCyberSourceTransaction`; you can add any additional fields you wish to store. Then `makemigrations` and `migrate`.

```python
from cybersource_hosted_checkout.models import AstractCyberSourceTransaction

class CyberSourceTransaction(AstractCyberSourceTransaction):
    """
    Stores credit card transaction receipts made with CyberSource.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
```

### views.py

```python
from uuid import uuid4
from my_app.models import CyberSourceTransaction

class AddCourseView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'my_app/transaction.html'
    form_class = TransactionForm
    success_url = reverse_lazy('home')
    success_message = "Your transaction has been completed."

    def form_valid(self, form, request, **kwargs):
        # Create a transaction in the database before we pass to CyberSource;
        # we will update this with the course on the return call from CyberSource
        transaction_uuid = uuid4().hex
        transaction = CyberSourceTransaction()
        transaction.transaction_uuid = transaction_uuid
        transaction.user = request.user
        transaction.save()

        # Credit card; redirect to CyberSource
        context = super().get_context_data(**kwargs)
        fields = {}
        fields['profile_id'] = settings.CYBERSOURCE_PROFILE_ID
        fields['access_key'] = settings.CYBERSOURCE_ACCESS_KEY
        fields['amount'] = '99.99'
        fields['transaction_uuid'] = transaction_uuid
        fields['bill_to_forename'] = request.user.first_name
        fields['bill_to_surname'] = request.user.last_name
        fields['bill_to_email'] = request.user.email
        fields['locale'] = 'en-us'
        fields['currency'] = 'usd'
        fields['type'] = 'sale'
        fields['reference_number'] = transaction.id

        context = sign_fields_to_context(fields, context)

        return render(
            request,
            'cybersource_hosted_checkout/post_to_cybersource.html',
            context=context,
        )
```

## Release Notes

### 0.1.0

* Initial release

## Contributors

* Timothy Allen (https://github.com/FlipperPA)
