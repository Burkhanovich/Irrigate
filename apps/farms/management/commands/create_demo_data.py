"""
Demo ma'lumotlar yaratish buyrug'i.
Ishga tushirish: python manage.py create_demo_data
"""
import random
from datetime import timedelta, time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Demo ma\'lumotlar yaratish'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Demo ma'lumotlar yaratilmoqda..."))

        admin = self._create_users()
        farmer = User.objects.get(username='farmer')
        farms = self._create_farms(farmer)
        fields = self._create_fields(farms)
        sensors = self._create_sensors(fields)
        self._create_readings(sensors)
        self._create_schedules(fields, farmer)
        self._create_events(fields, farmer)
        self._create_alerts(fields, sensors)

        self.stdout.write(self.style.SUCCESS("OK Demo ma'lumotlar muvaffaqiyatli yaratildi!"))
        self.stdout.write("")
        self.stdout.write("Kirish ma'lumotlari:")
        self.stdout.write(f"  Admin: admin@irrigate.uz / Admin1234!")
        self.stdout.write(f"  Fermer: farmer@irrigate.uz / Farmer1234!")

    def _create_users(self):
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@irrigate.uz',
                password='Admin1234!',
                full_name='Tizim Administratori',
                role='admin'
            )
            self.stdout.write("  OK Admin yaratildi")
        else:
            admin = User.objects.get(username='admin')

        if not User.objects.filter(username='farmer').exists():
            farmer = User.objects.create_user(
                username='farmer',
                email='farmer@irrigate.uz',
                password='Farmer1234!',
                full_name='Alisher Karimov',
                role='farmer',
                phone='+998901234567'
            )
            self.stdout.write("  OK Fermer yaratildi")
        else:
            farmer = User.objects.get(username='farmer')

        return admin

    def _create_farms(self, owner):
        from apps.farms.models import Farm

        farms_data = [
            {
                'name': 'Yangi Hayot Fermasi',
                'region': 'tashkent_region',
                'district': 'Zangiota tumani',
                'lat': Decimal('41.2756'),
                'lon': Decimal('69.1834'),
                'total_area': Decimal('45.50'),
                'description': 'Toshkent viloyatidagi asosiy ferma'
            },
            {
                'name': 'Bahor Bog\'i Fermasi',
                'region': 'tashkent_region',
                'district': 'Qibray tumani',
                'lat': Decimal('41.3721'),
                'lon': Decimal('69.3456'),
                'total_area': Decimal('32.00'),
                'description': 'Qibray tumanidagi meva-sabzavot fermasi'
            }
        ]

        farms = []
        for data in farms_data:
            farm, created = Farm.objects.get_or_create(
                name=data['name'],
                owner=owner,
                defaults=data
            )
            if created:
                self.stdout.write(f"  OK Ferma yaratildi: {farm.name}")
            farms.append(farm)

        return farms

    def _create_fields(self, farms):
        from apps.farms.models import Field

        fields_data = [
            {'farm': farms[0], 'name': 'Shimoliy paxta dalasi', 'area': Decimal('12.5'), 'crop_type': 'cotton',
             'irr_method': 'drip', 'soil_type': 'loam', 'kc_value': Decimal('1.15'),
             'planting_date': None, 'harvest_date': None},
            {'farm': farms[0], 'name': 'G\'arbiy bug\'doy', 'area': Decimal('18.0'), 'crop_type': 'wheat',
             'irr_method': 'surface', 'soil_type': 'clay', 'kc_value': Decimal('1.05'),
             'planting_date': None, 'harvest_date': None},
            {'farm': farms[0], 'name': 'Bodring parnik', 'area': Decimal('3.5'), 'crop_type': 'vegetable',
             'irr_method': 'drip', 'soil_type': 'sandy', 'kc_value': Decimal('1.00'),
             'planting_date': None, 'harvest_date': None},
            {'farm': farms[1], 'name': 'Pomidor dala-1', 'area': Decimal('8.0'), 'crop_type': 'vegetable',
             'irr_method': 'drip', 'soil_type': 'loam', 'kc_value': Decimal('1.10'),
             'planting_date': None, 'harvest_date': None},
            {'farm': farms[1], 'name': 'Olma bog\'i', 'area': Decimal('14.0'), 'crop_type': 'fruit',
             'irr_method': 'drip', 'soil_type': 'loam', 'kc_value': Decimal('0.85'),
             'planting_date': None, 'harvest_date': None},
        ]

        fields = []
        for data in fields_data:
            field, created = Field.objects.get_or_create(
                name=data['name'],
                farm=data['farm'],
                defaults={k: v for k, v in data.items() if k not in ('farm', 'name')}
            )
            if created:
                self.stdout.write(f"  OK Dala yaratildi: {field.name}")
            fields.append(field)

        return fields

    def _create_sensors(self, fields):
        from apps.sensors.models import Sensor

        sensors_config = [
            ('soil_moisture', '%', 20, 80),
            ('air_temp', '°C', 5, 45),
        ]

        sensors = []
        sensor_counter = 1

        for field in fields:
            for stype, unit, low, high in sensors_config:
                device_id = f"SNS_{field.pk:02d}_{sensor_counter:03d}"
                sensor, created = Sensor.objects.get_or_create(
                    device_id=device_id,
                    defaults={
                        'field': field,
                        'name': f"{field.name} — {dict(sensors_config)[stype] if False else stype}",
                        'sensor_type': stype,
                        'unit': unit,
                        'status': 'online',
                        'last_seen': timezone.now(),
                        'low_threshold': Decimal(str(low)),
                        'high_threshold': Decimal(str(high)),
                    }
                )
                if created:
                    self.stdout.write(f"    OK Sensor: {device_id}")
                sensors.append(sensor)
                sensor_counter += 1

        return sensors

    def _create_readings(self, sensors):
        from apps.sensors.models import SensorReading

        self.stdout.write("  Sensor o'lchovlari yaratilmoqda (7 kun)...")

        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)

        for sensor in sensors:
            if SensorReading.objects.filter(sensor=sensor).exists():
                continue

            readings = []
            current_time = seven_days_ago

            if sensor.sensor_type == 'soil_moisture':
                value = random.uniform(35, 65)
                while current_time <= now:
                    value += random.uniform(-2, 2)
                    value = max(15, min(85, value))
                    readings.append(SensorReading(
                        sensor=sensor,
                        timestamp=current_time,
                        value=Decimal(str(round(value, 2))),
                        unit=sensor.unit,
                        quality=random.randint(90, 100)
                    ))
                    current_time += timedelta(minutes=5)
            elif sensor.sensor_type == 'air_temp':
                while current_time <= now:
                    hour = current_time.hour
                    base = 28 if 10 <= hour <= 18 else 18
                    value = base + random.uniform(-3, 3)
                    readings.append(SensorReading(
                        sensor=sensor,
                        timestamp=current_time,
                        value=Decimal(str(round(value, 2))),
                        unit=sensor.unit,
                        quality=random.randint(90, 100)
                    ))
                    current_time += timedelta(minutes=10)

            SensorReading.objects.bulk_create(readings, batch_size=500)

        self.stdout.write(f"  OK O'lchovlar yaratildi")

    def _create_schedules(self, fields, created_by):
        from apps.irrigation.models import IrrigationSchedule

        schedules_data = [
            {'field': fields[0], 'name': 'Ertalabki sug\'orish', 'trigger_type': 'time',
             'start_time': time(6, 0), 'days_of_week': [1, 2, 3, 4, 5], 'duration_min': 45},
            {'field': fields[1], 'name': 'Kechki sug\'orish', 'trigger_type': 'time',
             'start_time': time(18, 30), 'days_of_week': [1, 3, 5], 'duration_min': 60},
            {'field': fields[2], 'name': 'Namligi past bo\'lganda', 'trigger_type': 'sensor',
             'start_time': None, 'days_of_week': [], 'duration_min': 30,
             'soil_threshold': Decimal('30.0'), 'target_moisture': Decimal('60.0')},
        ]

        for data in schedules_data:
            IrrigationSchedule.objects.get_or_create(
                name=data['name'],
                field=data['field'],
                defaults={
                    'trigger_type': data['trigger_type'],
                    'start_time': data.get('start_time'),
                    'days_of_week': data.get('days_of_week', []),
                    'duration_min': data['duration_min'],
                    'soil_threshold': data.get('soil_threshold'),
                    'target_moisture': data.get('target_moisture'),
                    'is_active': True,
                    'created_by': created_by,
                }
            )

        self.stdout.write(f"  OK Sug'orish jadvallari yaratildi")

    def _create_events(self, fields, user):
        from apps.irrigation.models import IrrigationEvent

        now = timezone.now()
        trigger_types = ['manual', 'schedule', 'sensor']
        statuses = ['completed', 'completed', 'completed', 'stopped']

        for field in fields[:4]:
            if IrrigationEvent.objects.filter(field=field).exists():
                continue

            for i in range(5):
                started = now - timedelta(days=random.randint(1, 7), hours=random.randint(0, 20))
                duration = random.randint(20, 90)
                ended = started + timedelta(minutes=duration)
                status = random.choice(statuses)

                IrrigationEvent.objects.create(
                    field=field,
                    trigger_type=random.choice(trigger_types),
                    started_at=started,
                    ended_at=ended,
                    duration_min=Decimal(str(duration)),
                    water_liters=Decimal(str(round(duration * random.uniform(15, 25), 1))),
                    status=status,
                    started_by=user,
                )

        self.stdout.write(f"  OK Sug'orish hodisalari yaratildi")

    def _create_alerts(self, fields, sensors):
        from apps.alerts.models import Alert

        if Alert.objects.filter(field__in=fields).exists():
            return

        alerts_data = [
            {
                'field': fields[0],
                'sensor': sensors[0] if sensors else None,
                'alert_type': 'low_moisture',
                'severity': 'warning',
                'message': f"{fields[0].name}: Tuproq namligi past — 22% (chegara: 30%)",
                'value': Decimal('22.0'),
                'threshold': Decimal('30.0'),
                'is_resolved': False,
            },
            {
                'field': fields[1],
                'sensor': None,
                'alert_type': 'device_offline',
                'severity': 'critical',
                'message': f"Sensor ulanishi yo'q: SNS_02_004",
                'is_resolved': True,
            },
            {
                'field': fields[2],
                'sensor': sensors[2] if len(sensors) > 2 else None,
                'alert_type': 'low_moisture',
                'severity': 'info',
                'message': f"{fields[2].name}: Namlik maqsadli darajaga yetdi",
                'value': Decimal('65.0'),
                'is_resolved': True,
            },
        ]

        now = timezone.now()
        for data in alerts_data:
            alert = Alert.objects.create(
                field=data['field'],
                sensor=data.get('sensor'),
                alert_type=data['alert_type'],
                severity=data['severity'],
                message=data['message'],
                value=data.get('value'),
                threshold=data.get('threshold'),
                is_resolved=data.get('is_resolved', False),
                resolved_at=now if data.get('is_resolved') else None,
            )

        self.stdout.write(f"  OK Ogohlantirishlar yaratildi")
