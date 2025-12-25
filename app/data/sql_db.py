import sqlite3
import os

# Chemin vers le fichier physique de la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), "banque.sqlite")

def get_db_connection():
    """Crée une connexion thread-safe à la base SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_banking_data():
    """Initialise la base avec des données factices."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comptes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            solde REAL NOT NULL,
            type_compte TEXT NOT NULL,
            devise TEXT DEFAULT 'EUR'
        )
    ''')
    
    # Reset des données pour le test
    cursor.execute("DELETE FROM comptes")
    
    donnees_test = [
        ('Alice', 2500.50, 'Compte Courant', 'EUR'),
        ('Alice', 12000.00, 'Livret A', 'EUR'),
        ('Bob', -150.00, 'Compte Courant', 'EUR')
    ]
    
    cursor.executemany(
        "INSERT INTO comptes (client_name, solde, type_compte, devise) VALUES (?, ?, ?, ?)", 
        donnees_test
    )
    
    conn.commit()
    conn.close()
    print(f"✅ Base SQL initialisée : {DB_PATH}")

if __name__ == "__main__":
    init_banking_data()