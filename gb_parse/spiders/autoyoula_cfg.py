

XPATH = {
    'brands' :  "//div[@data-target='transport-main-filters']/"
                "div[contains(@class, 'TransportMainFilters_brandsList')]//"
                "a[@data-target='brand']/@href",

    "next" :    "//a[@data-target-id=\"button-link-serp-paginator\"]/@href",

    "article" : "//article[@data-target=\"serp-snippet\"]//a[@data-target=\"serp-snippet-title\"]/@href",

    "article.title": "//div[@data-target='advert-title']/text()",
    "article.chars": "//h3[contains(text(), 'Характеристики')]/..//div[contains(@class, 'AdvertSpecs_row')]",
    "article.data": {
        "xpath" : "//script/text()",
        "regex" : '^window\.transitState\s*=\s*decodeURIComponent\(\\"(...+)\\"\)\;'
    }
}
