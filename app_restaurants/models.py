from django.db import IntegrityError, models


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        "auth.User", related_name="restaurants", on_delete=models.PROTECT
    )


class Ticket(models.Model):
    name = models.CharField(max_length=100)
    max_purchase_count = models.PositiveIntegerField(default=0)
    purchase_count = models.PositiveIntegerField(default=0)
    restaurant = models.ForeignKey(
        Restaurant, related_name="tickets", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        if self.purchase_count > self.max_purchase_count:
            raise IntegrityError
        super().save(*args, **kwargs)
