import os
from dotenv import load_dotenv
load_dotenv()
print('Env var:', os.getenv('GROQ_API_KEY'))
