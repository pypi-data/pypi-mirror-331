import requests

class CopilotClient:
	def __init__(self, base_url="http://localhost:3000"):
		"""
		Initialize the Copilot API client
		
		Args:
			base_url (str): The base URL of the Copilot API server
		"""
		self.base_url = base_url

	def list_models(self):
		"""
		List available Copilot models
		
		Returns:
			list: List of available models
		"""
		response = requests.get(f"{self.base_url}/models")
		response.raise_for_status()
		return response.json()["models"]

	def chat(self, message, history=None, vendor=None, family=None):
		"""
		Send a chat message and get a complete response
		
		Args:
			message (str): The message to send
			history (list, optional): List of previous chat messages
			vendor (str, optional): The model vendor (e.g. 'copilot')
			family (str, optional): The model family (e.g. 'gpt-4o')
			
		Returns:
			str: The response from Copilot
		"""
		data = {
			"message": message,
			"history": history or [],
			"vendor": vendor,
			"family": family
		}
		
		response = requests.post(
			f"{self.base_url}/chat",
			json=data
		)
		response.raise_for_status()
		return response.json()["response"]
    
	def chat_stream(self, message, history=None, vendor=None, family=None):
		"""
		Send a chat message and get a streaming response
		
		Args:
			message (str): The message to send
			history (list, optional): List of previous chat messages
			vendor (str, optional): The model vendor (e.g. 'copilot')
			family (str, optional): The model family (e.g. 'gpt-4o')
				
		Returns:
			generator: A generator yielding response fragments as they arrive
		"""
		import json
		
		data = {
			"message": message,
			"history": history or [],
			"vendor": vendor,
			"family": family
		}
		
		headers = {
			'Accept': 'text/event-stream',
			'Content-Type': 'application/json',
			'Cache-Control': 'no-cache'
		}
		
		response = requests.post(
			f"{self.base_url}/chat/stream",
			json=data,
			headers=headers,
			stream=True
		)
		response.raise_for_status()

		for line in response.iter_lines(decode_unicode=True):
			if not line:
				continue
				
			if line.startswith('data: '):
				try:
					event_data = json.loads(line[6:])
					
					if 'fragment' in event_data:
						yield event_data['fragment']
						
					if 'done' in event_data and event_data['done']:
						break
						
					if 'error' in event_data:
						raise Exception(f"Stream error: {event_data['error']}")
				except json.JSONDecodeError as e:
					print(f"JSON parsing error: {e}, data: {line[6:]}")