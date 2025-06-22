# ratings_simulator.py
import csv
import random
import time

RATINGS_FILE = "ratings.csv"

def simulate_rating():
    movie_ids = list(range(1, 1000))  # Assuming movie_id from 1 to 1000
    while True:
        movie_id = random.choice(movie_ids)
        rating = round(random.uniform(3.0, 10.0), 1)
        timestamp = int(time.time())
        
        with open(RATINGS_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([movie_id, rating, timestamp])
        
        print(f"Rated movie {movie_id} with {rating}")
        time.sleep(2)  # Wait before generating next rating

if __name__ == "__main__":
    print("Simulating real-time movie ratings... Press Ctrl+C to stop.")
    simulate_rating()
