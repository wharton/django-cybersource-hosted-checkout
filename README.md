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
* Once you have completed all of the fields, be sure to `Activate` the profile!

## Install Django CyberSource Hosted Checkout

First, `pip install django-cybersource-hosted-checkout`, and add `'cybersource_hosted_checkout'` to your `INSTALLED_APPS` list.

If you're going to be using the examples below to get started, you'll also need to `pip install django-braces`.

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

In this example, we will be charging a user of our Django site $19.95 in U.S. dollars to purchase a course.

First, create a model in an app in your Django project which inherits from `AbstractCyberSourceTransaction`; the abstract model stores a unique identifier, a transaction UUID, a time stamp of when the transaction is created in Django, and another time stamp of when it is completed from CyberSource. You can add any additional fields you wish to track and store. In this example, we are adding `user` and `course`, so we can complete the transaction after payment. Then `makemigrations` and `migrate`.

```python
from django.db import models
from cybersource_hosted_checkout.models import AbstractCyberSourceTransaction

class CyberSourceTransaction(AbstractCyberSourceTransaction):
    """
    Stores credit card transaction receipts made with CyberSource.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
```

### views.py

Here, we leverage a Django `FormView`, and in `form_valid()` we call the functions and render the template which will automatically prepare the data for CyberSource and POST it to their server. The `fields` dictionary contains CyberSource specific fields required to perform a transaction. You can see a full list in the manual; the example below is for a one-time purchase of the course for $19.95.

```python
import datetime
from uuid import uuid4
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.views.generic import FormView
from braces import LoginRequiredMixin, CsrfExemptMixin
from my_app.models import CyberSourceTransaction

class AddCourseView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'my_app/transaction.html'
    form_class = TransactionForm
    success_url = reverse_lazy('home')
    success_message = "Your transaction has been completed."

    def form_valid(self, form, request, **kwargs):
        # Get the proverbial `course` from the database based on something in the form.
        course = Course.objects.get(course_code=form.cleaned_data['course_code'])

        # Create a transaction in the database before we pass to CyberSource;
        # we will update this with a timestamp on return from CyberSource
        transaction_uuid = uuid4().hex
        transaction = CyberSourceTransaction()
        transaction.transaction_uuid = transaction_uuid
        transaction.user = request.user
        transaction.course = course
        transaction.save()

        # Fields to pass to CyberSource - see manual for a full list
        fields = {}
        fields['profile_id'] = settings.CYBERSOURCE_PROFILE_ID
        fields['access_key'] = settings.CYBERSOURCE_ACCESS_KEY
        fields['amount'] = '19.95'
        fields['transaction_uuid'] = transaction_uuid
        fields['bill_to_forename'] = request.user.first_name
        fields['bill_to_surname'] = request.user.last_name
        fields['bill_to_email'] = request.user.email
        fields['locale'] = 'en-us'
        fields['currency'] = 'usd'
        fields['transaction_type'] = 'sale'
        fields['reference_number'] = transaction.id

        context = super().get_context_data(**kwargs)
        context = sign_fields_to_context(fields, context)

        # Render a page which POSTs to CyberSource via JavaScript.
        return render(
            request,
            'cybersource_hosted_checkout/post_to_cybersource.html',
            context=context,
        )

class CyberSourceResponseView(CsrfExemptMixin, View):
    """
    Recevies a POST from CyberSource and redirects to home.
    """

    def post(self, request):
        if request.POST.get('decision').upper() == 'ACCEPT':
            # Success! Add the course by getting the transaction we started.
            # Check both reference number and UUID since we're not requiring
            # a login.
            transaction = CyberSourceTransaction.objects.get(
                id=request.POST.get('req_reference_number'),
                transaction_uuid=request.POST.get('req_transaction_uuid'),
            )
            transaction.return_from_cybersource = datetime.datetime.now()
            # Here is where you'll put your code in place of this dummy function.
            add_course_for_user(transaction.course, transaction.user, request)
            messages.success(
                request,
                'Your payment was successful and the course has been added. Happy trading!',
            )
            transaction.save()
        else:
            # Uh oh, unsuccessful payment.
            messages.error(
                request,
                'Sorry, your payment was not successful.',
            )

        return redirect(reverse_lazy('home'))
```

The `AddCourseView` class will display your purchase form, and when it is valid, pass the necessary fields to CyberSource to display their checkout page.

The `CyberSourceResponseView` is the class for the view that is run after a successful checkout from CyberSource. After successfully completing a purchase, the user will then be directed back to the route you put in your CyberSource profile (in the example, `https://www.mysite.com/orders/payment-response/`), where we mark the transaction as complete by updating the timestamp `return_from_cybersource` to mark the transaction complete.

### urls.py

We need to plug our views into routes that match CyberSource.

```python
from django.urls import path
from myapp.views import MyHomeView, AddCourseView, CyberSourceResponseView

urlpatterns = [
    path('', MyHomeView.as_view(), name='home'),
    path('orders/buy-course/', AddCourseView.as_view(), name='add-course'),
    path('orders/payment-response/', CyberSourceResponseView.as_view(), name='add-course-cybersource-response'),
]
```

## Release Notes

### 0.0.1 - 0.0.4

Initial releases and documentation improvements.

## Contributors

* Timothy Allen (https://github.com/FlipperPA)
