import firebase_admin
from firebase_admin import credentials, messaging
import json, os
from flask import Flask, request
from functools import wraps

app = Flask(__name__)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/talha/Desktop/fbAdminConfig.json"
firebase = firebase_admin.initialize_app()


def send_android_notification(title, device_token):

    data={
            "device_name":"Apple 10",
            "user_agent":"Ubuntu",
            "timestamp":"1603802576",
            "username":"Talha",
            "request_id": "1",
            "ip_address":"111.119.187.22",
            "message":"Did you just sign-in?",
            "geo_location":"Pakistan",
            "user_id":"talha@broadstonetech.com",
        }

    android = messaging.AndroidConfig(priority='high',
        notification=messaging.AndroidNotification(
            )
        )

    apns = messaging.APNSConfig(
        headers={
        'apns-priority': '10'
        },
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                alert=messaging.ApsAlert(
                    title="Talha",
                    body="Talha Umer sending you an testing  notification",
                    ),
                content_available=1,
                mutable_content=1
                )
            )
        )


    message = messaging.Message(
        data=data,
        token=device_token,
        apns=apns,
        android = android,
     )

    response = messaging.send(message)
    if response:
        return {"message":True},200
    else:
        return {"message":"Msg not send"}, 400
##############################################################################
@app.route('/send_push_notification')
def send_push_notification_helper():
    device_token  = "ekwLuMG9RTKK940JKI0kSb:APA91bFPzxbMd9KobN4A4YUDLZyq41fs9g0jeHP38UBTA9bBzkmS3yi6tqBSCBzZBwYkMKJoWhkvQLNKnjeohe1wvYqhJI-DLqJ1vQ4kM6vZycbQ79X7gG_pE3aZRUzT5lgmjA7ypif9"
    # device_token = "cYF8ApPMqE2Ju4gjwsSlwj:APA91bH03w-vfBsYZryJGRdC3bocHcV7JE-_SyWC43mBG5wBje12Y6auOEgVnIRxDq9gYu7VEX8xMBCvggYAnuGzPsJAFQ2XWe1IhJJ4BDIvoQN3fGl5MusFnAzjsG8-Wb5p_AsD6n7R"
    return send_android_notification("title", device_token)
    
    

if __name__ == '__main__':
    app.run(debug=True)