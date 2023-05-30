import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из ingredients.csv файлов'

    def _load_ingredients(self):
        with open('ingredients.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            object_list = []
            for row in reader:
                object_list.append(Ingredient(**row))
            Ingredient.objects.bulk_create(objs=object_list)
        self.stdout.write('Игредиенты из ingredients.csv загружены!')

    def handle(self, *args, **options):
        self._load_ingredients()
