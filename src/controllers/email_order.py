from flask import request
from flask.ext.restful import Resource
from flask_mail import Mail, Message

from recaptcha.client import captcha

from settings import app, api, environment, recaptcha_private_key


mail = Mail(app)


class EmailOrder(Resource):
    def post(self):
        recaptcha_challenge_field = request.form.get(
            'recaptcha_challenge_field')
        recaptcha_response_field = request.form.get('recaptcha_response_field')

        if not request.headers.getlist("X-Forwarded-For"):
            remote_address = request.remote_addr
        else:
            remote_address = request.headers.getlist("X-Forwarded-For")[0]

        response = captcha.submit(
            recaptcha_challenge_field,
            recaptcha_response_field,
            recaptcha_private_key,
            remote_address
        )

        if not response.is_valid:
            return {
                'error': 'recaptcha',
                'notification': 'Incorrect Captcha. Please try again.'
            }, 200

        return self.send_email()


    def send_email(self):
        name = request.form.get('name')
        email_address = request.form.get('email')
        message = request.form.get('message')
        recipients = ['teenypies@gmail.com']

        email = Message(
            'A message from teenypies.com',
            sender = 'teenypies@gmail.com',
            recipients = recipients
        )
        email.body = 'Name: %s\nEmail: %s\n\nMessage: %s' % (name,
            email_address, message)

        if environment == 'development':
            print email.body
        else:
            mail.send(email)

        return {
            'notification': 'Your message has been sent!'
        }, 201


api.add_resource(EmailOrder, '/email-order')
