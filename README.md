[![Build Status](https://travis-ci.org/griffithlab/civic-api-client.svg?branch=master)](https://travis-ci.org/griffithlab/civic-api-client)

# civic-api-client
Example tools using the CIVIC API. Very basic docs on using the API is
[here](https://civic.genome.wustl.edu/#/api-documentation). The schemas
can be viewed [here](https://github.com/genome/civic-server/blob/deploy/db/schema.rb)

##Setup
Install like any other Python package, I like using the Virtualenv setup.
``` bash
git clone https://github.com/griffithlab/civic-api-client
cd civic-api-client
virtualenv myenv && source myenv/bin/activate
pip install .
```

##Usage
Very basic functionality for now
To output variants to the screen(including variants with no co-ordinates):
```
civic-api-client  variants-list --no-coords
```
To output variants to a web-view(query variants from first 10 genes):
```
civic-api-client  variants-list --no-coords --max-gene-count 10 --web
```

To list the evidence-items with an invalid DOID
```
civic-api-client evidence-items-list --doid --max-gene-count 10 --web
```
