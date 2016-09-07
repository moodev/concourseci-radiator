import json
import os
import time
from flask import Flask, Response, redirect, request, make_response, jsonify
import requests
import hashlib

app = Flask(__name__, static_url_path='', static_folder='public')

# add route for the statics
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

# get configuration settings
app.config.from_object('config')

# get properties from config file
baseUrl = app.config.get('CONCOURSE_DOMAIN', 'http://concourse.change.me.hostname')
ciUsername = app.config.get('CONCOURSE_USERNAME', 'admin')
ciPassword = app.config.get('CONCOURSE_PASSWORD', 'admin')

@app.route('/api/v1/pipelines', methods=['GET'])
def redirectPipelines():
    '''
        Make requests to the concourseCI and collect easy-to-parse output
        about pipelines and job statuses

    '''

    r = requests.get(baseUrl + '/api/v1/pipelines', auth=(ciUsername, ciPassword))

    # iterate over pipelines and find the status for each
    lstPipelines = []
    for pipeline in r.json():
        details = {}
        details['url'] = baseUrl + pipeline['url']
        details['name'] = pipeline['name']
        details['paused'] = pipeline['paused']

        if (not pipeline["paused"]):
            lstJobs = []

            rr = requests.get(baseUrl + '/api/v1/pipelines/' + pipeline['name'] + '/jobs', auth=(ciUsername, ciPassword))
            for job in rr.json():
                if job['next_build']:
                    lstJobs.append(
                            {
                                'status': job['next_build']['status'], 
                                'id': job['next_build']['id']
                            }
                        )
                elif job['finished_build']:
                    lstJobs.append(
                            {
                                'status': job['finished_build']['status'], 
                                'id': job['finished_build']['id']
                            }
                        )
                else:
                    lstJobs.append(
                        {'status': 'non-exist'}
                        )

            details['jobs'] = lstJobs

        lstPipelines.append(details)

    # sort pipelines by name
    lstPipelines = sorted(lstPipelines, key=lambda pipeline: pipeline['name'])     

    jsonResponse = json.dumps(lstPipelines)

    # SHA1 should generate well-behaved etags
    etag = hashlib.sha1(jsonResponse).hexdigest()
    requestEtag = request.headers.get('If-None-Match', '')

    if requestEtag == etag:
        # the concourse status wasn't modify. Return only "not modified" response
        return Response(
            status=304,
            mimetype='application/json',
            headers={
                'Cache-Control': 'public',
                'Access-Control-Allow-Origin': '*',
                'Etag': etag
            })

    else:
        # there were changes since the last call. Return full request
        return Response(
            jsonResponse,
            mimetype='application/json',
            headers={
                'Cache-Control': 'public',
                'Access-Control-Allow-Origin': '*',
                'Etag': etag
            })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=port, debug=True)
