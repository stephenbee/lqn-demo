# A package
import logging
LOG_FILENAME = 'lqn_demo_log.out'
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
		    filename=LOG_FILENAME,
                    level=logging.DEBUG)


