import logging
import os
import json
import requests
from flask import Flask, abort, request
from flask.logging import create_logger
import iso8601
from prometheus_flask_exporter import PrometheusMetrics
import toml


from .j2_template_engine import load_j2_template_engine
from . import __version__

app = Flask(__name__)

# Logger Setup
LOGGER = create_logger(app)
LOGGER.setLevel(os.environ.get('LOGLEVEL', logging.INFO))

# Load configuration file.
CONFIG = toml.load(os.environ.get('CONFIG_FILE_LOCATION', 'config.toml'))
USE_CARDS = CONFIG['app']['notification'].get('use_cards')

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


def post_request(url: str, post_request_data):
    post_request_details = requests.post(
        url,
        json=post_request_data,
        verify=False)

    if post_request_details.ok:
        LOGGER.info('Alert message posted successfully.')
    else:
        LOGGER.error('Alert message failed to be posted.')
        LOGGER.error('%s - %s',
                        str(post_request_details.status_code), str(post_request_details.text)
                        )


@app.route('/alerts', methods=['POST'])
def post_alerts():
    """ Parses the given message and post it to the indicated channel. """

    # Get room name and validate.
    room_name = request.args.get('room', '')
    if room_name == '':
        LOGGER.error('Room <%s> not given as parameter.', room_name)
        abort(400)

    # Check if room is defined in configuration.
    if room_name not in CONFIG['app']['room']:
        LOGGER.error('Room <%s> not present in configuration file.', room_name)
        abort(404)

    notification_url = CONFIG['app']['room'][room_name]['notification_url']
    group_alerts = CONFIG['app']['room'][room_name].get('group_alerts', True)
    origin = CONFIG['app']['notification'].get('origin', os.environ.get('HOSTNAME', 'Unknown'))

    if USE_CARDS and not group_alerts:
        LOGGER.error(
            'Room <%s>: group_alerts enabled but use_cards disabled, incompatible settings.',
            room_name
        )
        abort(404)

    LOGGER.info('Processing alert(s) for GChat room <%s>.', room_name)

    # Render alerts
    rendered_alerts = []
    for alert in request.json['alerts']:
        render_payload = {
            'origin': origin
        }
        for field in ["startsAt", "endsAt", "updatedAt"]:
            try:
                alert[f'{field}DateTime'] = iso8601.parse_date(alert[field])
            except (KeyError, TypeError, ValueError):
                pass
        render_payload.update(alert)
        rendered_alert = J2_TEMPLATE_ENGINE.render(render_payload)
        if USE_CARDS:
            rendered_alert = json.loads(rendered_alert)
        rendered_alerts.append(rendered_alert)

    if USE_CARDS:
        post_request(notification_url, {'cards': rendered_alerts})
    elif group_alerts:
        post_request(notification_url, {'text': '\n'.join(rendered_alerts)})
    else:
        for rendered_alert in rendered_alerts:
            post_request(notification_url, {'text': rendered_alert})

    return ''
