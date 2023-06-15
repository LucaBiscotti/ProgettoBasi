from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from routes import app, db  # Importa l'istanza di Flask e il database SQLAlchemy dal tuo modulo principale

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
