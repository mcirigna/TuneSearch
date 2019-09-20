#!/usr/bin/python3

from flask import Flask, render_template, request

import search 

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
else:
    app.debug = False 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=["GET"])
def dosearch():
    query = request.args.get('query')
    qtype = request.args.get('query_type')
    page = request.args.get('page')
    if page is not None:
        page = int(page)
        search_results = search.search(query, qtype, page, False)
    else:
        search_results = search.search(query, qtype)

    return render_template('results.html',
            query=query,
            qtype=qtype,
            page=search_results['page'],
            songcount=search_results['songcount'],
            offset=search_results['offset'],
            results=len(search_results['songs']),
            search_results=search_results['songs'])


if __name__ == '__main__':
    app.run()