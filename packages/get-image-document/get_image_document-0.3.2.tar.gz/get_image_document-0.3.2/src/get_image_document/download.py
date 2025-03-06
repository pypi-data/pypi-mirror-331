import requests
import random
import datetime
import os

sizes = [200, 300, 400, 500, 600, 900, 1000]
save_dir = "./temp"

os.makedirs(save_dir, exist_ok=True)

for i in range(100):
    width = random.choice(sizes)
    height = random.choice(sizes)
    timestamp = datetime.datetime.now().strftime('%S%f') 
    filename = f"{save_dir}/image_{i+1}_{width}x{height}_{timestamp}.jpg"
    
    url = f"https://picsum.photos/{width}/{height}?random=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download image {i+1}")
