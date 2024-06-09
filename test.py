from quart import Quart, request
app = Quart(__name__)
@app.route('/chat', methods=['POST',"GET"])
async def chat():
   data = await request.get_json()
   return {'response': 'Hello, World'}
if __name__ == '__main__':
   app.run()