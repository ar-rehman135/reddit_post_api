import json
from flask import Flask, request, jsonify
from flask_cors import cross_origin

from models.posts import Posts, Scores

app = Flask(__name__)


@app.route('/api/get_ticker_data', methods=['POST'])
@cross_origin()
def get_ticker():
    ticker = request.json.get('ticker')
    get_ticker_data_from_scores = Scores.query.filter(Scores.stock_ticker == ticker).first()
    score = get_ticker_data_from_scores.score
    mention = get_ticker_data_from_scores.mention

    ######### Posts data
    get_ticker_data_from_post = Posts.query.filter(Posts.stock_ticker == ticker).first()
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
        "score" : score,
        "mention" : mention,
        "logo": logo,
        "sector": sector,
        "market_cap" : market_cap,
        "employees": employees,
        "url": url,
        "description": description,
        "company_name": company_name,
        "similiar_companies": similiar_companies,
        "industry": industry
    }

    d = json.dumps(data)
    return d

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
