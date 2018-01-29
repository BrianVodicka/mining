import requests
import pymongo
import pdb
import json
import time

API_URL = "https://whattomine.com/coins.json"

def commit_to_db(data):
    client = MongoClient('localhost', 27017)
    datacollection = client.testdata
    for coin, coin_data in data.iteritems():
        coin_id = "%s-%s" % coin, coin_data['algorithm']
        try:
            datacollection.find_one_and_update({'coin_id': coin_id}, 
                {'$push': {
                    'data': {'exchange_rate': coin_data['exchange_rate'], 
                    'nethash': coin_data['nethash'],
                    'profitability': coin_data['profitability'],
                    'exchange_rate_vol': coin_data['exchange_rate_vol'],
                    'difficulty': coin_data['difficulty']}},
                 '$set': {
                    'block_time': coin_data['block_time'],
                    'block_size': coin_data['block_size'],
                    'block_reward': coin_data['block_reward']}
                })
        except:
            datacollection.insert_one({
                'coin_id': coin_id,
                'tag': coin_data['tag'],
                'block_reward': coin_data['block_reward'],
                'block_time': coin_data['block_time'],
                'algorithm': coin_data['algorithm'],
                'exchange_rate_curr': coin_data['exchange_rate_curr'],
                'data': [{
                    'nethash': coin_data['nethash'],
                    'exchange_rate': coin_data['exchange_rate'],
                    'lagging': coin_data['lagging'],
                    'last_block': coin_data['last_block'],
                    'profitability': coin_data['profitability'],
                    'exchange_rate_vol': coin_data['exchange_rate_vol'],
                    'timestamp': coin_data['timestamp'],
                    'market_cap': coin_data['market_cap'],
                }]
            })
    # important fields: exchange_rate, nethash, tag, profitability, difficulty, block_time, block_size
        
    
    #datacollection.find_one_and_update({'coin_id': data)

def compute_average(top_profits, data):
    most_profitable = 0
    top_coin = None
    for coin, coin_data in data.iteritems():
        #most_profitable = max(most_profitable, float(coin_data['btc_revenue']))
        if float(coin_data['btc_revenue']) > most_profitable:
            most_profitable = float(coin_data['btc_revenue'])
            top_coin = coin
    top_profits.append(most_profitable)
    avg_profit_btc = float(sum(top_profits)) / len(top_profits)
    avg_profit_usd = avg_profit_btc * 11500   
    print "%s profit is highest now (%s, %s) / 24h" % (top_coin, most_profitable, most_profitable * 11500)
    print "running average profit is (%s, %s) / 24h" % (avg_profit_btc, avg_profit_usd)

def get_data():
    result = requests.get(API_URL)
    data = json.loads(result.text)
    return data['coins']

def get_data_continuous(timeInterval):
    topProfits = []
    while True:
        data = get_data()
        compute_average(topProfits, data)
        with open("whattomine_%d.txt" % time.time(), 'w') as outfile:
            json.dump(data, outfile)
        time.sleep(timeInterval)

if __name__ == "__main__":
    get_data_continuous(60*3) 
