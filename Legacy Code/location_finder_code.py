import googlemaps
from typing import List, Dict
import os
from dotenv import load_dotenv

class LocationFinder:
    def __init__(self, api_key: str):
        self.gmaps = googlemaps.Client(key=api_key)

    def find_closest_locations(self, region: str, location_types: List[str]) -> List[Dict]:
        """Find closest pairs of locations"""
        # Get locations of each type
        all_locations = {}
        for loc_type in location_types:
            print(f"Searching for {loc_type}...")
            result = self.gmaps.places(
                loc_type,
                location=self.get_region_center(region),
                region=region
            )
            all_locations[loc_type] = result.get('results', [])

        # Calculate distances between pairs
        pairs = []
        for i, loc1_type in enumerate(location_types[:-1]):
            for loc2_type in location_types[i+1:]:
                for loc1 in all_locations[loc1_type]:
                    for loc2 in all_locations[loc2_type]:
                        distance_result = self.gmaps.distance_matrix(
                            origins=[(loc1['geometry']['location']['lat'], 
                                    loc1['geometry']['location']['lng'])],
                            destinations=[(loc2['geometry']['location']['lat'], 
                                        loc2['geometry']['location']['lng'])],
                            mode="driving"
                        )
                        
                        if distance_result['rows'][0]['elements'][0]['status'] == 'OK':
                            distance = distance_result['rows'][0]['elements'][0]['distance']['value']
                            pairs.append({
                                'location1': {
                                    'name': loc1['name'],
                                    'address': loc1.get('formatted_address', 'Address not available'),
                                    'type': loc1_type
                                },
                                'location2': {
                                    'name': loc2['name'],
                                    'address': loc2.get('formatted_address', 'Address not available'),
                                    'type': loc2_type
                                },
                                'distance': distance
                            })

        # Sort by distance and return top 3
        pairs.sort(key=lambda x: x['distance'])
        return pairs[:3]

    def get_region_center(self, region: str) -> tuple:
        """Get the center coordinates of a region"""
        geocode_result = self.gmaps.geocode(region)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return (location['lat'], location['lng'])
        return (0, 0)

def main():
    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        print("Error: Google Maps API key not found!")
        print("Please create a .env file with your API key.")
        return

    finder = LocationFinder(api_key)

    # Get user input
    print("\n=== Location Finder ===")
    region = input("\nEnter the region (e.g., 'Kadiyam Mandal'): ")
    
    print("\nEnter location types (e.g., 'Sai Baba Temple', 'Medical Store')")
    print("Press Enter twice when done")
    
    location_types = []
    while True:
        loc_type = input("Enter location type (or press Enter to finish): ")
        if not loc_type:
            break
        location_types.append(loc_type)

    if len(location_types) < 2:
        print("Error: Please enter at least 2 location types!")
        return

    print("\nSearching for closest locations...")
    pairs = finder.find_closest_locations(region, location_types)

    # Display results
    print("\n=== Results ===")
    if not pairs:
        print("No results found!")
    else:
        for i, pair in enumerate(pairs, 1):
            print(f"\nPair {i}:")
            print(f"{pair['location1']['type']}: {pair['location1']['name']}")
            print(f"Address: {pair['location1']['address']}")
            print(f"\n{pair['location2']['type']}: {pair['location2']['name']}")
            print(f"Address: {pair['location2']['address']}")
            print(f"Distance: {pair['distance']/1000:.2f} km")

if __name__ == "__main__":
    main()