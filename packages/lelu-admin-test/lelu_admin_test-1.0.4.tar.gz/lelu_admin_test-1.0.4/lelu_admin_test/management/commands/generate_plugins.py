"""
@author: Ethan
@contact: email:
@Created on: 2024/12/7 14:51
@Remark:
"""
import random
from django.core.management.base import BaseCommand
from faker import Faker
from lelu_admin_test.models import TestPlugin


class Command(BaseCommand):
    help = 'Generate plugins test records'

    def handle(self, *args, **kwargs):
        fake = Faker()
        age_list = [i for i in range(18, 56)]

        for _ in range(300):
            TestPlugin.objects.create(
                name=fake.name(),
                remark=fake.text(max_nb_chars=20),
                gender=random.choice(['male', 'female', 'other']),
                age=random.choice(age_list),
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated 300 plugins test records'))
