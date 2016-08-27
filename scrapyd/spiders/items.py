# -*- coding: utf-8 -*-
from scrapy import Item, Field


class ProductItem(Item):
    # define the fields for your item here like:
    keyword = Field()
    total_matches = Field()
    all_brands = Field()

    product_image = Field()
    title = Field()
    rank = Field()
    brand = Field()
    price = Field()
    asin = Field()
    prime = Field()
    shipping_price = Field()
    new_price = Field()
    new_offers = Field()
    used_price = Field()
    used_offers = Field()
    rating = Field()
    number_of_reviews = Field()
    category = Field()
    number_of_items = Field()
