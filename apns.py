from pyfcm import FCMNotification
push_service = FCMNotification(api_key="AAAAJTNYVvo:APA91bGMFBpgLfDzMqsji42jiudHeYP_xTvmO_-KGVMHJWp9lugsKIx2Eb5AM3peoguak_Y-EPbmqA86u13WvxiKqIBGkUtrbWjUgs7qBXjzPIu2s07IJ4-OIaPCWwLSupVd_t-acLVM")

# Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging
 
registration_id = "eOoXzmclKUEImb2nQLxlDj:APA91bEVJiCOh5vGYLRSD454AVE5bbk7eWRLjZp1uABHJ08wsxvcWB3Ws_eTldEcDS-CJSuWCWQvYplvDGup_BYrKoK6TF7rinKb1pksRfVwYFFExYONO6NK5uGro1mkoDqsQgUijwf-"
# payload = {"key":"Hi Mubashir, your customized news for today is ready"}
data_message = {
    "Nick" : "Mario",
    "body" : "great match!",
    "Room" : "PortugalVSDenmark"
}
message_title = "Hello"
# result = push_service.notify_single_device(low_priority=False,registration_id=registration_id, message_title=message_title, data_message=message_body)
result = push_service.single_device_data_message(registration_id=registration_id, low_priority=False,data_message=data_message)
print (result)