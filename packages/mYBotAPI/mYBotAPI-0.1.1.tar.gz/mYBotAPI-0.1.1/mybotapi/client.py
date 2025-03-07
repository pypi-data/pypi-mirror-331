# mybot/client.py

class Client:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def ask_ai(self, model, messages):
        import requests
        import json
        
        url = "https://mYBot.yb-tech.de/api/askAI"
        params = {
            'model': model,
            'messages': json.dumps(messages),
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.json().get('error', 'Unknown error occurred'))

