import json
from flask import Flask, request, jsonify, url_for
from flask_cors import cross_origin

from models.posts import Posts, Scores

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
                "industry": industry
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

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
