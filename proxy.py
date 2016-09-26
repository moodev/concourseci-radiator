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
ciTeam = app.config.get('CONCOURSE_TEAM', 'main')

# header with auth token
tokenHeader = ''

@app.route('/api/v1/pipelines', methods=['GET'])
def redirectPipelines():
    '''
        Make requests to the concourseCI and collect easy-to-parse output
        about pipelines and job statuses

    '''

    # Then, get list of all the pipelines
    try:
        r = requests.get(baseUrl + '/api/v1/pipelines', headers=tokenHeader)
        r.raise_for_status()
    except requests.ConnectionError as e:
        return Response("The ConcourseCI is not reachable", status=500)
    except requests.exceptions.HTTPError as e:
        return Response("The ConcourseCI is not reachable, status code: " + str(e.response.status_code) + ", reason: " + e.response.reason, status=500)

    # Check that at least one worker is available
    try:
        from requests.auth import HTTPDigestAuth
        responseWorkers = requests.get(baseUrl + '/api/v1/workers', headers=tokenHeader)
        responseWorkers.raise_for_status()
        if len(responseWorkers.json()) == 0:
            return Response("There are no workers available!", status=500)

    except requests.exceptions.HTTPError as e:
        return Response("The ConcourseCI is not reachable, status code: " + str(e.response.status_code) + ", reason: " + e.response.reason, status=500)


    # iterate over pipelines and find the status for each
    lstPipelines = []
    for pipeline in r.json():
        details = {}
        details['url'] = baseUrl + pipeline['url']
        details['name'] = pipeline['name']
        details['paused'] = pipeline['paused']

        if (not pipeline["paused"]):
            lstJobs = []

            rr = requests.get(baseUrl + '/api/v1/teams/' + ciTeam + '/pipelines/' + pipeline['name'] + '/jobs', headers=tokenHeader)
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
        # the concourse status wasn't modify. Return only "not modified" status code, avoiding to refresh the page
        return Response(
            status=304,
            mimetype='application/json',
            headers={
                'Cache-Control': 'public',
                'Access-Control-Allow-Origin': '*',
                'Etag': etag
            })

    else:
        # there were changes since the last call. Return the full response
        return Response(
            jsonResponse,
            mimetype='application/json',
            headers={
                'Cache-Control': 'public',
                'Access-Control-Allow-Origin': '*',
                'Etag': etag
            })


if __name__ == '__main__':

    # set debugging level to "ERROR"
    import logging
    logging.basicConfig(level=logging.ERROR)

    # get the Bearer Token for the given team avoiding to request it again and again
    r = requests.get(baseUrl + '/api/v1/teams/' + ciTeam + '/auth/token', auth=(ciUsername, ciPassword))
    r.raise_for_status()
    tokenHeader = { "Authorization" : "Bearer " + r.json()['value'] }

    port = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=port, debug=False)
