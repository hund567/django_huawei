import django
import manage
try:
   manage.execute_from_command_line('runserver')
finally:
    print 'a'