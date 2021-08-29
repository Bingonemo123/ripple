import os
import pathlib
import datetime
import pickle
import shutil
import logging


class Archivarius ():
    def __init__(self):
        
        if os.name == 'posix':
            path = pathlib.PurePosixPath(os.path.abspath(__file__)).parent 
            if 'Forex_experiments' in path.parts:
                path = path.parent / str(datetime.date.today())
            else:
                path = path / 'Forex_experiments'  / str(datetime.date.today())
            # After this, path is equals to current date folder
            file_path = pathlib.PurePosixPath(os.path.abspath(__file__))
        else:
            path = pathlib.PureWindowsPath(os.path.abspath(__file__)).parent 
            if 'Forex_experiments' in path.parts:
                path = path.parent / str(datetime.date.today())
            else:
                path = path / 'Forex_experiments'  / str(datetime.date.today())
            # After this, path is equals to current date folder
            file_path = pathlib.PureWindowsPath(os.path.abspath(__file__))
            
        try:
            os.mkdir(str(path))
        except OSError as ose:
            pass

        try:
            experiment_number = pickle.load(open(str(path.parent / 'experiment_number.pkl'), 'rb+')) + 1
        except FileNotFoundError:
            experiment_number = 1
        pickle.dump(experiment_number, open(str(path.parent / 'experiment_number.pkl'), 'wb+'))

        shutil.copy(file_path, path / (file_path.stem + str(experiment_number) + file_path.suffix) )

        '''----------------------------------------------------------------------------------------------'''
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        """StreamHandler"""
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.DEBUG) 
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)
        """FileHandler"""
        self.rotatingfile_handler = logging.handlers.RotatingFileHandler(path.parent/'main.log', backupCount=5, maxBytes=1073741824)
        self.rotatingfile_handler.setLevel(logging.DEBUG)
        self.rotatingfile_handler.setFormatter(selfformatter)
        self.logger.addHandler(self.rotatingfile_handler)

        self.logger.info('Main Entry ' + str(experiment_number))