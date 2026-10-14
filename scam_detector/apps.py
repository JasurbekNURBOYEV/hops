import sys
from pathlib import Path

from django.apps import AppConfig


class ScamDetectorConfig(AppConfig):
    name = 'scam_detector'
    verbose_name = 'Scam Detector'

    def ready(self):
        # load the model at server startup, so the first scanned message doesn't pay for it.
        # other processes (migrate, collectstatic, ...) don't scan messages, so they skip it.
        # covers both `daphne ...` and `python -m daphne ...`
        if 'daphne' in Path(sys.argv[0]).parts:
            from scam_detector.classifier import load_model
            load_model()
