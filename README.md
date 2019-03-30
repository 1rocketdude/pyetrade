# pyetrade

Python E-Trade API Wrapper   
[![PyPI](https://img.shields.io/pypi/v/pyetrade.svg)](https://pypi.python.org/pypi/pyetrade)
[![PyPI](https://img.shields.io/pypi/l/pyetrade.svg)]()
[![PyPI](https://img.shields.io/pypi/pyversions/pyetrade.svg)](https://pypi.python.org/pypi/pyetrade)
[![Build Status](https://travis-ci.org/jessecooper/pyetrade.svg?branch=master)](https://travis-ci.org/jessecooper/pyetrade)
[![codecov](https://codecov.io/gh/jessecooper/pyetrade/branch/master/graph/badge.svg)](https://codecov.io/gh/jessecooper/pyetrade)
## Completed
v1 API  
Authorization API - ALL  
Accounts  
* list accounts
  
NOTICE: v0 API - Will be sunset by etrade on 12/31/2018 an effert is underway to move pyetrade over to v1  
Authorization API - ALL  
Order API - 
* List Orders
* Place Equity Order 
* Cancel Order
 
Market API - 
* Look Up Product 
* optionchain
* Get Quote  

## TODO
* All of v1 API
* Migrate test suit to pytest

## Install
```
pip install pyetrade
- or -
git clone https://github.com/jessecooper/pyetrade.git
cd pyetrade
sudo make init
sudo make install
```
## Example Usage
```python
import pyetrade
oauth = pyetrade.ETradeOAuth(consumer_key, consumer_secret)
oauth.get_request_token()
#Follow url and get verification code
oauth.get_access_token(verifier_code)
accounts = pyetrade.ETradeAccounts(
        consumer_key,
        consumer_secret, 
        oauth['oauth_token'],
        oauth['oauth_token_secret']
    )
accounts.list_accounts()
```
## Documentation
[PyEtrade Documentation](https://pyetrade.readthedocs.io/en/latest/)
## Contribute to pyetrade
* [ETrade API Docs](https://developer.etrade.com/ctnt/dev-portal/getArticleByCategory?category=Documentation)
* Fork pyetrade
* Development Setup:  
```
    sudo make init  
    sudo make devel
```
* Lint  
```
# Run Linter
pylint pyetrade/  #Lint score should be >=8
```
* Test  
```
make test #Ensure test coverage is >80%
```
* Push Changes:  
Push changes to a branch on your forked repo
* Create pull request
