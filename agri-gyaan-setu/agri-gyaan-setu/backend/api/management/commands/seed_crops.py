from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed the Crop table with sample crops (idempotent).'

    def handle(self, *args, **options):
        from api.models import Crop

        samples = [
            {'name':'Rice','nitrogen':1.0,'phosphorus':1.0,'potassium':1.0,'temperature':30.0,'humidity':70.0,'ph':6.5,'rainfall':200},
            {'name':'Wheat','nitrogen':0.8,'phosphorus':0.7,'potassium':0.9,'temperature':22.0,'humidity':60.0,'ph':6.8,'rainfall':120},
            {'name':'Maize','nitrogen':0.9,'phosphorus':0.6,'potassium':0.8,'temperature':25.0,'humidity':65.0,'ph':6.7,'rainfall':150},
            {'name':'Sugarcane','nitrogen':1.2,'phosphorus':1.1,'potassium':1.3,'temperature':28.0,'humidity':75.0,'ph':6.4,'rainfall':220},
            {'name':'Cotton','nitrogen':0.7,'phosphorus':0.5,'potassium':0.6,'temperature':27.0,'humidity':55.0,'ph':6.5,'rainfall':90},
            {'name':'Millet','nitrogen':0.6,'phosphorus':0.4,'potassium':0.5,'temperature':24.0,'humidity':50.0,'ph':7.0,'rainfall':80},
            {'name':'Barley','nitrogen':0.75,'phosphorus':0.6,'potassium':0.7,'temperature':20.0,'humidity':55.0,'ph':6.9,'rainfall':100},
            {'name':'Sorghum','nitrogen':0.65,'phosphorus':0.45,'potassium':0.55,'temperature':26.0,'humidity':58.0,'ph':6.6,'rainfall':110},
            {'name':'Soybean','nitrogen':0.95,'phosphorus':0.8,'potassium':0.85,'temperature':23.0,'humidity':63.0,'ph':6.7,'rainfall':130},
            {'name':'Potato','nitrogen':1.1,'phosphorus':0.9,'potassium':1.0,'temperature':18.0,'humidity':80.0,'ph':6.0,'rainfall':300},
        ]

        created = 0
        for s in samples:
            obj, created_flag = Crop.objects.get_or_create(name=s['name'], defaults=s)
            if created_flag:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Inserted sample crops: {created}'))
