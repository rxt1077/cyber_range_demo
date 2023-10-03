from bs4 import BeautifulSoup

from challenges.routes import AVAILABLE_CHALLENGES 

def test_challenges(admin_logged_in):
    """Tests each challenge in /list_challenges"""

    response = admin_logged_in.get('/list_challenges')
    assert response.status_code == 200
    list_challenges_soup = BeautifulSoup(response.text, 'html.parser')
    for index, li in enumerate(list_challenges_soup.find_all('li')):
        # try starting the challenge
        start_challenge_link = li.contents[0]['href']
        response = admin_logged_in.get(start_challenge_link, follow_redirects=True)
        assert response.status_code == 200

        # try stopping the challenge
        challenge_soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = challenge_soup.find(id='csrf_token')['value']
        flag = challenge_soup.find(id='flag')['value']
        stop = challenge_soup.find(id='stop')['value']
        response = admin_logged_in.post('/active_challenge', data={
            'csrf_token': csrf_token,
            'flag': flag,
            'stop': stop,
        })
        assert response.status_code == 302

        # try starting the challenge again
        response = admin_logged_in.get(start_challenge_link, follow_redirects=True)
        assert response.status_code == 200

        # try capturing the flag
        challenge_soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = challenge_soup.find(id='csrf_token')['value']
        capture = challenge_soup.find(id='capture')['value']
        response = admin_logged_in.post('/active_challenge', data={
            'csrf_token': csrf_token,
            'flag': AVAILABLE_CHALLENGES[index].FLAG,
            'capture': capture,
        })

        # see if we got the success page
        success_soup = BeautifulSoup(response.text, 'html.parser')
        assert(success_soup.find('h1').contents[0] == "Congratulations!")
