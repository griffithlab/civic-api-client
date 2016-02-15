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
virtualenv myenv && source myenv/bin/activate
pip install .
```

##Usage
Very basic functionality for now
```
civic-api-client action-items-web-view
```

##Development
To contribute to the code for this project, please fork the repo and submit a pull request

To test your own changes (after editing code) you can rebuild the package as follows:
pip install . --upgrade
