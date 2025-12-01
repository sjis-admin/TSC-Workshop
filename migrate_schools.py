
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workshop_registration.settings')
django.setup()

from workshops.models import Registration, School

def migrate_schools():
    print("Starting data migration...")
    count = 0
    for reg in Registration.objects.all():
        if reg.school_name:
            school, created = School.objects.get_or_create(name=reg.school_name)
            reg.school = school
            reg.save()
            count += 1
            print(f"Migrated registration {reg.id}: {reg.school_name} -> {school.name}")
    
    print(f"Migration complete. Updated {count} registrations.")

if __name__ == '__main__':
    migrate_schools()
