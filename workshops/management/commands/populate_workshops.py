from django.core.management.base import BaseCommand
from workshops.models import Workshop


class Command(BaseCommand):
    help = 'Populate database with Titanium Science Club workshops'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Clearing existing workshops...'))
        Workshop.objects.all().delete()
        
        self.stdout.write(self.style.WARNING('Creating workshops...'))
        
        # Workshop 1: PROJECT DISPLAY & PRESENTATION
        workshop1 = Workshop.objects.create(
            name='PROJECT DISPLAY & PRESENTATION Workshop',
            description='Showcase your innovative projects and present them to judges and peers. '
                       'This workshop provides a platform for students to demonstrate their creativity, '
                       'critical thinking, and problem-solving skills through hands-on projects. '
                       'Participants will receive feedback and guidance from experienced mentors.',
            workshop_date='10 & 11 December 2025',
            venue='New building, St Joseph International School',
            time='10:30 AM - 1:30 PM',
            duration='3 hours per day',
            fee=200.00,
            capacity=100,
            is_active=True,
            organizer='Titanium Science Club'
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Created: {workshop1.name}'))
        
        # Workshop 2: PHYSICS OLYMPIAD
        workshop2 = Workshop.objects.create(
            name='PHYSICS OLYMPIAD Workshop',
            description='Prepare for Physics Olympiad competitions with expert guidance from national coaches. '
                       'This intensive workshop covers advanced physics concepts, problem-solving strategies, '
                       'and competition techniques. Perfect for students passionate about physics and looking '
                       'to compete at national and international levels.',
            workshop_date='Saturday, 13 December 2025',
            venue='New building, St Joseph International School',
            time='9:45 AM - 12:30 PM',
            duration='2 hours 45 minutes',
            fee=0.00,
            capacity=150,
            is_active=True,
            organizer='Fayez Ahmed Jahangir Masud, General Secretary & Dr Arshad Momen, National Coach, BDPhO'
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Created: {workshop2.name}'))
        
        # Workshop 3: ARDUINO ROBOTICS BOOTCAMP
        workshop3 = Workshop.objects.create(
            name='ARDUINO ROBOTICS BOOTCAMP',
            description='Learn the fundamentals of robotics and programming with Arduino! '
                       'This hands-on bootcamp covers Arduino basics, sensor integration, motor control, '
                       'and building autonomous robots. Students will work on real projects and gain '
                       'practical experience in electronics and programming. No prior experience required!',
            workshop_date='Monday, 15 December 2025 & Wednesday, 17 December 2025',
            venue='New building, St Joseph International School',
            time='9:45 AM - 12:30 PM',
            duration='2 hours 45 minutes per day',
            fee=0.00,
            capacity=120,
            is_active=True,
            organizer='2 teams from Zan Tech'
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Created: {workshop3.name}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Successfully created 3 workshops!'))
        self.stdout.write(self.style.SUCCESS('✓ Project Display Workshop: ৳200 (Paid)'))
        self.stdout.write(self.style.SUCCESS('✓ Physics Olympiad Workshop: FREE'))
        self.stdout.write(self.style.SUCCESS('✓ Arduino Robotics Bootcamp: FREE'))
