[![Build Status](https://travis-ci.org/griffithlab/civic-api-client.svg?branch=master)](https://travis-ci.org/griffithlab/civic-api-client)

# civic-api-client
Example tools using the CIVIC API. Very basic docs on using the API is
[here](https://civic.genome.wustl.edu/#/api-documentation). The schemas
can be viewed [here](https://github.com/genome/civic-server/blob/deploy/db/schema.rb)

##Dependencies
```
brew install wget
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo pip install virtualenv
```

##Setup
Install like any other Python package, I like using the Virtualenv setup.
``` bash
git clone https://github.com/griffithlab/civic-api-client
cd civic-api-client
virtualenv myenv 
#virtualenv myenv --python=python2.7 #if you have problems with your python version
source myenv/bin/activate
pip install .
```

To deactivate the virtual environment,
```
deactivate
```

##Usage
Command options:
1. variants-list
2. evidence-items-list
3. action-items-web-view
4. tsv-create

1. List variants errors
Basic usage (check for all variants and print out all errors):
```
civic-api-client variants-list
```
Error type can be specified, for example:
```
civic-api-client variants-list --wrong-base
```
Command above will print variants where ref/var base is not in [A,C,G,T,N,None]
For more error types, see help manu with following command:
```
civic-api-client variants-list -h
```
2. List evidence errors
Basic usage (check for all evidence and print out all errors):
```
civic-api-client evidence-items-list
```
Error type can be specified, for example, search for missing drug items:
Print out on screen(All types):
```
civic-api-client evidence-items-list --drug 
```
Specify evidence types and print on web page(Predictive,for example):
```
civic-api-client evidence-items-list --drug --evi-type Predictive --web
```
For more error types, see help manu with following command:
```
civic-api-client evidence-items-list -h
```
3. Check for variants or evidences errors on web
Basic functionality for now, this will run a web-server on
http://127.0.0.1:5000/ , this page will list the items that need work.
```
civic-api-client action-items-web-view
```
Can also be done by following command:
```
civic-api-client variants-list --web
```
```
civic-api-client evidence-items-list --web
```
4. Export all evidence items as tsv file 
```
civic-api-client tsv-create
```

##Development
To contribute to the code for this project, please fork the repo and submit a pull request.

To test your own changes (after editing code) you can rebuild the package as follows:
```
pip install . --upgrade
```

To install the latest changes
```
git pull 
pip install . --upgrade
```

### Git repositories related to the CIViC project
The CIViC source code and application are organized in a client-server model. The backend code is available in the [civic-server repository](https://github.com/genome/civic-server) and frontend code is available in the [civic-client repository](https://github.com/genome/civic-client). Issues relating to curation are tracked in the [civic-curation repository](https://github.com/genome/civic-curation). An example of a Python client is available in the [civic-api-client repository](https://github.com/griffithlab/civic-api-client). Issues relating to public CIViC meetings are tracked in the [civic-meeting repository](https://github.com/genome/civic-meeting).
