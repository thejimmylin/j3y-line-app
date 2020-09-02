from django.db import models


class QNA(models.Model):
    question = models.TextField(
        blank=True,
        null=True,
    )
    answer = models.TextField(
        blank=True,
        null=True,
    )
    learned_from = models.TextField(
        blank=True,
        null=True,
    )

class Follower(models.Model):
    user_id = models.TextField(
        blank=True,
        null=True,
    )
    display_name = models.TextField(
        blank=True,
        null=True,
    )
    picture_url = models.TextField(
        blank=True,
        null=True,
    )
    status_message = models.TextField(
        blank=True,
        null=True,
    )
    timestamp = models.BigIntegerField(
        blank=True,
        null=True,
    )
    state = models.TextField(
        blank=True,
        null=True,
    )
