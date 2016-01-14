import requests
import json

'''
r = requests.get("https://civic.genome.wustl.edu/api/genes/1/variants")
for variant in  r.json():
    print "c1", variant['coordinates']['chromosome'], variant['coordinates']['start'], variant['coordinates']['stop']
    print "c2", variant['coordinates']['chromosome2'], variant['coordinates']['start2'], variant['coordinates']['stop2']
'''

url = 'https://civic.genome.wustl.edu/api/genes?count=100000'
resp = sorted(requests.get(url).json(), key=lambda key: int(key['id']))
done_variant_id = []
for gene in resp:
    for variant in gene['variants']:
        variant_name = variant['name']
        variant_id = variant['id']
        if variant_id in done_variant_id:
            continue
        done_variant_id.append(variant_id)
        variant_url = 'https://civic.genome.wustl.edu/api/variants/' + str(variant_id)
        variant_details = requests.get(variant_url).json()
        print variant_name
        if 'coordinates' in variant_details:
            print "c1", variant_details['coordinates']['chromosome'], variant_details['coordinates']['start'], variant_details['coordinates']['stop']
            print "c2", variant_details['coordinates']['chromosome2'], variant_details['coordinates']['start2'], variant_details['coordinates']['stop2']
        else:
            print "coordinates unavailable: ", variant_name, variant_id
