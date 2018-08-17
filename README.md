# Django CyberSource Hosted Checkout

This package provides utilities for using CyberSource Secure Acceptance Hosted Checkout.

CyberSource Secure Acceptance Hosted Checkout is a round-trip process: you start the payment on your server, then pass off to CyberSource. At the end of the transaction, CyberSource returns to your server at a URL you configure.

We assume you have a working knowledge of the product and profiles; you can [read the CyberSource manual here](http://apps.cybersource.com/library/documentation/dev_guides/Secure_Acceptance_WM/Secure_Acceptance_WM.pdf).

The heavy lifting it does is properly creating the `signed_date_time`, `fields_to_sign`, and `signature` fields and automatically include them in the `POST`, along with any fields you need to pass along.

If you don't feel like making your eyes bleed with that awful PDF above, here's a TL;DR.

## Create Your CyberSource Profile

You'll have to do this in both the CyberSource TEST and LIVE environments. Start with TEST. The process is the same.

* Log in here: https://businesscenter.cybersource.com/ebc/login/
* Under `Tools & Settings`, click `Profiles`, then `Create New Profile`.
* Fill in the form and click `Save`. Then click the profile name you just created to edit it further.
* Copy your `Profile ID` from this screen into your Django settings as `CYBERSOURCE_PROFILE_ID`. You will notice there are eight sections you can modify. I will only cover the required areas here.
    * Payment Settings: enter at least one `Card Type` with at least one `Currency` associated with it.
    * Security: click `Create New Key`. Copy the `Access Key` and `Secret Key` values to your Django settings as `CYBERSOURCE_ACCESS_KEY` and `CYBERSOURCE_SECRET_KEY` respectively.
    * Customer Response Pages: for `Transaction Response Page`, select `Hosted by you`, and enter a route that you will create later in Django, such as `https://www.mysite.com/orders/payment-response/`

## Install Django CyberSource Hosted Checkout

First, `pip install django-cybersource-hosted-checkout`, and add `'cybersource_hosted_checkout'` to your `INSTALLED_APPS` list.

### Settings

These settings are required to be present in Django's settings.

* `CYBERSOURCE_URL`
    * For CyberSource's TEST Environment: `https://testsecureacceptance.cybersource.com/pay`
    * For CyberSource's LIVE Environment: `https://secureacceptance.cybersource.com/pay`
* `CYBERSOURCE_PROFILE_ID` = '[Your CyberSource Profile ID]'
* `CYBERSOURCE_ACCESS_KEY` = '[Your CyberSource Access Key]'
* `CYBERSOURCE_SECRET_KEY` = '[Your CyberSource Secret Key]'

## Code and Configuration

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

You can call the relevant functions from within a FormView.

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

        # Fields to pass to CyberSource
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
        fields['transaction_type'] = 'sale'
        fields['reference_number'] = transaction.id

        context = sign_fields_to_context(fields, context)

        # Render a page which POSTs to CyberSource via JavaScript.
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
