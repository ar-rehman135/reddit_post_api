import json
from datetime import datetime
from sqlalchemy import desc, asc, func, and_
from flask import Flask, request
from flask_cors import cross_origin
from requests import request as req

from models.posts import Posts, Scores
from src.database.db import db_session
app = Flask(__name__)
app.config['REVERSE_PROXY_PATH'] = '/api/get_ticker_data'


def error_json(msg):
    return json.dumps({
        "error": msg
    })


@app.route('/api/get_ticker_data', methods=['GET'])
@cross_origin()
def get_ticker():
    if 'ticker' in request.args:
        ticker = request.args.get('ticker')
        ticker = str(ticker).upper()
        get_ticker_data_from_post = Posts.query.filter(Posts.stock_ticker == ticker).first()

        if get_ticker_data_from_post:
            d1 = get_ticker_data_from_post.toDict(True)

            ##### hit polygon api
            volume = ''
            week_high = ''
            week_low = ''
            POLYGON_API_KEY = 'YvETvDJe59N6Duvha_iEQPLFepUqsZwR'
            todayDate = datetime.today()
            toDate = todayDate.strftime("%Y-%m-%d")
            fromDate = str(todayDate.year - 1) + "-" + str(todayDate.month).zfill(2) + "-" + str(todayDate.day).zfill(2)
            volume_url = "https://api.polygon.io/v2/aggs/ticker/"+ticker+"/range/1/year/"+fromDate+"/"+toDate+"?unadjusted=true&sort=asc&limit=120&apiKey="+POLYGON_API_KEY;
            print(volume_url)
            response2 = req(method="GET", url=volume_url)
            result2 = json.loads(response2.text)
            if 'results' in result2 and len(result2['results'])>0:
                volume = result2['results'][0]["v"]
                week_high = result2['results'][0]["h"]
                week_low = result2['results'][0]["l"]

            d2 = {
                "volume": volume,
                "week_high": week_high,
                "week_low": week_low
            }

            data = dict(d1, **d2)
            d = json.dumps(data)
            return d

        return error_json("Invalid Ticker " + ticker)
    else:
        return error_json("Invalid Data")

@app.route('/api/list_tickers', methods=['GET'])
@cross_origin()
def list_ticker():

    #### get args  ######
    sort_order = request.args.get('sort_order') if request.args.get('sort_order') else "asc"
    sort_column = request.args.get('sort_column') if request.args.get('sort_column') else "id"
    limit = request.args.get('limit') if request.args.get("limit") else 10
    page_no = request.args.get('page_no') if request.args.get("page_no") else 1
    search = request.args.get('search')

    if not (sort_order == 'asc' or sort_order == "desc"):
        return error_json("Invalid Sort Order")

    try:
        limit = int(limit)
    except:
        return error_json("Invalid Limit")

    column_names = Posts.__table__.columns.keys()
    if not sort_column in column_names:
        return error_json("Invalid Sort Column")
    else:
        order_by_column = desc(getattr(Posts, sort_column)) if sort_order == "desc" else asc(getattr(Posts, sort_column))

    try:
        page_no = int(page_no)
    except:
        return error_json("Invalid page_no")

    if not search:
        j = Posts.query\
            .order_by(order_by_column).limit(limit).offset((page_no-1)*limit).all()
    else:
        j = Posts.query \
            .filter(Posts.stock_ticker.contains(search))\
            .order_by(order_by_column).limit(limit).offset((page_no - 1) * limit).all()

    count = db_session.query(func.count(Posts.stock_ticker)).scalar()
    data = []
    for post in j:
        d3 = post.toDict(True)
        data.append(d3)

    return json.dumps({"count": len(data), "total": count, 'data':data})

@app.route('/api/list_tickers_by_sub_reddit', methods=['GET'])
@cross_origin()
def list_tickers_by_sub_reddit():
    sub_reddit = request.args.get('sub_reddit') if request.args.get('sub_reddit') else 'pennystocks'
    sort_order = request.args.get('sort_order')  if request.args.get('sort_order') else 'asc'
    sort_column = request.args.get('sort_column') if request.args.get('sort_column') else 'id'
    todayDate = datetime.today()
    date = request.args.get('date')
    if date:
        try:
            date = datetime.strptime(date, "%Y-%m-%d")
        except:
            return error_json("Invalid Date. Date must be in YYYY-mm-dd format")
    else:
        date = todayDate.strftime("%y-%m-%d")
    all_sub_reddits = Scores.query.with_entities(Scores.sub_reddit).all()
    all_sub_reddits = [sub_reddit[0] for sub_reddit in all_sub_reddits]

    if not sub_reddit in all_sub_reddits:
        return error_json("Invalid sub_reddit")

    column_names = Scores.__table__.columns.keys()
    if not sort_column in column_names:
        return error_json("Invalid Sort Column")
    else:
        order_by_column = desc(getattr(Scores, sort_column)) if sort_order == "desc" else asc(
            getattr(Scores, sort_column))

    query = db_session.query(Scores, Posts).outerjoin(Posts, Scores.stock_ticker == Posts.stock_ticker) \
        .filter(and_(Scores.sub_reddit == sub_reddit, func.date(Scores.date) == date))\
        .order_by(order_by_column).all()

    data = []
    d1 = {}
    d2 = {}
    for post in query:
        if post[1]:
            d1 = post[1].toDict(False)
        if post[0]:
            d2 = post[0].toDict()
        d3 = dict(d1, **d2)
        data.append(d3)

    return json.dumps({"count": len(data), 'data': data})

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
