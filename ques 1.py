from flask import Flask, request, jsonify
import asyncio
import aiohttp

app = Flask(__name__)

async def fetch_number_data(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
    return None

async def fetch_all_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_number_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [result for result in results if not isinstance(result, Exception)]

@app.route('/numbers', methods=['GET'])
async def get_numbers():
    urls = request.args.getlist('url')

    if not urls:
        return jsonify({"error": "No URLs provided."}), 400

    try:
        results = await asyncio.wait_for(fetch_all_urls(urls), timeout=0.5)
    except asyncio.TimeoutError:
        return jsonify({"error": "Request timed out."}), 500

    merged_numbers = sorted(set(num for result in results for num in result.get("numbers", [])))

    return jsonify({"numbers": merged_numbers}), 200

if __name__ == '__main__':
    app.run(port=8008)
