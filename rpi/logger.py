import datetime
from datetime import datetime
import os

log_folder = "/home/pi/doorbotlog/"


class Logger:
    last_pushed:datetime
    verbose_level:int = 5#0-5. 5 being for debugging, 0 being for errors that always need to be logged
    def __init__(self, verbose:int=5):
        #this should probably throw an error if the logging is outside of the expected range. But IDC

        self.verbose_level = verbose


    # saves the message to log, if the verbose level is below the verboseLevel of the logger. Returns true if it is saved
    def log(self, message, when:datetime=datetime.now(), verbose = 0) -> bool:
        if verbose>self.verbose_level:
            #then this is above the level we should log.
            return False

        # get the log file for today. With a different folder for each year.
        log_file = self.get_log_file_str(when)
        f = open(log_file, "a")
        f.write(
            "[{h:02d}-{m:02d}-{s:02d}] L{verbose}:>{msg}\n".format(
                h=when.hour, m=when.minute, s=when.second, verbose=verbose, msg=message)
        )
        f.close

        return True

    # mk_log_dr should normally be true, unless you are testing, and don't want it to make the log directory
    def get_log_file_str(self, when:datetime= datetime.now(), mk_log_dr:bool = True)->str:
        lf = "{logFolder}{year}/log_{month}_{day}.txt".format(
            logFolder=log_folder, 
            year=when.year, 
            month=when.month, 
            day=when.day
        )
        if not os.path.exists(lf) and mk_log_dr:
            #if the log folder doesn't exist, we need to make it.
            ldr = "{logFolder}{year}".format(
                logFolder=log_folder, 
                year=when.year
            )
            os.makedirs(ldr, exist_ok=True)
        return lf
