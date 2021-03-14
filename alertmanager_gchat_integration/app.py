import logging
import os
import requests
from flask import Flask, abort, request
from flask.logging import create_logger
import iso8601
from prometheus_flask_exporter import PrometheusMetrics
import toml

from .j2_template_engine import load_j2_template_engine
from . import __version__

app = Flask(__name__)

# Load configuration file.
CONFIG = toml.load(os.environ.get('CONFIG_FILE_LOCATION', 'config.toml'))

# Logger Setup
LOGGER = create_logger(app)
LOGGER.setLevel(os.environ.get('LOGLEVEL', logging.INFO))

# Metrics set-up
metrics = PrometheusMetrics(app)
metrics.info('up', 'Application health')
metrics.info('info', 'Application information', version=__version__)

# Template Setup.
if 'custom_template_path' in CONFIG['app']['notification']:
    J2_TEMPLATE_ENGINE = load_j2_template_engine(CONFIG['app']['notification']['custom_template_path'])
else:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    J2_TEMPLATE_ENGINE = load_j2_template_engine(dir_path + '/default-notification-template.json.j2')


@app.route('/healthz')
@metrics.do_not_track()
def healthz():
    """ Healthz endpoint """
    return ''


@app.route('/alerts', methods=['POST'])
def post_alerts():
    """ Parses the given message and post it to the indicated channel. """

    # Get room name and validate.
    room_name = request.args.get('room', '')
    if room_name == '':
        LOGGER.debug('Room <%s> not given as parameter.')
        abort(400)

    # Check if room is defined in configuration.
    if room_name not in CONFIG['app']['room']:
        LOGGER.debug('Room <%s> not present in configuration file.')
        abort(404)

    # Notification URL.
    notification_url = CONFIG['app']['room'][room_name]['notification_url']
    if 'origin' in CONFIG['app']['notification']:
        origin = CONFIG['app']['notification']['origin']
    else:
        origin = os.environ.get('HOSTNAME', 'Unknown')

    # Build a HTTP client request
    for alert in request.json['alerts']:
        # Render alert as text.
        render_payload = {
            'origin': origin
        }
        for field in ["startsAt", "endsAt", "updatedAt"]:
            try:
                alert[f'{field}DateTime'] = iso8601.parse_date(alert[field])
            except (KeyError, TypeError, ValueError):
                pass
        render_payload.update(alert)
        text_alert = J2_TEMPLATE_ENGINE.render(render_payload)

        # Post request.
        post_request_details = requests.post(
            notification_url,
            json={
                'text': text_alert
            },
            verify=False)

        if post_request_details.ok:
            LOGGER.info('Alert message posted successfully to GChat room <%s>.', room_name)
        else:
            LOGGER.error('Alert message failed to be posted to GChat room <%s>.', room_name)
            LOGGER.error('%s - %s',
                         str(post_request_details.status_code), str(post_request_details.text)
                         )

    return ''
