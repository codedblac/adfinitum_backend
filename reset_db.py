import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
APPS = ["accounts"]  # Add more apps if needed

def delete_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Deleted db.sqlite3")

def delete_migrations():
    for app in APPS:
        migrations_dir = os.path.join(BASE_DIR, app, "migrations")
        if os.path.exists(migrations_dir):
            for file in os.listdir(migrations_dir):
                path = os.path.join(migrations_dir, file)
                if file != "__init__.py":
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)  # removes __pycache__ folders
            print(f"🗑️ Deleted migrations for {app}")

def run_migrations():
    os.system("python manage.py makemigrations")
    os.system("python manage.py migrate")

if __name__ == "__main__":
    delete_db()
    delete_migrations()
    run_migrations()
    print("🎉 Reset complete. Now run:")
    print("   python manage.py createsuperuser")
