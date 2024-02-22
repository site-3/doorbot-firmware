import datetime
from datetime import (datetime, timedelta)
import os
from git import Repo


log_folder = "/home/pi/doorbotlog"
logRepoURL = "https://github.com/site-3/doorbotlog"

class Logger:
    last_pushed:datetime
    verbose_level:int = 5#0-5. 5 being for debugging, 0 being for errors that always need to be logged
    def __init__(self, verbose:int=5, debugMode:bool=False, setupRepo:bool=True):
        #this should probably throw an error if the logging is outside of the expected range. But IDC
        self.verbose_level = verbose
        if not setupRepo:
            return
        self.repo = Repo(log_folder)#get the local repo files connected
        self.origin = self.repo.remote() #get our remote connection setup

        #check that the remote connection is up, and if it isn't, log that!
        if not self.origin.exists():
            self.log("origin could not be connected to!", verbose=0)
        self.origin.fetch()#this can give data apparently, but for now, we just update our stuff with it
        # Create local branch "master" from remote "master".
        # Set local "master" to track remote "master.
        # Check out local "master" to working tree.
        if debugMode:
            self.repo.create_head("testing", self.origin.refs.testing)
            trackedBranch = self.repo.heads.testing.tracking_branch()
            if trackedBranch == None or trackedBranch.name != "origin/testing":
                #this will cause bugs if we call it when it's already the tracking branch
                self.repo.heads.testing.set_tracking_branch(self.origin.refs.testing)
            self.repo.heads.testing.checkout()
        else:
            self.repo.create_head("master", self.origin.refs.master)
            trackedBranch = self.repo.heads.master.tracking_branch()
            if trackedBranch == None or trackedBranch.name != "origin/master":
                self.repo.heads.master.set_tracking_branch(self.origin.refs.master)
            self.repo.heads.master.checkout()
        self.origin.pull()#make sure our copies are up to date and will play nice


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
        lf = "{logFolder}/{year}/log_{month:02d}_{day:02d}.txt".format(
            logFolder=log_folder, 
            year=when.year, 
            month=when.month, 
            day=when.day
        )
        if not os.path.exists(lf) and mk_log_dr:
            #if the log folder doesn't exist, we need to make it.
            ldr = "{logFolder}/{year}".format(
                logFolder=log_folder, 
                year=when.year
            )
            os.makedirs(ldr, exist_ok=True)
        return lf
    
    def push_logs(self, now:datetime=datetime.now(), nDays:timedelta=timedelta(days=30), force:bool=False):
        # find the log files it'll need for the past nDays, and add those to a git commit. Then push.
        self.origin.pull()
        timeSinceLastCommit, last_commit_time = self._get_time_since_last_auto_commit(now)
        if timeSinceLastCommit<nDays and not force:
            #we've updated recently, and dont need to force it to update anyways
            return
        
        files = []
        # now we get the files in an array so they can be added to the commit
        for i in range(timeSinceLastCommit.days+2):#+2, one for today, and one for the last day logged.
            foo=self.get_log_file_str(when=now-timedelta(days=i), mk_log_dr=False)
            if os.path.exists(foo):
                files.append(foo)
        self.repo.index.add(files,True)
        newCommit = self.repo.index.commit(
            "logs for {}/{}-{}/{}".format(last_commit_time.month, last_commit_time.day, now.month, now.day)
        )
        self.log("created commit {}".format(newCommit.message),verbose=3)
        self.origin.push()#this gives info on how the push went, we might want to log that in the future.

    # gets the time since the last automatic commit. Checks that it is an automatic commit. returns the time since, and the last commit
    def _get_time_since_last_auto_commit(self, now:datetime, backCount:int =10):
        commits = list(self.repo.iter_commits(all=False, max_count=10))  #the latest commit to this branch
        for commit in commits:
            if commit.message.startswith("logs for "):
                if now.date()<commit.authored_datetime.date():
                    # dates can be weird. especially if you test by going back in time.
                    return timedelta(days=1), commit.authored_datetime
                return commit.authored_datetime.date() - now.date(), commit.authored_datetime

        return self._get_time_since_last_auto_commit(now, backCount=backCount*2)