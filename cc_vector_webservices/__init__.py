import sys
sys.path.append('/home/app/call_center_dr/trunk/cc_vector_manager/')

import logging
#create logger
logger = logging.getLogger('cc_vector_webservices')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)

logger.info("cc_vector_webservices started")