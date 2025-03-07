mYBot
=====

mYBotAPI ist ein einfaches Python-Modul, das es dir ermöglicht, bequem mit einer KI-API zu kommunizieren. Mit nur wenigen Zeilen Code kannst du Abfragen an die API stellen und Antworten erhalten.

Inhaltsverzeichnis
------------------

Installation
------------

Um mYBot zu verwenden, benötigst du Python und `pip`. Stelle sicher, dass du beide installiert hast.

1.  Installiere das Modul mit dem folgenden Befehl:
    
```undefined
        pip install mYBotAPI
```
    

Benutzung
---------

Um mYBot zu verwenden, importiere das Modul und erstelle eine Instanz des `Client`\-Objekts mit deinem API-Schlüssel.

### Schritt 1: API-Schlüssel erhalten

Du benötigst einen gültigen API-Schlüssel, um auf die KI-API zugreifen zu können. Stelle sicher, dass du einen Schlüssel hast, bevor du fortfährst.

### Schritt 2: Erstelle einen Client

Hier ist ein einfaches Beispiel, wie du den Client einrichtest und eine Anfrage an die KI-API sendest:

### Beispiel
```python
    from mybotapi import Client
    
    # Ersetze 'DEIN_API_KEY' mit deinem tatsächlichen API-Schlüssel
    client = Client(api_key='DEIN_API_KEY')
    
    # Definiere das Modell und die Nachrichten    
    model = 'gpt-4o-mini'
    messages = [{"role": "user", "content": "Hello my friend!"}]
    
    # Frage die KI-API
    try:
        response = client.ask_ai(model=model, messages=messages)
        print(response['content'])
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
```

Fehlerbehandlung
----------------

Wenn beim Abrufen der Antwort von der API ein Fehler auftritt (z. B. ungültiger API-Schlüssel oder ungültige Nachrichten), wird eine Ausnahme ausgelöst. Stelle sicher, dass du diese Fehler abfängst und angemessen behandelst.

Verfügbare Fehlermeldungen sind z.B.:

*   **Ungültiger API-Schlüssel**: Stelle sicher, dass dein API-Schlüssel korrekt ist.
*   **Fehler bei der Generierung von Inhalten**: Es kann sich um ein Problem mit der API handeln.
