#!/usr/bin/python3

"""Market - ETrade Market API V1

    Calling sequence to get all option chains for a particular month
    me = pyetrade.market.ETradeMarket(
                    consumer_key,
                    consumer_secret,
                    tokens['oauth_token'],
                    tokens['oauth_token_secret'],
                    dev = False)

    option_dates = me.get_option_expire_date('aapl')
    option_chains = me.get_option_chains('aapl')

    OR all inclusive:
        (option_dates,option_chains) = me.get_all_option_chains('aapl')
    TODO:
    * move logger into object under self.logger

"""

import datetime as dt
import logging
import xmltodict
from requests_oauthlib import OAuth1Session

LOGGER = logging.getLogger(__name__)


class ETradeMarket(object):
    """ETradeMarket"""

    def __init__(
        self,
        client_key,
        client_secret,
        resource_owner_key,
        resource_owner_secret,
        dev=True,
    ):
        """__init__(client_key, client_secret, resource_owner_key,
                    resource_owner_secret, dev=True)

            This is the object initialization routine, which simply
            sets the various variables to be used by the rest of the
            methods and constructs the OAuth1Session.

            param: client_key
            type: str
            description: etrade client key

            param: client_secret
            type: str
            description: etrade client secret

            param: resource_owner_key
            type: str
            description: OAuth authentication token key

            param: resource_owner_secret
            type: str
            description: OAuth authentication token secret

            param: dev
            type: boolean
            description: use the sandbox environment (True) or live (False)

        """
        self.client_key = client_key
        self.client_secret = client_secret
        self.resource_owner_key = resource_owner_key
        self.resource_owner_secret = resource_owner_secret
        self.dev_environment = dev
        suffix = "apisb" if dev else "api"
        self.base_url = r"https://%s.etrade.com/v1/market/" % suffix
        self.session = OAuth1Session(
            self.client_key,
            self.client_secret,
            self.resource_owner_key,
            self.resource_owner_secret,
            signature_type="AUTH_HEADER",
        )

    def __str__(self):
        ret = [
            "Use development environment: %s" % self.dev_environment,
            "base URL: %s" % self.base_url,
        ]
        return "\n".join(ret)

    def look_up_product(self, search_str: str, resp_format="xml") -> dict:
        """Look up product
           Args:
            search_str (str): full or partial name of the company. Note
                that the system extensivly abbreviates common words
                such as company, industry and systems and generally
                skips punctuation.
            resp_format (str): the api endpoint to hit (json or xml)
        """

        # api_url = self.base_url + "lookup/%s" % search_str
        api_url = "%slookup/%s" % (
            self.base_url,
            search_str if resp_format.lower() == "xml" else search_str + ".json",
        )
        LOGGER.debug(api_url)
        req = self.session.get(api_url)
        req.raise_for_status()
        LOGGER.debug(req.text)
        return xmltodict.parse(req.text) if resp_format.lower() == "xml" else req.json()

    def get_quote(
        self,
        symbols,
        detail_flag=None,
        require_earnings_date=None,
        skip_mini_options_check=None,
        resp_format="xml",
    ) -> dict:
        """ get_quote(symbols, detail_flag=None, require_earnings_date=None,
                      skipMiniOptionsCheck=None)

            Get quote data on all symbols provided in the list args.
            the eTrade API is limited to 25 requests per call. Issue
            warning if more than 25 are requested. Only process the first 25.

            param: skipMiniOptionsCheck
            type: True, False, None
            description: If value is true, no call is made to the service to check
            whether the symbol has mini options. If value is false or if the field
            is not specified, a service call is made to check if the symbol has mini
            options

            param: detailFlag
            type: enum
            required: optional
            description: Optional parameter specifying which details to
                return in the response. The field set for each possible
                value is listed in separate tables below. The possible
                values are:
                    * FUNDAMENTAL - Instrument fundamentals and latest
                        price
                    * INTRADAY - Performance for the current of most
                        recent trading day
                    * OPTIONS - Information on a given option offering
                    * WEEK_52 - 52-week high and low (highest high and
                        lowest low
                    * ALL (default) - All of the above information and
                        more
                    * MF_DETAIL - MutualFund structure gets displayed.

            param: symbols
            type: list
            required: true
            description: One or more symobols for equities or options, up to a
            maximum of  25 symbols.
                For equities, the symbol name alone, e.g. GOOGL.
                Symbols for options are more complex, consisting of six elements
                separated by colons, in this format:
                underlier:year:month:day:optionType:strikePrice

            if q is returned value, then q['QuoteResponse']['QuoteData'] is a list of quotes returned
            """

        assert detail_flag in (
            "fundamental",
            "intraday",
            "options",
            "week_52",
            "all",
            "mf_detail",
            None,
        )
        assert require_earnings_date in (True, False, None)
        assert skip_mini_options_check in (True, False, None)
        assert isinstance(symbols, list or tuple)
        if len(symbols) > 25:
            LOGGER.warning(
                "get_quote asked for %d requests; only first 25 returned" % len(symbols)
            )

        args = list()
        if detail_flag is not None:
            args.append("detailflag=%s" % detail_flag.upper())
        if require_earnings_date:
            args.append("requireEarningsDate=true")
        if skip_mini_options_check is not None:
            args.append("skipMiniOptionsCheck=%s" % str(skip_mini_options_check))

        api_url = "%s%s%s" % (self.base_url, "quote/", ",".join(symbols[:25]))
        if resp_format.lower() == "json":
            api_url += ".json"
        if len(args):
            api_url += "?" + "&".join(args)
        LOGGER.debug(api_url)

        req = self.session.get(api_url)
        req.raise_for_status()
        LOGGER.debug(req.text)

        return xmltodict.parse(req.text) if resp_format.lower() == "xml" else req.json()

    def get_all_option_chains(self, underlier):
        """ Returns the all the option chains for the underlier with expiration_dates
            as the key. This requires two calls, one to get_option_expire_date, then
            to get all the expiration_dates and multiple calls to get_option_chains
            with defaults.

            param: underlier
            type: str
            description: market symbol

        """
        try:
            expiration_dates = self.get_option_expire_date(underlier)
        except Exception:
            raise
        rtn = dict()
        for this_expiry_date in expiration_dates:
            q = self.get_option_chains(underlier, this_expiry_date)
            chains = q['OptionChainResponse']['OptionPair']
            rtn[this_expiry_date] = [i['Put'] for i in chains] + [i['Call'] for i in chains]
        return rtn

    def get_option_chains(
        self,
        underlier,
        expiry_date,
        skipAdjusted=None,
        chainType=None,
        strikePriceNear=None,
        noOfStrikes=None,
        optionCategory=None,
        priceType=None,
    ):
        """ get_optionchains(underlier, expiry_date=None, skipAdjusted=None,
                             chainType=None, strikePriceNear=None, noOfStrikes=None,
                             optionCategory=None, priceType=None)

            Returns the option chain information for the requested expiry_date and
            chaintype in the desired format.

            if q is the returned value, then q['OptionChainResponse']['OptionPair'] is
            a list of option chain dict, with keys 'Put' and 'Call'.
            Therefore, q[0]['Put'] is the first 'Put' option chain.

            param: underlier
            type: str
            description: market symbol

            param: chainType
            type: str
            description: put, call, or callput
            Default: callput

            param: priceType
            type: 'atmn', 'all', None
            description: The price type
            Default: ATNM

            param: expiry_date
            type: dt.date()
            description: contract expiration date; if expiry_date is None, then gets the
            expiration_date closest to today

            param: optionCategory
            type: 'standard', 'all', 'mini', None
            description: what type of option data to return
            Default: standard

            param: skipAdjusted
            type: bool
            description: Specifies whether to show (TRUE) or not show (FALSE) adjusted
                options, i.e., options that have undergone a change resulting
                in a modification of the option contract.

            Sample Request
            GET https://api.etrade.com/v1/market/optionchains?
            expiryDay=03&expiryMonth=04&expiryYear=2011
            &chainType=PUT&skipAdjusted=true&symbol=GOOGL

        """
        assert chainType in ("put", "call", "callput", None)
        assert optionCategory in ("standard", "all", "mini", None)
        assert priceType in ("atmn", "all", None)
        assert skipAdjusted in (True, False, None)

        args = ["symbol=%s" % underlier]
        if expiry_date is not None:
            args.append(
                "expiryDay=%02d&expiryMonth=%02d&expiryYear=%04d"
                % (expiry_date.day, expiry_date.month, expiry_date.year)
            )
        if strikePriceNear is not None:
            args.append("strikePriceNear=%0.2f" % strikePriceNear)
        if chainType is not None:
            args.append("chainType=%s" % chainType.upper())
        if optionCategory is not None:
            args.append("optionCategory=%s" % optionCategory.upper())
        if priceType is not None:
            args.append("priceType=%s" % priceType.upper())
        if skipAdjusted is not None:
            args.append("skipAdjusted=%s" % str(skipAdjusted))
        if noOfStrikes is not None:
            args.append("noOfStrikes=%d" % noOfStrikes.upper())
        api_url = self.base_url + "optionchains?" + "&".join(args)

        req = self.session.get(api_url)
        req.raise_for_status()
        LOGGER.debug(api_url)
        LOGGER.debug(req.text)
        return xmltodict.parse(req.text)

    def get_option_expire_date(self, underlier):
        """ get_option_expiry_dates(underlier)

            JSON formatted return does not work as documented.
            However, the XML formatted response correctly returns the weekly and monthly
            option dates

            param: underlier
            type: str
            description: market symbol

            https://api.etrade.com/v1/market/optionexpiredate?symbol={symbol}

            Sample Request
            GET https://api.etrade.com/v1/market/optionexpiredate?
               symbol=GOOG&expiryType=ALL

            another way to do this is with lxml:
                import lxml.etree as etree
                r = etree.parse(xml).getroot()
                date_list = list()
                for this_one in r:
                    q = {a.tag: a.text for a in this_one.getchildren()}
                    date_list.append(
                    dt.date(int(q['year']), int(q['month']), int(q['day'])))
        """

        api_url = (
            self.base_url + "optionexpiredate?symbol=%s&expiryType=ALL" % underlier
        )
        LOGGER.debug(api_url)

        req = self.session.get(api_url)
        req.raise_for_status()
        LOGGER.debug(req.text)

        try:
            q = xmltodict.parse(req.text)
        except Exception as err:
            LOGGER.error("XML parsing %s text failed\n%s", underlier, err)
            raise

        dates = [dt.date(
                    int(this_date["year"]),
                    int(this_date["month"]),
                    int(this_date["day"]))
                    for this_date in q['OptionExpireDateResponse']['ExpirationDate']
                ]

        return dates
