import json
from datetime import datetime
from sqlalchemy import desc, asc, func
from flask import Flask, request
from flask_cors import cross_origin
from requests import request as req

from models.posts import Posts, Scores
from src.database.db import db_session
app = Flask(__name__)
app.config['REVERSE_PROXY_PATH'] = '/api/get_ticker_data'

@app.route('/api/get_ticker_data', methods=['GET'])
@cross_origin()
def get_ticker():
    if 'ticker' in request.args:
        ticker = request.args.get('ticker')
        ticker = str(ticker).upper()
        get_ticker_data_from_post = Posts.query.filter(Posts.stock_ticker == ticker).first()
        if not get_ticker_data_from_post:
            err = {
                "message": "Invalid Ticker " + ticker,
                "code": "201"
            }
            return json.dumps(err)
        get_ticker_data_from_scores = Scores.query.filter(Scores.stock_ticker == ticker).first()
        if not get_ticker_data_from_scores:
            score = ''
            mention = ''

        if get_ticker_data_from_scores:
            score = get_ticker_data_from_scores.score
            mention = get_ticker_data_from_scores.mention
        if get_ticker_data_from_post:
            logo = get_ticker_data_from_post.logo
            industry = get_ticker_data_from_post.industry
            sector = get_ticker_data_from_post.sector
            market_cap = get_ticker_data_from_post.market_cap
            employees = get_ticker_data_from_post.employees
            url = get_ticker_data_from_post.url
            description = get_ticker_data_from_post.description
            company_name = get_ticker_data_from_post.company_name
            similiar_companies = get_ticker_data_from_post.similiar_companies

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

            data = {
                "score": score,
                "mention": mention,
                "logo": logo,
                "sector": sector,
                "market_cap": market_cap,
                "employees": employees,
                "url": url,
                "description": description,
                "company_name": company_name,
                "similiar_companies": similiar_companies,
                "industry": industry,
                "volume": volume,
                "week_high": week_high,
                "week_low": week_low
            }

            d = json.dumps(data)
            return d
        err = {
            "message": "Invalid Ticker " + ticker,
            "code": "201"
        }
        return json.dumps(err)
    else:
        err = {
            "message": "Invalid Data",
            "code": "403"
        }
        return json.dumps(err)

@app.route('/api/list_tickers', methods=['GET'])
@cross_origin()
def list_ticker():

    #### get args  ######
    sort_order = request.args.get('sort_order') if request.args.get('sort_order') else "asc"
    sort_column = request.args.get('sort_column') if request.args.get('sort_column') else "id"
    limit = request.args.get('limit') if request.args.get("limit") else 10
    page_no = request.args.get('page_no') if request.args.get("page_no") else 1
    search = request.args.get('search')

    try:
        limit = int(limit)
    except:
        return json.dumps({"error": "Invalid Limit"})

    column_names = Posts.__table__.columns.keys()
    if not sort_column in column_names:
        column_names = Scores.__table__.columns.keys()
        if not sort_column in column_names:
            return json.dumps({
                "error": "Invalid Sort Column"
            })

    try:
        page_no = int(page_no)
    except:
        return json.dumps({"error": "Invalid page_no"})

    if not (sort_order == 'asc' or sort_order == "desc"):
        return json.dumps({
            "error": "Invalid Sort Order"
        })


    order_by_column = desc(sort_column) if sort_order == "desc" else asc(sort_column)

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
        d3 = post.toDict()
        data.append(d3)

    return json.dumps({"count": len(data), "total": count, 'data':data})

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
