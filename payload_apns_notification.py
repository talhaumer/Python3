import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials

#initialize firebase admin sdk
creds = credentials.Certificate('path/to/certificate.json')
firebase_admin.initialize_app(creds)


def send(token):
    message = messaging.Message(
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                title='title',
                body='body'
            ),
            data={
                'a': {'b': '1'}
            }
        ),
        token=token,
    )
    response = messaging.send(message)
    print(response)

your_token = 'registration_token'
send(your_token)


################################################################################


def send(token):
    message = messaging.Message(
        webpush=messaging.WebpushConfig(
            headers={
                'Urgency': 'high'
            },
            notification=messaging.WebpushNotification(
                title='title',
                body='body'
            ),
            data={
                'a': {'b': '1'}
            }
        ),
    token=token)
    response = messaging.send(message)
    print(response)

your_token = 'registration_token'
send(your_token)


########################################################################


def send(token):
    message = messaging.Message(
        apns=messaging.APNSConfig(
            headers={
                'apns-priority': '10',
            },
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title='title1',
                        subtitle='subtitle1',
                        body='body'
                    ),
                    content_available=1,
                    mutable_content=1
                ),
                data={
                    'a': {'b': '1'}
                }
            ),
        ),
        token=token
    )
    response = messaging.send(message)
    print(response)