import requests

def send_notification(recepient_email, subject, message):
    """ FastApi notification """

    url = 'http://notify:8000/notify' # url inside Docker
    try:
        response = requests.post(
            url,
            json={
                "recipient": recepient_email,
                "subject": subject,
                "message": message,
            },
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f'Error with sending notification: {e}')