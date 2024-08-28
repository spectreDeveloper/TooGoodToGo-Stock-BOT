import logging
import asyncio
import aiohttp
import os

class TooGoodToGoProduct:
    def __init__(self, item_data):
        # Basic item details
        self.item_id = item_data["item"]["item_id"]
        self.item_type = item_data["item"]["item_type"]
        self.name = item_data["item"]["name"]
        
        # Price details
        self.price = self._convert_price(item_data["item"]["item_price"])
        self.original_price = self._convert_price(item_data["item"]["item_value"])
        
        # Stock and images
        self.available_stock = item_data["item"]["available_stock"]
        self.cover_picture_url = item_data["item"]["cover_picture"]["current_url"]
        
        # Manufacturer properties
        self.estimated_delivery = item_data["item"]["manufacturer_properties"]["estimated_delivery"]
        self.parcel_type = item_data["item"]["manufacturer_properties"]["parcel_type"]
        self.is_discounted = item_data["item"]["manufacturer_properties"]["is_discounted"]
        
        # Tags
        self.tags = [tag["short_text"] for tag in item_data["item"]["tags"]]
    
    def _convert_price(self, price_data):
        """
        Converts the price from minor units to major units based on the number of decimals.
        """
        return price_data["minor_units"] / (10 ** price_data["decimals"])
    
    def get_discount_percentage(self):
        """
        Calculate the discount percentage based on item price and item value.
        """
        if self.original_price > 0:
            discount = 100 * (1 - self.price / self.original_price)
            return round(discount, 2)
        return 0.0
    
    def is_available(self):
        """
        Check if the item is in stock.
        """
        return self.available_stock > 0
        

class TooGoodToGoAPI:
    captcha_url: str
    datadome_cookie: str | None = None
    access_token: str
    refresh_token: str
    access_token_ttl: int
    aiohttp_session: aiohttp.ClientSession

    def __init__(self):
        logging.info('TooGoodToGoAPI initialized, please solve the captcha')
        self.aiohttp_session = aiohttp.ClientSession()
        if os.getenv('DATADOME_COOKIE') is not None:
            self.datadome_cookie = os.getenv('DATADOME_COOKIE')
            
    
    async def retrieve_datadome_tokens(self) -> bool | str | None:
        headers = {
            'Host': 'apptoogoodtogo.com',
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': os.getenv('USER_AGENT'),
            'accept-language': 'it-IT',
            'Cookie': f'datadome={self.datadome_cookie}',
        }

        json_data = {
            'country_id': 'IT',
            'device_type': 'IOS',
            'push_notification_opt_in': False,
        }

        async with self.aiohttp_session.post('https://apptoogoodtogo.com/api/auth/v5/continue', headers=headers, json=json_data) as response:
            match response.status:
                case 403:
                    json_response: dict = await response.json()
                    self.captcha_url = json_response['url']
                    return self.captcha_url
                case 200:
                    json_response: dict = await response.json()
                    self.access_token = json_response['login_response']['access_token']
                    self.refresh_token = json_response['login_response']['refresh_token']
                    self.access_token_ttl = json_response['login_response']['access_token_ttl_seconds']
                    return True
                case _:
                    logging.error(f'Unexpected response status code {response.status}')
                    return None
                        
    async def retrieve_products_shippable(self) -> list[TooGoodToGoProduct]:
        headers = {
            'Host': 'apptoogoodtogo.com',
            'content-type': 'application/json',
            'accept': 'application/json',
            'authorization': f'Bearer {self.access_token}',
            'x-timezoneoffset': '+02:00',
            'accept-language': 'it-IT',
            'user-agent': os.getenv('USER_AGENT'),
            'x-24hourformat': 'true',
        }

        json_data = {
            'element_types_accepted': [
                'ITEM',
                'HIGHLIGHTED_ITEM',
                'MANUFACTURER_STORY_CARD',
                'DUO_ITEMS',
                'DUO_ITEMS_V2',
                'TEXT',
                'PARCEL_TEXT',
                'NPS',
                'SMALL_CARDS_CAROUSEL',
                'ITEM_CARDS_CAROUSEL',
            ],
            'action_types_accepted': [
                'QUERY',
            ],
            'display_types_accepted': [
                'LIST',
                'FILL',
            ],
        }

        async with self.aiohttp_session.post('https://apptoogoodtogo.com/api/manufactureritem/v2/', headers=headers, json=json_data) as response:
            if response.status == 200:
                json_response: dict = await response.json()
                products_list: list[TooGoodToGoProduct] = []
                for category_type in json_response['groups']:
                    if category_type['type'] == 'LIST':
                        for item in category_type['elements']:
                            if "item" not in item.keys():
                                continue
                            products_list.append(TooGoodToGoProduct(item))
                return products_list
            else:
                logging.error(f'Unexpected response status code {response.status}')
                return []
            

    
    