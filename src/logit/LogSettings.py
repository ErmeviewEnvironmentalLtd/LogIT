import logging.config

LOG_SETTINGS_CONSOLE_ONLY = {
    'version': 1,
    'root': {
        'level': 'NOTSET',
        'disable_existing_loggers': True,
        'handlers': ['console'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
    },
    'formatters': {
        'console': {
            'format': '%(asctime)s %(module)-30s line:%(lineno)-4d ' \
            '%(levelname)-8s %(message)s',
        },
    },
}
LOG_SETTINGS = {
    'version': 1,
    'root': {
        'level': 'NOTSET',
        'disable_existing_loggers': True,
        'handlers': ['console', 'file'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': 'logs/LogIT.log',
            'mode': 'a',
            'maxBytes': 51200, # 50 Kb
            'backupCount': 5,
        },
    },
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(name)-50s line:%(lineno)-4d ' \
            '%(levelname)-8s %(message)s',
        },
        'simple': {
            'format': '%(filename)-25s %(levelname)-8s %(message)s'
        }
    },
}
LOG_SETTINGS_DEBUG = {
    'version': 1,
    'root': {
        'level': 'NOTSET',
        'disable_existing_loggers': True,
        'handlers': ['console', 'file'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/LogIT.log',
            'mode': 'a',
            'maxBytes': 51200, # 50 Kb
            'backupCount': 5,
        },
    },
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(name)-50s line:%(lineno)-4d ' \
            '%(levelname)-8s %(message)s',
        },
        'simple': {
            'format': '%(module)-30s %(levelname)-8s %(message)s'
        }
    },
}

