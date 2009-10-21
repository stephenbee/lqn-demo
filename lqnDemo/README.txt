Ok, here is how to make use of this 

git clone git@github.com:stephenbee/lqn-demo.git
cd lqn-demo
virtualenv --no-site-packages .
./bin/easy_install -U setuptools
cd lqnDemo
../bin/python setup.py develop
../bin/paster serve lqnDemo.ini




