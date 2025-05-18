import subprocess
import threading

def run_script(command, directory):
    try:
        result = subprocess.run(command, cwd=directory, check=True, text=True, shell=True, capture_output=True)
        print(f"Выполнена команда в {directory}: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды {command} в директории {directory}: {e}")
        print(e.stderr)

def run_django():
    run_script('python manage.py runserver 192.168.56.1:8000', 'tg_bot')


def run_bot():
    run_script('python bot.py', 'real_bot')


if __name__ == "__main__":
    django_thread = threading.Thread(target=run_django)
    bot_thread = threading.Thread(target=run_bot)

    django_thread.start()
    print("сервер джанго запущен 192.168.56.1:8000")
    bot_thread.start()
    print("бот запущен")