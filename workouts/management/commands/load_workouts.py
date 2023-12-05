from pathlib import Path

from django.core.management.base import BaseCommand

from workouts.models import SetOfExercise


class Command(BaseCommand):
    help = "Load workouts from an Excel file"

    def add_arguments(self, parser):
        parser.add_argument("path", type=Path, help="Path to the Excel file")

    def handle(self, *args, **kwargs):
        path = kwargs["path"]
        SetOfExercise.objects.create_from_excel(path)
        self.stdout.write(self.style.SUCCESS("Successfully loaded workouts"))
