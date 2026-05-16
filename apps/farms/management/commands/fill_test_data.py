"""
To'liq test ma'lumotlari yaratish buyrug'i.
Ishlatish: python manage.py fill_test_data
Mavjud ma'lumotlarga qo'shimcha qiladi.
"""
import random
from datetime import timedelta, time as dtime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Qo'shimcha test ma'lumotlari yaratish"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Test ma'lumotlari yaratilmoqda..."))
        farmer = User.objects.filter(username='farmer').first()
        if not farmer:
            self.stdout.write(self.style.ERROR("Avval create_demo_data ni ishga tushiring!"))
            return

        farms = self._create_extra_farms(farmer)
        fields = self._create_extra_fields(farms)
        sensors = self._create_extra_sensors(fields)
        self._create_readings(sensors)
        self._create_extra_schedules(fields, farmer)
        self._create_extra_events(fields, farmer)
        self._create_extra_alerts(fields, sensors)
        self._create_active_irrigation(fields, farmer)

        self.stdout.write(self.style.SUCCESS("\nOK Barcha test ma'lumotlari yaratildi!"))
        from apps.farms.models import Farm, Field
        from apps.sensors.models import Sensor, SensorReading
        from apps.irrigation.models import IrrigationEvent
        from apps.alerts.models import Alert
        self.stdout.write(f"  Fermalar: {Farm.objects.count()}")
        self.stdout.write(f"  Dalalar:  {Field.objects.count()}")
        self.stdout.write(f"  Sensorlar: {Sensor.objects.count()}")
        self.stdout.write(f"  O'lchovlar: {SensorReading.objects.count()}")
        self.stdout.write(f"  Sug'orish hodisalari: {IrrigationEvent.objects.count()}")
        self.stdout.write(f"  Ogohlantirishlar: {Alert.objects.count()}")

    def _create_extra_farms(self, owner):
        from apps.farms.models import Farm
        farms_data = [
            {
                'name': "Samarqand Uzum Fermasi",
                'region': 'samarkand',
                'district': "Urgut tumani",
                'lat': Decimal('39.4035'),
                'lon': Decimal('67.2567'),
                'total_area': Decimal('60.00'),
                'description': "Samarqand viloyatidagi uzumchilik fermasi",
            },
            {
                'name': "Farg'ona Sholi Fermasi",
                'region': 'fergana',
                'district': "Bag'dod tumani",
                'lat': Decimal('40.3891'),
                'lon': Decimal('71.7864'),
                'total_area': Decimal('80.50'),
                'description': "Farg'ona vodiysidagi sholi fermasi",
            },
            {
                'name': "Namangan Meva Bog'i",
                'region': 'namangan',
                'district': "Chortoq tumani",
                'lat': Decimal('41.0121'),
                'lon': Decimal('71.6453'),
                'total_area': Decimal('42.00'),
                'description': "Namangan viloyatidagi poliz va meva fermasi",
            },
        ]
        farms = []
        for data in farms_data:
            farm, created = Farm.objects.get_or_create(
                name=data['name'], owner=owner, defaults=data
            )
            if created:
                self.stdout.write(f"  + Ferma: {farm.name}")
            farms.append(farm)
        return farms

    def _create_extra_fields(self, farms):
        from apps.farms.models import Field
        fields_config = [
            # Samarqand Uzum Fermasi
            (farms[0], "Qora uzum parsel-1", Decimal('15.0'), 'fruit', 'drip', 'loam', Decimal('0.90')),
            (farms[0], "Qizil uzum parsel-2", Decimal('20.0'), 'fruit', 'drip', 'loam', Decimal('0.85')),
            (farms[0], "Gilos bog'i", Decimal('10.0'), 'fruit', 'drip', 'clay', Decimal('0.80')),
            (farms[0], "O'rik parsel", Decimal('15.0'), 'fruit', 'sprinkler', 'loam', Decimal('0.75')),
            # Farg'ona Sholi Fermasi
            (farms[1], "Asosiy sholi dala", Decimal('35.0'), 'rice', 'surface', 'clay', Decimal('1.20')),
            (farms[1], "Sholi-2 dala", Decimal('28.0'), 'rice', 'surface', 'clay', Decimal('1.20')),
            (farms[1], "Makkajo'xori dala", Decimal('17.5'), 'corn', 'sprinkler', 'loam', Decimal('1.10')),
            # Namangan Meva Bog'i
            (farms[2], "Qovun poliz", Decimal('8.0'), 'vegetable', 'drip', 'sandy', Decimal('0.95')),
            (farms[2], "Tarvuz poliz", Decimal('10.0'), 'vegetable', 'drip', 'sandy', Decimal('0.95')),
            (farms[2], "Olcha bog'i", Decimal('12.0'), 'fruit', 'drip', 'loam', Decimal('0.70')),
            (farms[2], "Nok bog'i", Decimal('12.0'), 'fruit', 'drip', 'loam', Decimal('0.80')),
        ]
        fields = []
        for farm, name, area, crop, irr, soil, kc in fields_config:
            field, created = Field.objects.get_or_create(
                name=name, farm=farm,
                defaults={
                    'area': area, 'crop_type': crop, 'irr_method': irr,
                    'soil_type': soil, 'kc_value': kc,
                }
            )
            if created:
                self.stdout.write(f"  + Dala: {field.name}")
            fields.append(field)
        return fields

    def _create_extra_sensors(self, fields):
        from apps.sensors.models import Sensor
        sensor_types = [
            ('soil_moisture', '%', 20, 80),
            ('air_temp', '°C', 5, 45),
            ('air_humidity', '%', 20, 95),
            ('flow_meter', 'L/min', 0, 100),
        ]
        sensors = []
        for field in fields:
            for stype, unit, low, high in sensor_types:
                device_id = f"EXT_{field.pk}_{stype[:4].upper()}"
                sensor, created = Sensor.objects.get_or_create(
                    device_id=device_id,
                    defaults={
                        'field': field,
                        'name': f"{field.name} — {stype}",
                        'sensor_type': stype,
                        'unit': unit,
                        'status': random.choice(['online', 'online', 'online', 'offline']),
                        'last_seen': timezone.now() - timedelta(minutes=random.randint(0, 60)),
                        'low_threshold': Decimal(str(low)),
                        'high_threshold': Decimal(str(high)),
                    }
                )
                if created:
                    self.stdout.write(f"    + Sensor: {device_id}")
                sensors.append(sensor)
        return sensors

    def _create_readings(self, sensors):
        from apps.sensors.models import SensorReading
        self.stdout.write("  Sensor o'lchovlari yaratilmoqda (14 kun)...")
        now = timezone.now()
        start = now - timedelta(days=14)

        for sensor in sensors:
            if SensorReading.objects.filter(sensor=sensor).count() > 100:
                continue

            readings = []
            t = start
            if sensor.sensor_type == 'soil_moisture':
                v = random.uniform(35, 65)
                while t <= now:
                    v += random.uniform(-2, 2)
                    v = max(15, min(85, v))
                    readings.append(SensorReading(
                        sensor=sensor, timestamp=t,
                        value=Decimal(str(round(v, 2))), unit=sensor.unit,
                        quality=random.randint(88, 100)
                    ))
                    t += timedelta(minutes=5)

            elif sensor.sensor_type == 'air_temp':
                while t <= now:
                    h = t.hour
                    base = 30 if 11 <= h <= 17 else 17
                    v = base + random.uniform(-4, 4)
                    readings.append(SensorReading(
                        sensor=sensor, timestamp=t,
                        value=Decimal(str(round(v, 2))), unit=sensor.unit,
                        quality=random.randint(90, 100)
                    ))
                    t += timedelta(minutes=10)

            elif sensor.sensor_type == 'air_humidity':
                v = random.uniform(40, 70)
                while t <= now:
                    h = t.hour
                    v += random.uniform(-3, 3)
                    v = max(20, min(95, v))
                    readings.append(SensorReading(
                        sensor=sensor, timestamp=t,
                        value=Decimal(str(round(v, 2))), unit=sensor.unit,
                        quality=random.randint(85, 100)
                    ))
                    t += timedelta(minutes=15)

            elif sensor.sensor_type == 'flow_meter':
                while t <= now:
                    # Flow only during typical irrigation hours
                    h = t.hour
                    if 6 <= h <= 8 or 18 <= h <= 20:
                        v = round(random.uniform(20, 60), 2)
                    else:
                        v = 0.0
                    readings.append(SensorReading(
                        sensor=sensor, timestamp=t,
                        value=Decimal(str(v)), unit=sensor.unit,
                        quality=random.randint(90, 100)
                    ))
                    t += timedelta(minutes=10)

            if readings:
                SensorReading.objects.bulk_create(readings, batch_size=500)

        self.stdout.write("  OK O'lchovlar yaratildi")

    def _create_extra_schedules(self, fields, user):
        from apps.irrigation.models import IrrigationSchedule
        schedules = [
            (fields[0],  "Uzum — ertalab",  'time', dtime(5, 30),  [1,2,3,4,5,6,7], 60),
            (fields[1],  "Uzum-2 — kechki", 'time', dtime(19, 0),  [1,3,5,7],       45),
            (fields[4],  "Sholi — kunduz",  'time', dtime(10, 0),  [1,2,3,4,5],     90),
            (fields[5],  "Sholi-2 — ertalab",'time', dtime(6, 0),  [2,4,6],         90),
            (fields[7],  "Qovun — sensor",  'sensor', None,        [],              30),
            (fields[8],  "Tarvuz — sensor", 'sensor', None,        [],              35),
            (fields[9],  "Olcha — ertalab", 'time', dtime(7, 0),   [1,3,5],         40),
            (fields[10], "Nok — kechki",    'time', dtime(20, 0),  [2,4,6],         40),
        ]
        for field, name, ttype, stime, days, dur in schedules:
            IrrigationSchedule.objects.get_or_create(
                name=name, field=field,
                defaults={
                    'trigger_type': ttype,
                    'start_time': stime,
                    'days_of_week': days,
                    'duration_min': dur,
                    'soil_threshold': Decimal('30.0') if ttype == 'sensor' else None,
                    'target_moisture': Decimal('65.0') if ttype == 'sensor' else None,
                    'is_active': True,
                    'created_by': user,
                }
            )
        self.stdout.write("  OK Jadvallar yaratildi")

    def _create_extra_events(self, fields, user):
        from apps.irrigation.models import IrrigationEvent
        now = timezone.now()
        triggers = ['manual', 'schedule', 'schedule', 'sensor']
        statuses = ['completed', 'completed', 'completed', 'stopped']

        for field in fields:
            if IrrigationEvent.objects.filter(field=field).count() >= 5:
                continue
            count = random.randint(4, 8)
            for i in range(count):
                started = now - timedelta(days=random.randint(1, 14),
                                          hours=random.randint(0, 22))
                dur = random.randint(20, 120)
                IrrigationEvent.objects.create(
                    field=field,
                    trigger_type=random.choice(triggers),
                    started_at=started,
                    ended_at=started + timedelta(minutes=dur),
                    duration_min=Decimal(str(dur)),
                    water_liters=Decimal(str(round(dur * random.uniform(12, 28), 1))),
                    status=random.choice(statuses),
                    started_by=user,
                )
        self.stdout.write("  OK Sug'orish hodisalari yaratildi")

    def _create_active_irrigation(self, fields, user):
        """Hozir aktiv sug'orilayotgan dalalar."""
        from apps.irrigation.models import IrrigationEvent
        from apps.farms.models import Field as FField
        now = timezone.now()

        # Get a couple of extra fields from DB too
        active_fields = list(FField.objects.exclude(
            events__status='irrigating'
        ).order_by('?')[:3])

        for field in active_fields:
            started = now - timedelta(minutes=random.randint(5, 40))
            IrrigationEvent.objects.create(
                field=field,
                trigger_type='schedule',
                started_at=started,
                ended_at=None,
                duration_min=Decimal(str(random.randint(30, 90))),
                water_liters=Decimal('0'),
                status='irrigating',
                started_by=user,
            )
        self.stdout.write(f"  OK {len(active_fields)} ta dala aktiv sug'orish holatida")

    def _create_extra_alerts(self, fields, sensors):
        from apps.alerts.models import Alert
        now = timezone.now()
        alerts_data = [
            ('low_moisture',  'critical', fields[0],  sensors[0] if sensors else None,
             "Uzum parsel-1: Tuproq namligi juda past — 18% (chegara: 20%)",
             Decimal('18.0'), Decimal('20.0'), False),
            ('high_temp',     'warning',  fields[1],  sensors[4] if len(sensors) > 4 else None,
             "Uzum parsel-2: Harorat yuqori — 42°C (chegara: 40°C)",
             Decimal('42.0'), Decimal('40.0'), False),
            ('low_moisture',  'warning',  fields[4],  None,
             "Sholi dala: Namlik past — 25%",
             Decimal('25.0'), Decimal('30.0'), False),
            ('device_offline','critical', fields[2],  sensors[8] if len(sensors) > 8 else None,
             "Sensor ulanishi yo'q: Gilos bog'i flow_meter",
             None, None, False),
            ('high_moisture', 'info',     fields[5],  None,
             "Sholi-2: Namlik yuqori — 82% (cho'l xavfi)",
             Decimal('82.0'), Decimal('80.0'), False),
            ('low_moisture',  'warning',  fields[7],  None,
             "Qovun poliz: Namlik chegara yaqin — 32%",
             Decimal('32.0'), Decimal('30.0'), True),
            ('device_offline','warning',  fields[9],  None,
             "Olcha bog'i: Sensor 2 soatdan beri javob bermayapti",
             None, None, True),
            ('high_temp',     'info',     fields[10], None,
             "Nok bog'i: Harorat normalga qaytdi",
             Decimal('25.0'), Decimal('38.0'), True),
        ]
        for atype, severity, field, sensor, msg, val, thr, resolved in alerts_data:
            Alert.objects.get_or_create(
                field=field, alert_type=atype, message=msg,
                defaults={
                    'sensor': sensor,
                    'severity': severity,
                    'value': val,
                    'threshold': thr,
                    'is_resolved': resolved,
                    'resolved_at': now if resolved else None,
                }
            )
        self.stdout.write("  OK Ogohlantirishlar yaratildi")
