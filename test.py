# import os

# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

# message = Mail(
#     from_email='paulsas007@gmail.com',
#     to_emails='paulkatok77@gmail.com',
#     subject='Sending with Twilio SendGrid is Fun',
#     html_content='<strong>and easy to do anywhere, even with Python</strong>')
# try:
#     print('api_key: ', os.environ.get('SENDGRID_API_KEY'))
#     sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
#     response = sg.send(message)
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)
# except Exception as e:
#     print(e)
# import schedule
# import time

# def job():
#     print("I'm working...")
# schedule.every(10).seconds.do(job)

# # schedule.every(10).minutes.do(job)
# # schedule.every().hour.do(job)
# # schedule.every().day.at("10:30").do(job)
# # schedule.every().monday.do(job)
# # schedule.every().wednesday.at("13:15").do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1) 
import json
values = {
            "merchantRefNum": "merchant 03.24.17_3",
            "amount": 1000,
            "settleWithAuth": False,
            "dupCheck": False,
            "card": {
            "cardNum": "4111111111111111",
            "cardExpiry": {
                "month": 9,
                "year": 2020
            },
            "cvv": "123"
            },
            "profile": {
            "firstName": "Joe",
            "lastName": "Smith",
            "email": "Joe.Smith@canada.com"
            },
            "billingDetails": {
            "street": "100 Queen Street West",
            "city": "Toronto",
            "state": "ON",
            "country": "CA",
            "zip": "M5H 2N2"
            },
            "customerIp": "204.91.0.12",
            "description": "Video purchase"
        }


print(type(json.dumps(values)))