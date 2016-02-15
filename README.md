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
source myenv/bin/activate
pip install .
```

To deactivate the virtual environment,
```
deactivate
```

##Usage
Very basic functionality for now, this will pull up a web-page running on
http://127.0.0.1:5000/ , this page will list the items that need work.
```
civic-api-client action-items-web-view
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
