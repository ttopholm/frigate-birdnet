import requests
from bs4 import BeautifulSoup
from models.ebird import Birds
import argparse



def load_localized_birds(ebird_api_token, locale, country):
    print('Fetching locale names and images')
    r = requests.get(f'https://api.ebird.org/v2/product/spplist/{country}', headers={
        'X-Ebirdapitoken': ebird_api_token
    })
    species = ",".join(r.json())

    r = requests.get('https://api.ebird.org/v2/ref/taxonomy/ebird', headers={
        'X-Ebirdapitoken': ebird_api_token
    }, params={
        'species': species,
        'locale': locale,
        'fmt': 'json'
    })
    birds = Birds.model_validate_json(r.text)

    for bird in birds:
        bird_request = requests.get(f'https://ebird.org/species/{bird.speciesCode}', headers={
            'X-Ebirdapitoken': ebird_api_token
        })
        soup = BeautifulSoup(bird_request.content, "html.parser")
        
        image = soup.find("meta", property="og:image")
        bird.image = image.get('content')

    with open('./labels/ebird_taxonomy.json', 'w') as f:
        f.write(birds.model_dump_json())
    print('Fetched all images')
    return birds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to generate ebird taxonomy json including image urls"
    )
    parser.add_argument("--ebird-api-token", required=True, type=str, help="The token for ebird api" )
    parser.add_argument("--locale", required=True, type=str, help="Locale for the language you want the taxonomy in.")
    parser.add_argument("--country", required=True, type=str, help="Which country you are in, used for only selecting the country, can also use region code")
    args = parser.parse_args()
    load_localized_birds(args.ebird-api-token, args.locale, args.country)