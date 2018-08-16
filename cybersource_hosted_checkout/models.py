from django.db import models


class AstractCyberSourceTransaction(models.Model):
    """
    Stores credit card transaction receipts made with CyberSource.
    """
    id = models.BigAutoField(primary_key=True)
    uuid = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now_add=True)
    return_from_cybersource = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
