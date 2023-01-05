import os
from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler

from skraggle.base_helpers.report_email_builder import prepare_email_message, prepare_email_html, prepare_email_body
from skraggle.run import mail
from skraggle.base_helpers.responser import DataResponse
from smart_open import open


def prepare_attachment(attachment_path, msg):
    with open(attachment_path, 'rb') as f:
        msg.attach("Attachment", 'application/pdf', f.read())


def report_sender(emails, expire_date, name, report_for, file_path=None):
    try:
        msg = prepare_email_message(emails)[report_for]
        msg.body = prepare_email_body()[report_for]
        print(msg)
        try:
            msg.html = prepare_email_html(name, expire_date)[report_for]
        except Exception as e:
            return str(e)
        if file_path:
            prepare_attachment(file_path, msg)

        print(msg)
        mail.send(msg)
        resp = DataResponse(True, "E-blasts Sent Successfully")
        return resp.status()
    except Exception as e:
        resp = DataResponse(False, str(e)[:150])
        return resp.status()


# This is not being used anywhere in the project but it's here for anything that comes in future around this.
def background_schedule():
    def tick():
        print("Tick! The time is: %s" % datetime.now())

    scheduler = BackgroundScheduler()
    scheduler.add_job(tick, "interval", seconds=3)
    scheduler.start()
    print("Press Ctrl+{0} to exit".format("Break" if os.name == "nt" else "C"))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
