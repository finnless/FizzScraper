from decouple import config
import requests
import time

class ScrapeSession:
    def __init__(self, auth):
        self.auth = auth


    def save_auth(self, new_auth):
        # TODO implement save auth to local csv or something
        pass

    def refresh_auth(self):
        print('Refreshing Token...')

        refresh_token = config('REFRESH_TOKEN')
        
        url = "https://securetoken.googleapis.com/v1/token?key=AIzaSyCV4nUAYef19aqroWDdeMFzQZmCXxdJoJs"

        headers = {
            'content-type': 'application/json',
            'accept': '*/*'
        }
        
        data = {
            "grantType": "refresh_token",
            "refreshToken": refresh_token
            }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            refresh_json = response.json()
            self.auth = refresh_json['id_token']
            self.save_auth(refresh_json['id_token'])
        else:
            raise Exception('Auth Refresh Failed.')

    def request_post(self, post_id):

        url = "https://us-central1-buzz-3eeb8.cloudfunctions.net/feedMainEndpoint"

        headers = {
            'content-type': 'application/json',
            'accept': '*/*',
            'authorization': 'Bearer ' + self.auth
        }

        data = {
            "data":{
                "postID": post_id,
                "clientVersion": "1.11.13",
                "startAfter": post_id,
                "endpointFeedType": "getPostByID"
                }
            }

        response = requests.post(url, headers=headers, json=data)

        return response
        
    
    def get_post(self, post_id):

        for attempt in ['1', '2']:
            
            print(f'Try {attempt} for post {post_id}')

            request = self.request_post(post_id)
            
            # if GOOD
            if request.status_code == 200:
                return request.json()
            # if Unauthorized
            elif request.status_code == 401:
                print('401 Unauthorized')
                self.refresh_auth()
        raise Exception(f'Could not get post {post_id} at {time.time()}')


    def parse_poll(self, post_id, post_json=None):

        if post_json == None:
            post_json = self.get_post(post_id)

        poll_options = post_json['result']['posts'][0]['pollOptions']
        # print(json.dumps(poll_options, indent=4))

        result = {
        "time": time.time(),
        "postID": post_json['result']['posts'][0]['postID'],
        "likes": post_json['result']['posts'][0]['likesMinusDislikes'],
        "heads_votes": poll_options[0]['numVotes'],
        "tails_votes": poll_options[1]['numVotes']
        }
        return result




refresh = config('REFRESH_TOKEN')

auth = config('AUTH')


post_id = config('POST_ID')

s = ScrapeSession(auth)


poll = s.parse_poll(post_id)

# TODO Save to local csv

print(f'At {poll["time"]}, the post {poll["postID"]} had:')
print('Likes: ', poll["likes"])
print('Heads: ', poll["heads_votes"])
print('Tails: ', poll["tails_votes"])