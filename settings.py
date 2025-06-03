




'''
The available time between draft picks in minutes and seconds.
This setting is used to control the pacing of the draft process.

TIME_BETWEEN_PICKS["minutes"] is the number of minutes to wait between each pick.
TIME_BETWEEN_PICKS["seconds"] is the number of seconds to wait between each pick.

The Default setting that will be used in production will be somewhere between 1 and 5 minutes,
for testing purposes we can set it to smaller time periods so drafts run quickly.
'''
TIME_BETWEEN_PICKS: dict = {
    "minutes": 0,
    "seconds": 50
}