import time
import http.client
import json
from argparse import ArgumentParser
from prettytable import PrettyTable

_seller = 'your_seller_id_here'
_discord_token = 'your_auth_token_here'

# Examples
_common_asks = [
    {
        'id': '1256484542',  # Wood
        'count': 60
    },
    {
        'id': '529364044',  # Iron Nugget
        'count': 60
    },
    {
        'id': '529364044',  # Softwood
        'count': 60
    },
    {
        'id': '1517313989',  # Hardwood
        'count': 60
    },
    {
        'id': '209389833',  # Clay
        'count': 60
    },
    {
        'id': '785461505',  # Gold Nugget
        'count': 5
    },
    {
        'nmt': 3  # Nook Miles Ticket
    },
    {
        'id': '893650231',  # Rusted Part
        'count': 3
    },
    {
        'bells': 1000000
    }
]

_listings = {
    'listings': [
        {
            'id': '2050973545',  # Great White Shark Model
            'asks': _common_asks
        },
        {
            'id': '1526871784',  # Katana
            'variant': '1197763550',  # Gold
            'asks': {
                'nmt': 10  # Nook Miles Ticket
            }
        }
    ]
}


class Item:
    def __init__(self, json):
        self.id = json['id']
        self.count = 1
        self.variant = None
        self.diy = False

        if 'count' in json:
            self.count = json['count']

        if 'variant' in json:
            self.variant = json['variant']

        if 'diy' in json:
            self.diy = json['diy']

    def __str__(self):
        return 'Id:{} Count:{} Variant:{} DIY:{}'.format(self.id, self.count, self.variant, self.diy)

    def get_body_for_listing(self):
        body = {
            'amount': self.count,
            'item': self.id,
            'selling': True,
            'variant': self.variant,
            'diy': self.diy,
        }

        return body

    def get_body_for_ask(self):
        body = {
            'diy': self.diy,
            'quantity': self.count,
            'value': self.id
        }

        if self.variant is not None:
            body['variant'] = {
                'id': self.variant
            }

        return body


def get_connection():
    return http.client.HTTPSConnection('nookazon.com')


def get_default_headers():
    return {
        'Content-type': 'application/json',
        'authorization': _discord_token
    }


def add_listing(body):
    connection = get_connection()

    # https://nookazon.com/api/listings/create
    api = '/api/listings/create'
    connection.request('POST', api, json.dumps(body), get_default_headers())
    response = connection.getresponse()

    return response.status == 200


def add_listing_for_bells(item, bells):
    body = item.get_body_for_listing()
    body['bells'] = bells

    if not add_listing(body):
        print('Failed to add listing of {} for {} bells'.format(item, bells))


def add_listing_for_nmt(item, nmt):
    body = item.get_body_for_listing()
    body['nmt'] = nmt

    if not add_listing(body):
        print('Failed to add listing of {} for {} Nook Miles Tickets'.format(item, nmt))


def add_listing_for_item(item, ask):
    body = item.get_body_for_listing()
    body['items'] = [ask.get_body_for_ask()]

    if not add_listing(body):
        print('Failed to add listing of {} for {}'.format(item, ask))


def add_listings():
    listings = _listings['listings']
    for listing in listings:
        listing_item = Item(listing)
        for ask in listing['asks']:
            if 'bells' in ask:
                add_listing_for_bells(listing_item, ask['bells'])
            elif 'nmt' in ask:
                add_listing_for_nmt(listing_item, ask['nmt'])
            else:
                ask_item = Item(ask)
                add_listing_for_item(listing_item, ask_item)


def get_listings():
    connection = get_connection()
    # https://nookazon.com/api/listings?auction=false&seller=<seller_id>
    api = '/api/listings?auction=false&seller={}'.format(_seller)
    connection.request('GET', api, None, get_default_headers())
    response = connection.getresponse().read().decode()
    json_response = json.loads(response)
    return json_response['listings']


def dump_listings():
    listings = get_listings()
    for listing in listings:
        item = listing['name']
        if listing['variant_name'] is not None:
            item = '{} ({})'.format(item, listing['variant_name'])

        for price in listing['prices']:
            if price['bells'] is not None:
                print('{} - {} bells'.format(item, price['bells']))

            if price['name'] is not None:
                print('{} - {} x {}'.format(item,
                                            price['name'],
                                            price['quantity']))


def delete_listing(id):
    connection = get_connection()
    # https://nookazon.com/api/sell
    api = '/api/sell'
    body = {
        'listing': id,
        'selling': True,
        'page': 0,
        'remove': True
    }

    connection.request('POST', api, json.dumps(body), get_default_headers())
    response = connection.getresponse().read().decode()
    json_response = json.loads(response)
    if (json_response['msg'] != 'success'):
        print('Failed to delete listing: {}'.format(id))


def delete_listings():
    listings = get_listings()
    for listing in listings:
        for price in listing['prices']:
            delete_listing(price['listing_id'])


def refresh_periodically(timeInMinutes):
    start_time = time.time()
    while True:
        print('Refreshing postings.')
        # delete_listings()
        # add_listings()
        time.sleep(timeInMinutes * 60)


def do_nothing():
    pass


def main():
    parser = ArgumentParser(description='Handle Nookazon listings.')

    parser.add_argument(
        '-a',
        '--add',
        '--add-listings',
        dest='add_listings',
        action='store_const',
        const=add_listings,
        default=do_nothing,
        help='Will list all the items defined in the _listings variable to the user\'s profile.'
    )

    parser.add_argument(
        '-du',
        '--dump',
        '--dump-listings',
        dest='dump_listings',
        action='store_const',
        const=dump_listings,
        default=do_nothing,
        help='Will dump all listings AFTER deleting/creating listings.'
    )

    parser.add_argument(
        '-do',
        '--dump-old',
        '--dump-old-listings',
        dest='dump_old_listings',
        action='store_const',
        const=dump_listings,
        default=do_nothing,
        help='Will dump all listings BEFORE deleting/creating listings.'
    )

    parser.add_argument(
        '-d',
        '--delete',
        '--delete-listings',
        dest='delete_listings',
        action='store_const',
        const=delete_listings,
        default=do_nothing,
        help='Will delete all postings in the user\'s profile.'
    )

    parser.add_argument(
        '-p',
        '--periodically',
        '--periodically-list',
        type=int,
        metavar='MINUTES',
        help='If this is set, it will re-post all listings every N minutes.'
    )

    args = parser.parse_args()

    args.dump_old_listings()
    args.delete_listings()
    args.add_listings()
    args.dump_listings()

    if args.periodically:
        refresh_periodically(args.periodically)

    exit(0)


if __name__ == "__main__":
    main()
